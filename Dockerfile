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
    # Install Chromium and ChromeDriver (always install, compatible on all architectures)
    chromium \
    chromium-driver \
    && ln -s /usr/bin/chromedriver /usr/local/bin/chromedriver || true \
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
# Create symlink to make chromium available as google-chrome-stable for Selenium compatibility
RUN ln -s /usr/bin/chromium /usr/bin/google-chrome-stable || true

# Remove chrome_crashpad_handler to prevent crash handler errors
# This binary requires --database parameter which causes Chrome to fail in containers
RUN rm -f /usr/lib/chromium/chrome_crashpad_handler || true

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
