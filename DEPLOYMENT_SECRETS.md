# 🔐 Deployment Secrets Configuration

This document describes all the GitHub Secrets required for automated deployment to VPS.

## Required Secrets

### 1. VPS SSH Access

#### `VPS_SSH_KEY`
- **Description**: Private SSH key for accessing the VPS
- **Format**: Full private key content (including `-----BEGIN OPENSSH PRIVATE KEY-----`)
- **How to get**:
  ```bash
  # Generate a new SSH key pair (if you don't have one)
  ssh-keygen -t ed25519 -C "github-actions@aapanel" -f ~/.ssh/aapanel_deploy
  
  # Copy the private key (this goes to GitHub Secrets)
  cat ~/.ssh/aapanel_deploy
  
  # Copy the public key to VPS
  ssh-copy-id -i ~/.ssh/aapanel_deploy.pub user@your-vps-ip
  ```

#### `VPS_HOST`
- **Description**: VPS IP address or hostname
- **Format**: IP address or domain name
- **Example**: `192.168.1.100` or `vps.example.com`

#### `VPS_USER`
- **Description**: SSH username for VPS access
- **Format**: Username string
- **Example**: `root` or `deploy` or `ubuntu`
- **Recommendation**: Use a non-root user with sudo privileges

#### `VPS_DOMAIN`
- **Description**: Public domain name for the application
- **Format**: Domain name (without protocol)
- **Example**: `aapanel.example.com`

### 2. Docker Registry Access

The deployment workflow uses GitHub Container Registry (ghcr.io) which is automatically authenticated using `GITHUB_TOKEN`. No additional registry secrets are needed.

## Setup Instructions

### Step 1: Add Secrets to GitHub Repository

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret listed above

### Step 2: Configure VPS

#### 2.1 Prepare VPS User

```bash
# SSH to your VPS as root
ssh root@your-vps-ip

# Create deployment user (if not exists)
useradd -m -s /bin/bash deploy
usermod -aG sudo deploy
usermod -aG docker deploy

# Set password (optional)
passwd deploy
```

#### 2.2 Setup SSH Key Authentication

```bash
# On your local machine or GitHub Actions runner
# Copy the public key to VPS
ssh-copy-id -i ~/.ssh/aapanel_deploy.pub deploy@your-vps-ip

# Test SSH connection
ssh -i ~/.ssh/aapanel_deploy deploy@your-vps-ip
```

#### 2.3 Prepare Deployment Directory

```bash
# On VPS
sudo mkdir -p /opt/aapanel
sudo chown deploy:deploy /opt/aapanel
cd /opt/aapanel

# Create .env file
nano .env
# Add your environment variables (see .env.example)
```

#### 2.4 Install Docker & Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

### Step 3: Configure GitHub Environments

1. Go to: **Settings** → **Environments**
2. Create environment: `production`
3. Add environment-specific secrets (if any)
4. Configure protection rules:
   - ✅ Required reviewers (optional)
   - ✅ Wait timer (optional)
   - ✅ Deployment branches: `main` only

### Step 4: Test Deployment

#### Manual Trigger
1. Go to: **Actions** → **Deploy to VPS**
2. Click **Run workflow**
3. Select environment: `production`
4. Click **Run workflow**

#### Automatic Trigger
- Push to `main` branch after successful build
- The workflow will automatically trigger after Docker image is built

## Environment Variables on VPS

Ensure your `/opt/aapanel/.env` file contains:

```bash
# Application
ENVIRONMENT=production
SECRET_KEY=your-super-secret-key-here
PORT=5000

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/production_db
POSTGRES_USER=aapanel_user
POSTGRES_PASSWORD=strong-password-here
POSTGRES_DB=production_db

# Redis
REDIS_URL=redis://redis:6379/0

# Domain
DOMAIN=aapanel.example.com
```

## Security Best Practices

### ✅ Do's
- **Use strong passwords** for all services
- **Rotate SSH keys** regularly
- **Use non-root user** for deployment
- **Enable firewall** (UFW) on VPS
- **Keep secrets secure** - never commit to Git
- **Use environment-specific** secrets

### ❌ Don'ts
- **Don't use root** for deployment
- **Don't expose** database ports publicly
- **Don't hardcode** secrets in code
- **Don't share** private keys
- **Don't commit** .env files

## Troubleshooting

### Issue: SSH Connection Failed
```bash
# Debug SSH connection
ssh -vvv -i ~/.ssh/aapanel_deploy deploy@your-vps-ip

# Check SSH key permissions
chmod 600 ~/.ssh/aapanel_deploy
```

### Issue: Docker Permission Denied
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo
sudo docker-compose up -d
```

### Issue: Health Check Failed
```bash
# Check container logs
docker-compose logs -f app

# Check container status
docker-compose ps

# Check network connectivity
curl -v http://localhost:5000/health
```

### Issue: Deployment Rollback
The deployment script automatically rolls back on failure. Check logs:
```bash
# On VPS
cd /opt/aapanel
docker-compose logs --tail=100
```

## Maintenance

### Viewing Logs
```bash
# On VPS
cd /opt/aapanel

# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f app
```

### Manual Rollback
```bash
# If automatic rollback fails
cd /opt/aapanel

# Stop current version
docker-compose down

# Restore backup
mv docker-compose.backup.yml docker-compose.yml

# Start previous version
docker-compose up -d
```

### Cleanup Old Images
```bash
# The deployment script does this automatically
# Manual cleanup if needed:
docker image prune -a -f
docker volume prune -f
```

## Support

For issues or questions:
1. Check workflow logs in GitHub Actions
2. Check application logs on VPS
3. Review this documentation
4. Contact the DevOps team

---

**Last Updated**: September 30, 2025  
**Maintained By**: aaPanel Team
