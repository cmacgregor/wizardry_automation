FROM python:3.11-slim

# Security: Create non-root user
RUN groupadd -r botuser && useradd -r -g botuser botuser

# Install Chrome and dependencies in a single layer to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget=1.21.* \
    gnupg=2.2.* \
    ca-certificates \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    # Clean up to reduce image size
    && apt-get purge -y --auto-remove wget gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with pinned versions
RUN pip install --no-cache-dir --upgrade pip==24.* \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache

# Copy application files
COPY --chown=botuser:botuser wizardry_bot.py scheduler.py ./

# Security: Run Chrome with no-sandbox for container environment
ENV CHROME_BIN=/usr/bin/google-chrome-stable \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Security: Switch to non-root user
USER botuser

# Health check (optional but recommended)
HEALTHCHECK --interval=24h --timeout=30s --start-period=5m --retries=1 \
    CMD pgrep -f scheduler.py || exit 1

# Run the scheduler
CMD ["python", "-u", "scheduler.py"]
