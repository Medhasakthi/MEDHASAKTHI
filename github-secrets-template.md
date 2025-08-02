# GitHub Secrets Configuration Template

## Required Secrets for Production Deployment

Copy these values to your GitHub repository secrets:

### 🔐 Production Server Configuration

```
Secret Name: PRODUCTION_HOST
Value: YOUR_SERVER_IP_OR_DOMAIN
Example: 123.456.789.0 or server.medhasakthi.com
```

```
Secret Name: PRODUCTION_USER
Value: YOUR_SSH_USERNAME
Example: ubuntu, root, or your-username
```

```
Secret Name: PRODUCTION_SSH_KEY
Value: YOUR_PRIVATE_SSH_KEY_CONTENT
Example: 
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAFwAAAAdzc2gtcn
[... full private key content ...]
-----END OPENSSH PRIVATE KEY-----
```

```
Secret Name: DOMAIN
Value: YOUR_DOMAIN_NAME
Example: medhasakthi.com
```

### 🔧 Optional Configuration

```
Secret Name: PRODUCTION_PORT
Value: 22
Description: SSH port (default: 22)
```

```
Secret Name: DEPLOY_PATH
Value: /opt/medhasakthi
Description: Application path on server (default: /opt/medhasakthi)
```

## How to Add Secrets to GitHub

1. Go to your GitHub repository
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Enter the secret name and value
6. Click **Add secret**

## Environment Setup (Optional)

For additional security, you can create a production environment:

1. Go to **Settings** → **Environments**
2. Click **New environment**
3. Name it `production`
4. Add protection rules:
   - Required reviewers (optional)
   - Wait timer (optional)
   - Deployment branches (main only)

## Verification Checklist

Before pushing to trigger deployment:

- [ ] PRODUCTION_HOST is set to your server IP/domain
- [ ] PRODUCTION_USER is set to your SSH username
- [ ] PRODUCTION_SSH_KEY contains the full private key
- [ ] DOMAIN is set to your actual domain name
- [ ] Your server is accessible via SSH
- [ ] Docker and Docker Compose are installed on server
- [ ] Your domain DNS points to the server
- [ ] .env file is configured on the server

## Testing Your Setup

1. **Test SSH Connection**:
   ```bash
   ssh -i ~/.ssh/github_actions_key YOUR_USER@YOUR_SERVER
   ```

2. **Test Domain Resolution**:
   ```bash
   nslookup your-domain.com
   ```

3. **Test Server Readiness**:
   ```bash
   # On your server
   docker --version
   docker-compose --version
   ls -la /opt/medhasakthi
   ```

## Common Issues and Solutions

### SSH Connection Failed
- Verify the private key format (should include headers)
- Check if the public key is in ~/.ssh/authorized_keys on server
- Ensure SSH service is running on the server

### Domain Not Resolving
- Check DNS configuration
- Wait for DNS propagation (up to 24 hours)
- Test with server IP directly first

### Docker Issues
- Ensure Docker service is running: `sudo systemctl start docker`
- Check user permissions: `sudo usermod -aG docker $USER`
- Restart session after adding user to docker group

### Deployment Fails
- Check GitHub Actions logs for specific errors
- Verify all secrets are correctly set
- Test manual deployment on server first

## Security Best Practices

1. **Use dedicated SSH keys** for GitHub Actions (not your personal keys)
2. **Limit SSH key permissions** to specific commands if possible
3. **Use environment protection rules** for production deployments
4. **Regularly rotate SSH keys** and update secrets
5. **Monitor deployment logs** for suspicious activity

## Support

If you encounter issues:
1. Check the GitHub Actions logs in the Actions tab
2. Verify all secrets are correctly configured
3. Test SSH connection manually
4. Run the verification script on your server
5. Check server logs: `docker-compose logs`
