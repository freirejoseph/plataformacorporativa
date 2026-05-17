# Sync and Publish

This folder contains the automation used to keep the project aligned between:
- local Windows workspace
- Ubuntu mirror
- GitHub repository

## Scripts
- `sync_and_publish.py`
- `sync_and_publish.ps1`

## Usage
One-time sync:
```powershell
python .\infra\scripts\sync_and_publish.py
```

Watch mode:
```powershell
python .\infra\scripts\sync_and_publish.py --watch --interval 60
```

Sync and publish to GitHub:
```powershell
python .\infra\scripts\sync_and_publish.py --push
```

Watch mode plus GitHub publish:
```powershell
python .\infra\scripts\sync_and_publish.py --watch --interval 60 --push
```

PowerShell wrapper:
```powershell
.\infra\scripts\sync_and_publish.ps1 -Watch -Interval 60 -Push
```

## Remote roots
Primary root:
- `/home/plataformacorporativa`

Fallback root:
- `/home/joseph/plataformacorporativa`

The script tries the primary root first and falls back only if needed.

