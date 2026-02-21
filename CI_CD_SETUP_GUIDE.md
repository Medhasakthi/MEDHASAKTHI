# 🚀 MEDHASAKTHI Production CI/CD Setup Guide

## Overview

This guide explains how to set up automatic production deployment for MEDHASAKTHI using GitHub Actions with your existing secrets and production environment.

## Current CI/CD Status

✅ **Production Pipeline**: `ci-cd.yml` - Full production deployment with Docker registry
✅ **Simple Pipeline**: `simple-ci.yml` - Basic testing and build verification

## Production CI/CD Pipeline Features

The main `ci-cd.yml` workflow provides:
1. **Comprehensive Testing** - Backend and frontend validation
2. **Docker Image Building** - Builds and pushes to GitHub Container Registry
3. **Production Deployment** - Deploys to your production server via SSH
4. **Health Checks** - Verifies deployment success
5. **Database Migrations** - Runs Alembic migrations automatically
6. **Rollback Support** - Maintains previous images for quick rollback

### What Happens on Push to Main:
1. **Testing Phase** - Validates all code and builds
2. **Build & Push Phase** - Creates Docker images and pushes to registry
3. **Deployment Phase** - Deploys to production server
4. **Verification Phase** - Health checks and migration execution
5. **Notification Phase** - Success/failure notifications

## Required GitHub Secrets

You need to add these secrets to your GitHub repository for production deployment:

### 🔐 Production Server Secrets:
```
PRODUCTION_HOST=your-production-server-ip-or-domain
PRODUCTION_USER=your-ssh-username
PRODUCTION_SSH_KEY=your-private-ssh-key-content
PRODUCTION_PORT=22 (optional, defaults to 22)
DEPLOY_PATH=/opt/medhasakthi (optional, defaults to /opt/medhasakthi)
```

### 🌐 Domain Configuration:
```
DOMAIN=medhasakthi.com (your actual domain)
```

### 📧 Optional Notification Secrets:
```
SLACK_WEBHOOK=https://hooks.slack.com/services/... (for Slack notifications)
DISCORD_WEBHOOK=https://discord.com/api/webhooks/... (for Discord notifications)
```

## Setting Up GitHub Secrets

### Step 1: Generate SSH Key for Production Server

On your production server, generate an SSH key pair:
```bash
# On your production server
ssh-keygen -t rsa -b 4096 -C "github-actions@medhasakthi.com"
# Save as: /home/your-user/.ssh/github_actions_key

# Add public key to authorized_keys
cat ~/.ssh/github_actions_key.pub >> ~/.ssh/authorized_keys

# Get the private key content (copy this for GitHub secrets)
cat ~/.ssh/github_actions_key
```

### Step 2: Add Secrets to GitHub

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with its value:

#### Required Production Secrets:
- **PRODUCTION_HOST**: Your server IP or domain (e.g., `123.456.789.0` or `server.medhasakthi.com`)
- **PRODUCTION_USER**: SSH username (e.g., `ubuntu`, `root`, or your username)
- **PRODUCTION_SSH_KEY**: The private key content from Step 1 (entire content including headers)
- **DOMAIN**: Your domain name (e.g., `medhasakthi.com`)

#### Optional Secrets:
- **PRODUCTION_PORT**: SSH port (default: 22)
- **DEPLOY_PATH**: Application path on server (default: `/opt/medhasakthi`)

## Production Server Setup

### Step 3: Prepare Your Production Server

Run this script on your production server to set it up:
```bash
# Download and run the setup script
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/MEDHASAKTHI/main/setup-production-server.sh -o setup-production-server.sh
chmod +x setup-production-server.sh
./setup-production-server.sh
```

This script will:
- Install Docker and Docker Compose
- Set up the application directory
- Clone your repository
- Generate SSH keys for GitHub Actions
- Configure firewall and SSL
- Create systemd service for auto-start

### Step 4: Configure Your Domain

1. Point your domain DNS to your production server IP
2. Update the DOMAIN secret in GitHub with your actual domain
3. Ensure SSL certificate is configured (script will help with this)

## Deployment Process

### Automatic Deployment (Recommended)

1. **Push to Main Branch**: Any push to the main branch triggers deployment
2. **GitHub Actions Pipeline**:
   - Tests all code
   - Builds Docker images
   - Pushes images to GitHub Container Registry
   - Deploys to production server via SSH
   - Runs health checks
   - Executes database migrations

### Manual Deployment (Backup)

If automatic deployment fails:
```bash
# On your production server
cd /opt/medhasakthi
git pull origin main
docker-compose build --no-cache
docker-compose up -d
```

## Verification

After deployment, verify everything is working:
```bash
# Download and run verification script
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/MEDHASAKTHI/main/verify-production-deployment.sh -o verify.sh
chmod +x verify.sh
./verify.sh your-domain.com
```

## Current Issues Fixed

### ✅ Production-Ready CI/CD
- Full Docker registry integration with GitHub Container Registry
- Automatic deployment to production server via SSH
- Health checks and database migrations
- Proper environment variable handling

### ✅ Port Configuration
- Updated all references from port 8000 to 8080
- Fixed backend, frontend, and nginx configurations

### ✅ Security & SSL
- SSH key-based authentication for deployments
- SSL certificate setup and verification
- Firewall configuration

### ✅ Monitoring & Verification
- Comprehensive health checks
- Response time monitoring
- Error log analysis
- Disk space monitoring

## Workflow Files

### `simple-ci.yml` (Recommended)
- ✅ Ready to use immediately
- ✅ Tests all components
- ✅ Runs integration tests
- ✅ No external dependencies required

### `ci-cd.yml` (Advanced)
- ⚠️ Requires server setup
- ⚠️ Needs SSH keys and secrets
- ⚠️ Complex deployment pipeline
- ⚠️ Production-ready features

## Troubleshooting

### Build Failures
```bash
# Check the Actions tab in GitHub
# Look for specific error messages
# Common issues:
# - Missing dependencies
# - Port conflicts
# - Environment variable issues
```

### Integration Test Failures
```bash
# Services not starting:
# - Check Docker build logs
# - Verify port configurations
# - Check environment variables

# Health check failures:
# - Increase wait times
# - Check service logs
# - Verify endpoint URLs
```

### Deployment Issues
```bash
# SSH connection failures:
# - Verify SSH keys are correct
# - Check server accessibility
# - Confirm user permissions

# Docker issues on server:
# - Ensure Docker is installed
# - Check disk space
# - Verify Docker permissions
```

## Manual Deployment

If CI/CD fails, you can deploy manually:

```bash
# 1. Clone repository on server
git clone https://github.com/your-username/MEDHASAKTHI.git
cd MEDHASAKTHI

# 2. Set up environment
cp .env.example .env
# Edit .env with your values

# 3. Deploy
docker-compose build --no-cache
docker-compose up -d

# 4. Verify
curl http://localhost:8080/health
curl http://localhost:3000
```

## Next Steps

1. **Test the Simple Pipeline**: Push to main branch and check Actions tab
2. **Monitor Results**: Watch the integration tests complete
3. **Set Up Production**: Configure servers and SSH keys for advanced deployment
4. **Add Monitoring**: Set up health checks and notifications

## Support

If you encounter issues:
1. Check the GitHub Actions logs
2. Review the troubleshooting section
3. Test deployment locally first
4. Verify all environment variables are set correctly

The simple CI/CD pipeline should work immediately after pushing to GitHub. The advanced pipeline requires additional server setup and configuration.
