# Quick Start - Run Pre-built Container

Get up and running in 2 minutes with the pre-built Docker image.

## Prerequisites

- Docker and Docker Compose installed
- Your Wizardry Store User ID

## Steps

### 1. Create `.env` file

```bash
# Copy the example
cp .env.example .env

# Edit .env and replace YOUR_USER_ID_HERE with your actual User ID
# You can use any text editor:
nano .env    # or vim, code, notepad, etc.
```

Your `.env` file should look like:
```env
USER_ID=your-actual-user-id-here
TZ=America/New_York
RUN_ON_STARTUP=false
```

**Optional**: Set `RUN_ON_STARTUP=true` to run the bot immediately when the container starts (useful for testing)

### 2. Pull and Run

```bash
# Pull and start the container
docker-compose -f docker-compose.prebuilt.yml up -d
```

That's it! The bot will now run automatically every Monday at 10:00 AM.

## Verify It's Running

```bash
# Check the container status
docker ps

# View the logs
docker-compose -f docker-compose.prebuilt.yml logs -f
```

## Common Commands

```bash
# Stop the bot
docker-compose -f docker-compose.prebuilt.yml down

# Restart the bot
docker-compose -f docker-compose.prebuilt.yml restart

# Update to latest version
docker-compose -f docker-compose.prebuilt.yml pull
docker-compose -f docker-compose.prebuilt.yml up -d
```

## Architecture Support

The pre-built image supports:
- **linux/amd64** - Intel/AMD x86_64 processors
- **linux/arm64** - ARM processors (Raspberry Pi, Apple Silicon, etc.)

Docker will automatically pull the correct image for your system.

## Troubleshooting

### Container keeps restarting
Check the logs: `docker-compose -f docker-compose.prebuilt.yml logs`

Common issues:
- Missing or invalid `USER_ID` in `.env` file
- `.env` file not in the same directory as `docker-compose.prebuilt.yml`

### Need to change timezone
Edit `.env` and change `TZ` to your timezone (e.g., `TZ=Europe/London`)

### Want to test immediately
Edit `.env` and set `RUN_ON_STARTUP=true`, then restart: `docker-compose -f docker-compose.prebuilt.yml restart`

### Want to customize schedule or settings
See [README.md](README.md) for full configuration options.

## Next Steps

- Read [DOCKER.md](DOCKER.md) for detailed Docker documentation
- Check [SECURITY.md](SECURITY.md) for security features
- See [README.md](README.md) for manual installation options
