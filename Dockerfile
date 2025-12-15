FROM python:3.11-slim

# Security: Create non-root user
RUN groupadd -r botuser && useradd -r -g botuser botuser

# Install Chrome and dependencies in a single layer to reduce image size
# Use TARGETARCH to support multi-platform builds
ARG TARGETARCH
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    # Chrome/Chromium runtime dependencies
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && if [ "$TARGETARCH" = "amd64" ]; then \
        # Install Chrome and ChromeDriver
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
        && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
        && apt-get update \
        && apt-get install -y --no-install-recommends google-chrome-stable chromium-driver \
        && ln -s /usr/bin/chromedriver /usr/local/bin/chromedriver || true; \
    elif [ "$TARGETARCH" = "arm64" ]; then \
        # Chromium on ARM64 includes chromium-driver
        apt-get install -y --no-install-recommends chromium chromium-driver \
        && ln -s /usr/bin/chromedriver /usr/local/bin/chromedriver || true; \
    fi \
    # Clean up to reduce image size
    && apt-get purge -y --auto-remove wget gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache

# Copy application files
COPY --chown=botuser:botuser wizardry_bot.py scheduler.py ./

# Security: Run Chrome with no-sandbox for container environment
# Create symlink for ARM64 to make chromium available as google-chrome for consistency
ARG TARGETARCH
RUN if [ "$TARGETARCH" = "arm64" ]; then \
        ln -s /usr/bin/chromium /usr/bin/google-chrome-stable || true; \
    fi

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SE_AVOID_STATS=true

# Security: Switch to non-root user
USER botuser

# Health check (optional but recommended)
HEALTHCHECK --interval=24h --timeout=30s --start-period=5m --retries=1 \
    CMD pgrep -f scheduler.py || exit 1

# Run the scheduler
CMD ["python", "-u", "scheduler.py"]
