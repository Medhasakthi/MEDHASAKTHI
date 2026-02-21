# MEDHASAKTHI Deployment Troubleshooting Guide

## Issue: Seeing File Listings Instead of Web Pages

When you access your deployed application and see a directory listing or file browser instead of the actual web application, this is typically caused by one of these issues:

### 1. **Missing or Incorrect index.html**

**Symptoms:**
- Browser shows directory listing
- 404 errors for the main page
- Files are visible but not served as a web app

**Solution:**
```bash
# Check if index.html exists in the frontend container
docker-compose exec frontend ls -la /usr/share/nginx/html/

# If index.html is missing, rebuild the frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### 2. **Nginx Configuration Issues**

**Symptoms:**
- Directory listing enabled
- Nginx not serving the React app properly
- Routes not working

**Solution:**
The nginx configuration has been updated to:
- Disable directory listing (`autoindex off`)
- Properly handle React Router with `try_files`
- Serve index.html for all routes

### 3. **SSL Certificate Issues**

**Symptoms:**
- Nginx fails to start
- SSL errors in logs
- Services not accessible

**Solution:**
The nginx configuration has been updated to work without SSL certificates for testing:
- HTTP-only configuration enabled
- SSL servers commented out
- Access via `http://localhost` instead of `https://`

### 4. **React Build Issues**

**Symptoms:**
- Empty build directory
- Missing static files
- JavaScript errors in browser console

**Solution:**
```bash
# Check build output
docker-compose exec frontend ls -la /usr/share/nginx/html/static/

# Rebuild with verbose output
docker-compose build --no-cache frontend
```

## Quick Fix Commands

### Windows:
```cmd
# Run the automated fix script
fix-deployment.bat
```

### Linux/Mac:
```bash
# Make script executable and run
chmod +x fix-deployment.sh
./fix-deployment.sh
```

### Manual Steps:
```bash
# 1. Stop all services
docker-compose down

# 2. Clean up
docker-compose down --rmi all --volumes --remove-orphans

# 3. Rebuild everything
docker-compose build --no-cache

# 4. Start services
docker-compose up -d

# 5. Check status
docker-compose ps
docker-compose logs frontend
```

## Testing Your Deployment

After fixing, test these URLs:

1. **Main Application:** http://localhost
2. **Frontend Direct:** http://localhost:3000
3. **Backend API:** http://localhost:8080/health
4. **API Documentation:** http://localhost:8080/docs

## Common Error Messages and Solutions

### "403 Forbidden"
- Check nginx configuration
- Verify file permissions in container
- Ensure index.html exists

### "502 Bad Gateway"
- Backend service not running
- Check docker-compose logs backend
- Verify backend health endpoint

### "Connection Refused"
- Docker containers not started
- Port conflicts
- Firewall blocking ports

### "This site can't be reached"
- Wrong URL or port
- Services not exposed correctly
- Check docker-compose port mappings

## Debugging Commands

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs frontend
docker-compose logs nginx
docker-compose logs backend

# Access container shell
docker-compose exec frontend sh
docker-compose exec nginx sh

# Check nginx configuration
docker-compose exec nginx nginx -t

# Check file contents
docker-compose exec frontend cat /usr/share/nginx/html/index.html
```

## Production Deployment Notes

For production deployment:
1. Uncomment SSL configuration in nginx/nginx.conf
2. Add proper SSL certificates
3. Update domain names in configuration
4. Enable HTTPS redirects
5. Configure proper environment variables

## Getting Help

If you're still experiencing issues:
1. Run the fix script first
2. Check the logs for specific error messages
3. Verify all containers are running
4. Test each service individually
5. Check browser developer console for JavaScript errors
