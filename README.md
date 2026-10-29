# Wizardry Store Automation

Automatically collect your weekly free gems from the [Wizardry Variants Daphne store](https://store.wizardry.info/).

`claim_free_items.py` talks to the store's Xsolla API directly: it logs in with your User ID, lists the store items and claims every free item that still has a claim left. No browser is needed, and it only uses the Python standard library.

Free items reset every Sunday at 10:00 AM US Eastern.

## Run with Docker

1. Create a `.env` file with your User ID:
   ```bash
   cp .env.example .env
   # Edit .env: USER_ID=your-user-id
   ```

2. Start the container, using the pre-built image or building it locally:
   ```bash
   docker compose pull && docker compose up -d   # pre-built image
   docker compose up -d --build                  # build locally
   ```

The container checks for free items every `CHECK_INTERVAL_HOURS` (6 by default) and skips items that are already claimed.

View logs with `docker compose logs -f` and stop it with `docker compose down`.

## Run without Docker

Requires Python 3.8 or newer.

```bash
# Linux/Mac
USER_ID=your-user-id DRY_RUN=true python claim_free_items.py   # list only
USER_ID=your-user-id python claim_free_items.py                # claim

# Windows PowerShell
$env:USER_ID="your-user-id"; python claim_free_items.py
```

## Settings

All settings are environment variables (or entries in `.env` for Docker):

| Variable | Default | Description |
|---|---|---|
| `USER_ID` | (required) | Your Wizardry store User ID |
| `COUNTRY` | `US` | Country code sent at login |
| `CHECK_INTERVAL_HOURS` | (empty) | Check again every N hours; empty runs once and exits |
| `DRY_RUN` | `false` | `true` lists what would be claimed without claiming |

## CI

- `.github/workflows/docker-build.yml` builds the image for amd64 and arm64 and pushes it to `ghcr.io` on pushes to `master` and version tags.
- `.github/workflows/security-scan.yml` scans the image with Trivy weekly and on every push.
