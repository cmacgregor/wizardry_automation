# Docker Deployment Guide

Run the Wizardry automation bot in Docker with automatic weekly scheduling.

## Quick Start

1. **Create `.env` file with your credentials:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env`:
   ```env
   USER_ID=your-wizardry-user-id
   TZ=America/New_York
   ```

2. **Start the container:**
   ```bash
   docker-compose up -d
   ```

That's it! No config.json needed for Docker. The bot will run every Monday at 10:00 AM.

## Why .env File?

**Security Best Practice:**
- ✅ Credentials stay in local `.env` file (gitignored)
- ✅ Passed to container at runtime only
- ✅ Never stored in Docker image
- ✅ Image can be shared publicly without exposing secrets
- ✅ Each user has their own `.env` with their own credentials

**What NOT to do:**
- ❌ Don't put secrets in Dockerfile with ARG/ENV
- ❌ Don't commit `.env` to git
- ❌ Don't bake credentials into the image

## Configuration

### Required (.env file)
- `USER_ID` - Your Wizardry store User ID

### Optional (.env file)
- `TZ` - Timezone (default: America/New_York)

### Advanced (config.json - optional)
If you want to customize button selectors or other settings, create config.json:
```bash
cp config.json.example config.json
# Edit as needed
```

Docker will use defaults if config.json is not present.

## Schedule Configuration

Default: **Every Monday at 10:00 AM**

To change, edit `scheduler.py`:

```python
# Current schedule
schedule.every().monday.at("10:00").do(run_bot)

# Other examples:
schedule.every().sunday.at("09:00").do(run_bot)        # Sunday 9 AM
schedule.every().day.at("14:30").do(run_bot)           # Daily at 2:30 PM
schedule.every(3).days.at("10:00").do(run_bot)         # Every 3 days
```

After editing, rebuild:
```bash
docker-compose up -d --build
```

## Common Commands

```bash
# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild and restart
docker-compose up -d --build

# One-time manual run
docker-compose exec wizardry-bot python wizardry_bot.py
```

## Timezone Configuration

Common timezones (edit `.env`):
- `America/New_York` (EST/EDT)
- `America/Los_Angeles` (PST/PDT)
- `America/Chicago` (CST/CDT)
- `Europe/London` (GMT/BST)
- `Asia/Tokyo` (JST)

[Full list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

## Using Pre-built Images

Instead of building locally, use images from GitHub Container Registry:

1. Edit `docker-compose.yml`:
   ```yaml
   services:
     wizardry-bot:
       image: ghcr.io/YOUR_USERNAME/wizardry_automation:latest
       # Remove the build: section
   ```

2. Pull and run:
   ```bash
   docker pull ghcr.io/YOUR_USERNAME/wizardry_automation:latest
   docker-compose up -d
   ```

## Troubleshooting

**Container won't start:**
```bash
docker-compose logs
```

**Check environment variables:**
```bash
docker-compose exec wizardry-bot env | grep USER_ID
```

**Verify schedule:**
```bash
docker-compose logs | grep "Next run scheduled"
```

**Test without schedule:**
```bash
docker-compose exec wizardry-bot python wizardry_bot.py
```

## Security Features

- Non-root user inside container
- Read-only root filesystem
- No capabilities
- Resource limits (CPU/memory)
- Secrets via environment variables only

See [SECURITY.md](SECURITY.md) for details.
