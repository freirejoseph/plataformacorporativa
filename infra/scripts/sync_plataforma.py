from __future__ import annotations

import argparse
import hashlib
import os
import stat
import time
from pathlib import Path
from typing import Iterable

import paramiko
from dotenv import dotenv_values


ROOT_LOCAL = Path(__file__).resolve().parents[2]
DEFAULT_REMOTE_ROOT = "/home/plataformacorporativa"
EXCLUDE_DIRS = {".venv", "__pycache__", ".git", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
EXCLUDE_FILES = {".gitkeep"}


def load_env() -> dict[str, str]:
    values = dotenv_values(ROOT_LOCAL / ".env")
    return {k: v for k, v in values.items() if isinstance(v, str) and v}


def is_excluded(path_parts: Iterable[str]) -> bool:
    return any(part in EXCLUDE_DIRS for part in path_parts)


def file_hash(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def remote_hash(sftp: paramiko.SFTPClient, path: str) -> str:
    hasher = hashlib.sha256()
    with sftp.file(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def ensure_local_parent(rel_path: str) -> None:
    (ROOT_LOCAL / rel_path).parent.mkdir(parents=True, exist_ok=True)


def ensure_remote_parent(sftp: paramiko.SFTPClient, remote_root: str, rel_path: str) -> None:
    target = Path(rel_path).parent
    current = remote_root.rstrip("/")
    for part in target.parts:
        current = f"{current}/{part}"
        try:
            sftp.stat(current)
        except IOError:
            try:
                sftp.mkdir(current)
            except IOError:
                pass


def collect_local_files() -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in ROOT_LOCAL.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(ROOT_LOCAL)
        if is_excluded(rel.parts) or path.name in EXCLUDE_FILES:
            continue
        files[str(rel).replace("\\", "/")] = path
    return files


def collect_remote_files(sftp: paramiko.SFTPClient, remote_root: str) -> dict[str, str]:
    files: dict[str, str] = {}

    def walk(directory: str) -> None:
        try:
            entries = sftp.listdir_attr(directory)
        except IOError:
            return
        for entry in entries:
            if entry.filename in (".", "..") or entry.filename in EXCLUDE_FILES:
                continue
            remote_path = f"{directory.rstrip('/')}/{entry.filename}"
            rel = remote_path.removeprefix(remote_root.rstrip("/") + "/")
            if is_excluded(Path(rel).parts):
                continue
            if stat.S_ISDIR(entry.st_mode):
                walk(remote_path)
            else:
                files[rel] = remote_path

    walk(remote_root)
    return files


def connect_remote(env: dict[str, str]) -> tuple[paramiko.SSHClient, paramiko.SFTPClient]:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=env["SSH_HOST"],
        port=int(env.get("SSH_PORT", "22")),
        username=env["SSH_USER"],
        password=env["SSH_PASSWORD"],
        timeout=20,
        banner_timeout=20,
        auth_timeout=20,
    )
    return client, client.open_sftp()


def sync_file_to_remote(sftp: paramiko.SFTPClient, remote_root: str, rel: str, local_path: Path) -> None:
    ensure_remote_parent(sftp, remote_root, rel)
    with sftp.file(f"{remote_root.rstrip('/')}/{rel}", "wb") as handle:
        handle.write(local_path.read_bytes())
    mtime = int(local_path.stat().st_mtime)
    os.utime(local_path, (mtime, mtime))


def sync_file_to_local(sftp: paramiko.SFTPClient, remote_root: str, rel: str, remote_path: str) -> None:
    ensure_local_parent(rel)
    local_path = ROOT_LOCAL / rel
    with sftp.file(remote_path, "rb") as source:
        local_path.write_bytes(source.read())
    mtime = int(sftp.stat(remote_path).st_mtime)
    os.utime(local_path, (mtime, mtime))


def run_sync_once(remote_root: str, direction: str, dry_run: bool) -> list[tuple[str, str]]:
    env = load_env()
    if not env.get("SSH_HOST") or not env.get("SSH_USER") or not env.get("SSH_PASSWORD"):
        raise SystemExit("Missing SSH credentials in local .env")

    client, sftp = connect_remote(env)
    try:
        local_files = collect_local_files()
        remote_files = collect_remote_files(sftp, remote_root)
        all_keys = sorted(set(local_files) | set(remote_files))

        actions: list[tuple[str, str]] = []
        for rel in all_keys:
            local_path = local_files.get(rel)
            remote_path = remote_files.get(rel)

            if local_path and not remote_path and direction in ("both", "push"):
                actions.append(("push", rel))
                if not dry_run:
                    sync_file_to_remote(sftp, remote_root, rel, local_path)
            elif remote_path and not local_path and direction in ("both", "pull"):
                actions.append(("pull", rel))
                if not dry_run:
                    sync_file_to_local(sftp, remote_root, rel, remote_path)
            elif local_path and remote_path:
                local_sig = file_hash(local_path)
                remote_sig = remote_hash(sftp, remote_path)
                if local_sig != remote_sig and direction == "both":
                    local_mtime = local_path.stat().st_mtime
                    remote_mtime = sftp.stat(remote_path).st_mtime
                    if local_mtime >= remote_mtime:
                        actions.append(("push", rel))
                        if not dry_run:
                            sync_file_to_remote(sftp, remote_root, rel, local_path)
                    else:
                        actions.append(("pull", rel))
                        if not dry_run:
                            sync_file_to_local(sftp, remote_root, rel, remote_path)

        return actions
    finally:
        sftp.close()
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Plataforma Corporativa between local and Ubuntu.")
    parser.add_argument(
        "--direction",
        choices=("both", "push", "pull"),
        default="both",
        help="Sync direction. both compares and syncs in the newer direction.",
    )
    parser.add_argument("--remote-root", default=DEFAULT_REMOTE_ROOT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--watch", action="store_true", help="Keep syncing in a loop.")
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Seconds between sync cycles when --watch is enabled.",
    )
    args = parser.parse_args()

    interval = max(5, args.interval)

    if args.watch:
        print(f"watch=on interval={interval}s direction={args.direction} dry_run={args.dry_run}")
        try:
            while True:
                started_at = time.strftime("%Y-%m-%d %H:%M:%S")
                try:
                    actions = run_sync_once(args.remote_root, args.direction, args.dry_run)
                    print(f"[{started_at}] changed={len(actions)}")
                    for direction, rel in actions:
                        print(f"{direction} {rel}")
                except SystemExit as exc:
                    raise
                except Exception as exc:  # pragma: no cover - runtime guard
                    print(f"[{started_at}] error={exc}")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("watch=stopped")
        return 0

    actions = run_sync_once(args.remote_root, args.direction, args.dry_run)
    print(f"changed={len(actions)}")
    for direction, rel in actions:
        print(f"{direction} {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
