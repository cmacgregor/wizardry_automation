# GitHub Actions Workflows

## docker-build.yml

Builds and pushes Docker images to GitHub Container Registry.

### Triggers
- **Push to main**: Builds and tags as `latest`
- **Version tags** (v*.*.* format): Builds and tags with version numbers
- **Pull requests**: Builds but doesn't push (test only)
- **Manual**: Can be triggered manually from Actions tab

### Image Tags
- `latest` - Latest version from main branch
- `v1.0.0` - Specific version tag
- `v1.0` - Major.minor version
- `v1` - Major version only
- `main-abc1234` - Branch name + commit SHA

### Features
- Multi-platform builds (amd64, arm64)
- Docker layer caching for faster builds
- Build provenance attestation for security
- Automatic metadata extraction

### Using the Pre-built Image

After pushing to GitHub, pull and use the image:

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/YOUR_USERNAME/wizardry_automation:latest

# Use with docker-compose
# Update docker-compose.yml to use pre-built image instead of building
```

## security-scan.yml

Runs security vulnerability scanning on the Docker image.

### Triggers
- **Push to main**: Scans on every push
- **Pull requests**: Scans before merge
- **Weekly**: Automated scan every Sunday at midnight
- **Manual**: Can be triggered manually

### Features
- Trivy vulnerability scanner
- Scans for CRITICAL, HIGH, and MEDIUM vulnerabilities
- Uploads results to GitHub Security tab
- Human-readable output in Actions logs

### Viewing Results
1. Go to repository **Security** tab
2. Click **Code scanning**
3. View Trivy scan results

## Setup Requirements

### GitHub Container Registry (Automatic)
No setup needed! Uses `GITHUB_TOKEN` automatically.

### Docker Hub (Optional)
To also push to Docker Hub, uncomment the Docker Hub login step and add secrets:

1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Add secrets:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: Your Docker Hub access token

## Creating Releases

To create a new version:

```bash
# Tag the release
git tag v1.0.0
git push origin v1.0.0
```

This will:
1. Trigger the build workflow
2. Build image with version tags (v1.0.0, v1.0, v1, latest)
3. Push to GitHub Container Registry
4. Create build attestation

## Monitoring

Check workflow status:
- Go to **Actions** tab in GitHub
- View build logs and results
- Download build artifacts if needed
