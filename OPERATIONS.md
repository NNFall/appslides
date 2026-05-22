# Operations

## Canonical Workflow

After every large or important change:

1. Run local checks that match the changed area.
2. Commit the project state to Git.
3. Push the current branch to GitHub.
4. If backend files changed, redeploy the server and restart the container.
5. Update the project docs and plan if the runtime flow, deployment flow, or product behavior changed.

## GitHub Repository

- Repository: `https://github.com/NNFall/appslides`
- Local root: repository root

## Backend Runtime

- Server IP: `185.171.83.116`
- SSH user: `root`
- Remote app dir: `/root/appslides`
- Public backend endpoint: `http://185.171.83.116:8011`
- Docker service: `appslides_backend`

## Standard Git Flow

```powershell
git status -sb
git add .
git commit -m "short meaningful message"
git push -u origin main
```

If work is already on an existing branch:

```powershell
git status -sb
git add .
git commit -m "short meaningful message"
git push
```

## Standard Backend Deploy

```powershell
python scripts\deploy\deploy_backend_remote.py `
  --host 185.171.83.116 `
  --user root `
  --password <SERVER_PASSWORD> `
  --port 22 `
  --remote-dir /root/appslides
```

The deploy script:

- uploads `backend/`, `telegram_admin_bot/`, `templates/`, `docker-compose.yml` and `.env`
- keeps persistent data outside the container
- rebuilds and restarts Docker Compose
- expects the public port to remain `8011`

## Runtime Temp Cleanup

The backend creates temporary files for uploads, conversions and presentation rendering under `TEMP_DIR`.

Production mapping:

- container path: `/app/runtime/temp`
- host path: `/root/appslides/temp`
- cleanup buckets: `uploads/`, `conversions/`, `presentations/`

Cleanup is performed by the backend itself, not by the old Telegram bot. The loop starts with `appslides_backend` and deletes expired entries according to:

- `TEMP_TTL_SECONDS`: how long temp files live
- `TEMP_CLEAN_INTERVAL`: how often the cleanup loop runs

Current production deploy passes these values from local env when available. The legacy bot env currently provides `TEMP_TTL_SECONDS=3600` and `TEMP_CLEAN_INTERVAL=600`, so production temp artifacts are removed after about 1 hour.

When cleanup removes temp folders/files, it also deletes matching rows from the backend `artifacts` table. It only touches `TEMP_DIR/uploads`, `TEMP_DIR/conversions` and `TEMP_DIR/presentations`; it must not touch templates, fonts, the database, Docker data or logs.

Useful read-only checks:

```bash
du -xh --max-depth=2 /root/appslides/temp 2>/dev/null | sort -h | tail -50
docker compose logs --tail=200 appslides_backend
```

Expected successful log line:

```text
Temp cleanup removed dirs=<n> files=<n> artifact_rows=<n>
```

## Server Disk Diagnostics

`/var` is the standard Linux directory for variable runtime data: service logs, systemd journal, package cache, Docker/containerd image layers, container writable data and other service state.

Current server disk pressure is mainly from:

- `/var/lib/containerd`: Docker/containerd image layers and build-related content
- `/var/log/journal`: systemd journal logs
- `/root/appslides/temp`: application temp files, now covered by backend cleanup

Do not delete these blindly. Safe candidates after confirmation:

- Docker build cache: `docker builder prune`
- old unused Docker resources: inspect with `docker system df` first
- systemd journal retention: `journalctl --vacuum-size=1G`

Docker cache pruning should not stop running containers, but future builds can be slower because layers need to be downloaded or rebuilt again.

## Local Validation Before Push

### Backend

```powershell
python -m unittest discover -s backend/tests -v
python -m compileall backend/src
```

### Admin Telegram Bot

```powershell
python -m compileall telegram_admin_bot
python -c "import telegram_admin_bot.main; print('admin bot import ok')"
```

### Flutter App

```powershell
& 'C:\Users\User\develop\flutter\bin\flutter.bat' pub get
& 'C:\Users\User\develop\flutter\bin\flutter.bat' analyze
& 'C:\Users\User\develop\flutter\bin\flutter.bat' test
& 'C:\Users\User\develop\flutter\bin\flutter.bat' build web
& 'C:\Users\User\develop\flutter\bin\flutter.bat' build apk
```

## Notes

- The mobile/web client is hard-wired to `http://185.171.83.116:8011`.
- Local backend URL switching inside the app is intentionally disabled.
- YooKassa is currently integrated in backend live mode and driven through the chat `/balance` flow.
- Successful payment should now be reflected both on app resume and on later summary/generation checks because the backend auto-syncs unfinished payments.
- The separate `telegram_admin_bot/` works against the same SQLite database as the backend and uses `client_id` for subscription commands.
- The production compose stack now includes both `appslides_backend` and `appslides_admin_bot`.
