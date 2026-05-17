from __future__ import annotations

import argparse
import hashlib
import os
import posixpath
import subprocess
import sys
import time
from pathlib import Path

import paramiko


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REMOTE_ROOT = "/home/plataformacorporativa"
FALLBACK_REMOTE_ROOT = "/home/joseph/plataformacorporativa"
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode-test",
}
EXCLUDE_FILES = {".pyc", ".pyo"}
EXCLUDE_NAMES = {".gitkeep"}


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def parse_creds(env: dict[str, str]) -> tuple[str, str, str, int]:
    host = env.get("SSH_HOST", "")
    user = env.get("SSH_USER", "")
    password = env.get("SSH_PASSWORD", "")
    port = int(env.get("SSH_PORT", "22") or "22")
    if not host or not user or not password:
        raise RuntimeError("Missing SSH credentials in .env")
    return host, user, password, port


def should_skip(path: Path) -> bool:
    if path.name in EXCLUDE_NAMES:
        return True
    if path.is_dir() and path.name in EXCLUDE_DIRS:
        return True
    if path.is_file() and path.suffix in EXCLUDE_FILES:
        return True
    return False


def ensure_remote_dir(sftp: paramiko.SFTPClient, remote_dir: str) -> None:
    if remote_dir in {"", "/", "."}:
        return
    parts: list[str] = []
    current = remote_dir
    while current not in {"", "/", "."}:
        parts.append(current)
        current = posixpath.dirname(current)
    for directory in reversed(parts):
        try:
            sftp.stat(directory)
        except IOError:
            try:
                sftp.mkdir(directory)
            except IOError:
                pass


def hash_local(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_remote(sftp: paramiko.SFTPClient, remote_path: str) -> str | None:
    try:
        with sftp.open(remote_path, "rb") as handle:
            digest = hashlib.sha256()
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()
    except IOError:
        return None


def iter_local_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if should_skip(path):
            continue
        if path.is_file():
            files.append(path)
    return files


def connect_sftp(host: str, user: str, password: str, port: int) -> tuple[paramiko.Transport, paramiko.SFTPClient]:
    transport = paramiko.Transport((host, port))
    transport.connect(username=user, password=password)
    return transport, paramiko.SFTPClient.from_transport(transport)


def sync_tree(local_root: Path, remote_root: str, sftp: paramiko.SFTPClient) -> tuple[int, list[str]]:
    ensure_remote_dir(sftp, remote_root)
    synced = 0
    errors: list[str] = []
    for local_path in iter_local_files(local_root):
        rel = local_path.relative_to(local_root).as_posix()
        remote_path = posixpath.join(remote_root, rel)
        ensure_remote_dir(sftp, posixpath.dirname(remote_path))
        local_digest = hash_local(local_path)
        remote_digest = hash_remote(sftp, remote_path)
        if local_digest != remote_digest:
            try:
                sftp.put(str(local_path), remote_path)
                synced += 1
            except Exception as exc:  # pragma: no cover - remote runtime only
                errors.append(f"{rel}: {exc}")
    return synced, errors


def git_publish(message: str) -> tuple[int, int]:
    status = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    if not status.stdout.strip():
        return 0, 0
    subprocess.run(["git", "add", "-A"], cwd=REPO_ROOT, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=REPO_ROOT, check=True)
    push = subprocess.run(["git", "push", "-u", "origin", "main"], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    if push.returncode != 0:
        raise RuntimeError(push.stderr.strip() or push.stdout.strip() or "git push failed")
    return 1, 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync plataformacorporativa to Ubuntu and publish to GitHub.")
    parser.add_argument("--watch", action="store_true", help="Keep syncing at a fixed interval.")
    parser.add_argument("--interval", type=int, default=60, help="Seconds between watch iterations.")
    parser.add_argument("--push", action="store_true", help="Commit and push Git changes after sync.")
    parser.add_argument("--message", default="Auto sync plataformacorporativa", help="Git commit message.")
    parser.add_argument("--remote-root", default=DEFAULT_REMOTE_ROOT, help="Primary Ubuntu sync root.")
    parser.add_argument("--fallback-root", default=FALLBACK_REMOTE_ROOT, help="Fallback Ubuntu sync root.")
    args = parser.parse_args()

    env = load_env(REPO_ROOT / ".env")
    host, user, password, port = parse_creds(env)

    def run_once() -> None:
        transport, sftp = connect_sftp(host, user, password, port)
        try:
            roots = [args.remote_root]
            if args.fallback_root and args.fallback_root != args.remote_root:
                roots.append(args.fallback_root)

            last_error: Exception | None = None
            for remote_root in roots:
                try:
                    synced, errors = sync_tree(REPO_ROOT, remote_root, sftp)
                    print(f"REMOTE_ROOT={remote_root}")
                    print(f"SYNCED={synced}")
                    if errors:
                        print("ERRORS:")
                        for error in errors:
                            print(f"- {error}")
                    if args.push:
                        commits, pushes = git_publish(args.message)
                        print(f"GIT_COMMIT={commits}")
                        print(f"GIT_PUSH={pushes}")
                    return
                except Exception as exc:  # pragma: no cover - remote runtime only
                    last_error = exc
                    continue
            raise RuntimeError(f"Sync failed for all roots: {last_error}")
        finally:
            sftp.close()
            transport.close()

    if args.watch:
        while True:
            run_once()
            time.sleep(max(5, args.interval))
    else:
        run_once()
    return 0


if __name__ == "__main__":
    sys.exit(main())

