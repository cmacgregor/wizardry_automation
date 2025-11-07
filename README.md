# Wizardry Store Automation Bot

Automatically collect your weekly free gems from the Wizardry Variants Daphne store.

This bot logs into https://store.wizardry.info/ with your User ID and clicks the "Get Free" button in the Free Items section. Run it manually or set it up with Docker to collect your free gems automatically every week.

## Quick Start with Docker (Recommended)

**Automatically collect free gems every week with a secure, lightweight container:**

### Option 1: Use Pre-built Image (Easiest)

1. Create `.env` file with your User ID:
   ```bash
   cp .env.example .env
   # Edit .env: USER_ID=your-actual-user-id
   ```

2. Pull and run:
   ```bash
   docker pull ghcr.io/YOUR_USERNAME/wizardry_automation:latest
   docker-compose up -d
   ```

### Option 2: Build Locally

1. Create `.env` file (same as above)
2. Build and start:
   ```bash
   docker-compose up -d --build
   ```

**That's it!** Your User ID stays in the local `.env` file (never committed to git, never in the Docker image).

Done! The bot will now run automatically every Monday at 10:00 AM.

**View logs:**
```bash
docker-compose logs -f
```

**Stop the bot:**
```bash
docker-compose down
```

**Resources:**
- [DOCKER.md](DOCKER.md) - Detailed Docker instructions and scheduling
- [SECURITY.md](SECURITY.md) - Security features and best practices
- [.github/workflows/README.md](.github/workflows/README.md) - CI/CD documentation

---

## Manual Installation (Without Docker)

### Prerequisites

- Python 3.7 or higher
- Google Chrome browser

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your User ID (choose one):**

   **Option A: Environment variable (recommended)**
   ```bash
   export USER_ID=your-user-id  # Linux/Mac
   $env:USER_ID="your-user-id"  # Windows PowerShell
   ```

   **Option B: Config file**
   ```bash
   cp config.json.example config.json
   # Edit config.json and add your User ID
   ```

3. **Run the bot:**
   ```bash
   python wizardry_bot.py
   ```

## Configuration

### Docker Setup

Create `.env` file:
- **USER_ID**: Your Wizardry store User ID (required)
- **TZ**: Your timezone (optional)

### Manual Python Setup

**Required:** Set User ID via environment variable OR config.json

**Optional Customization** (create `config.json` from template):
- **headless**: `false` to watch browser, `true` for background (default: false)
- **wait_time**: Timeout in seconds for slow connections (default: 15)

## How It Works

1. Opens the Wizardry store website
2. Dismisses cookie consent popup
3. Logs in with your User ID (no password needed)
4. Scrolls to the Free Items section
5. Clicks the "Get Free" button

## Notes

- Free gems can only be collected once per week
- The website uses User ID authentication only (no password required)
- For debugging, set `headless: false` in config.json to watch the browser
