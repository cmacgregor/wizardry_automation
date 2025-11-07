# Security Features

This Docker image has been optimized for security and minimal footprint.

## Security Measures

### Image Security

1. **Non-root User**
   - Container runs as `botuser` (non-root)
   - Prevents privilege escalation attacks
   - Files owned by non-root user

2. **Minimal Base Image**
   - Uses `python:3.11-slim` (minimal Debian)
   - Only essential packages installed
   - Reduces attack surface

3. **Package Version Pinning**
   - Specific versions for wget, gnupg, pip
   - Prevents unexpected updates
   - Reproducible builds

4. **Layer Optimization**
   - Single RUN command for dependencies
   - Removes build tools after use
   - Cleans up caches and temp files

### Runtime Security

1. **Read-only Root Filesystem**
   - Container filesystem is immutable
   - Only /tmp and /dev/shm are writable
   - Prevents malicious file modifications

2. **Dropped Capabilities**
   - All Linux capabilities dropped
   - Minimal permissions granted
   - Principle of least privilege

3. **No New Privileges**
   - Prevents privilege escalation
   - Seccomp security profile

4. **Resource Limits**
   - CPU limited to 1 core max
   - Memory capped at 1GB
   - Prevents resource exhaustion

### Configuration Security

1. **Environment Variable Security**
   - User ID stored in `.env` file (gitignored)
   - Passed as environment variable to Docker
   - Never committed to version control
   - Follows Docker secrets best practices

2. **Read-only Config Mount**
   - config.json mounted as read-only
   - Contains only non-sensitive settings
   - Prevents accidental modification

3. **No Sensitive Data in Image**
   - Credentials excluded from Docker image
   - User ID not baked into image
   - Loaded from environment at runtime only

3. **Isolated Network**
   - No exposed ports
   - Outbound connections only
   - Cannot be accessed from outside

## Best Practices

### Before Deployment

1. **Review config.json**
   - Ensure User ID is correct
   - Set `headless: true` for production
   - Keep config.json out of version control

2. **Update Regularly**
   - Rebuild image monthly for security patches
   - Update Chrome to latest stable
   - Update Python dependencies

3. **Monitor Logs**
   ```bash
   docker-compose logs -f
   ```

### Secure Deployment

1. **Use Docker Secrets (Optional)**
   ```yaml
   secrets:
     - user_id
   ```

2. **Enable Docker Content Trust**
   ```bash
   export DOCKER_CONTENT_TRUST=1
   ```

3. **Scan for Vulnerabilities**
   ```bash
   docker scan wizardry-automation
   ```

## Image Size

Optimizations reduce the final image size:
- Removed unnecessary packages after installation
- No build tools in final image
- Python bytecode generation disabled
- All caches cleaned

Expected size: ~500-600MB (Chrome is ~400MB of this)

## Threat Model

**Protected Against:**
- ✅ Privilege escalation
- ✅ Container escape attempts
- ✅ Resource exhaustion (DoS)
- ✅ Filesystem tampering
- ✅ Configuration modification

**Out of Scope:**
- Network-level attacks (use firewall)
- Host system vulnerabilities
- User credential compromise
- Website changes/attacks

## Reporting Security Issues

If you discover a security vulnerability, please:
1. Do not open a public issue
2. Contact the maintainer privately
3. Provide detailed reproduction steps
