# 🏠 MEDHASAKTHI Local PC Deployment Guide

## 📋 Overview

Deploy MEDHASAKTHI on your own computer and make it accessible via medhasakthi.com. This approach offers:

- **💰 Zero server costs** - No monthly cloud bills
- **🚀 Immediate deployment** - Start in 15 minutes
- **🔧 Full control** - Complete access to your system
- **🔄 Easy migration** - Move to cloud anytime

## 🎯 Prerequisites

### Hardware Requirements
- **CPU**: Intel i5/AMD Ryzen 5 or better (4+ cores)
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 50GB free space (SSD preferred)
- **Internet**: Stable broadband connection

### Software Requirements
- **Windows 10/11**, **Ubuntu 20.04+**, or **macOS 10.15+**
- **Docker Desktop** (latest version)
- **Git** (for cloning repository)
- **Router admin access** (for port forwarding)

### Network Requirements
- **Public IP** (static or dynamic with DDNS)
- **Port forwarding capability** on your router
- **Domain control** (medhasakthi.com DNS management)

## 🔧 Step-by-Step Deployment

### Step 1: Install Docker Desktop (5 minutes)

**Windows/macOS:**
1. Download from https://www.docker.com/products/docker-desktop
2. Install and restart your computer
3. Start Docker Desktop
4. Verify: Open terminal/cmd and run `docker --version`

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo usermod -a -G docker $USER
# Logout and login again
```

### Step 2: Clone MEDHASAKTHI Repository (2 minutes)

```bash
# Clone the repository
git clone https://github.com/your-org/medhasakthi.git
cd medhasakthi

# Make scripts executable (Linux/macOS)
chmod +x deploy-local.sh migrate-to-cloud.sh
```

### Step 3: Deploy MEDHASAKTHI (10 minutes)

**Linux/macOS:**
```bash
./deploy-local.sh
```

**Windows:**
```cmd
deploy-local-windows.bat
```

The script will:
- ✅ Check Docker installation
- ✅ Generate secure environment configuration
- ✅ Create SSL certificates (self-signed)
- ✅ Build and start all services
- ✅ Set up monitoring and backups

### Step 4: Configure Router Port Forwarding (5 minutes)

**Required Port Forwards:**
```
External Port 80 → Internal IP:80 (HTTP)
External Port 443 → Internal IP:443 (HTTPS)
```

**Common Router Interfaces:**
- **TP-Link**: Advanced → NAT Forwarding → Virtual Servers
- **Netgear**: Dynamic DNS → Port Forwarding
- **Linksys**: Smart Wi-Fi Tools → Port Range Forward
- **ASUS**: Adaptive QoS → Port Forwarding

**Example Configuration:**
```
Service Name: MEDHASAKTHI-HTTP
External Port: 80
Internal Port: 80
Internal IP: 192.168.1.100 (your PC's IP)
Protocol: TCP

Service Name: MEDHASAKTHI-HTTPS
External Port: 443
Internal Port: 443
Internal IP: 192.168.1.100
Protocol: TCP
```

### Step 5: Configure DNS (5 minutes)

**Point medhasakthi.com to your public IP:**

1. **Find your public IP:**
   ```bash
   curl ifconfig.me
   ```

2. **Update DNS records:**
   ```
   Type: A
   Name: @
   Value: YOUR_PUBLIC_IP
   TTL: 300

   Type: A
   Name: www
   Value: YOUR_PUBLIC_IP
   TTL: 300
   ```

3. **Verify DNS propagation:**
   ```bash
   dig medhasakthi.com A
   ```

## 🔍 Verification & Testing

### Local Access (Immediate)
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001

### External Access (After DNS propagation)
- **Main Site**: https://medhasakthi.com
- **API Docs**: https://medhasakthi.com/api/docs
- **Monitoring**: https://medhasakthi.com:3001

### Health Check Script
```bash
# Check all services
docker-compose -f docker-compose.local.yml ps

# Test endpoints
curl -k https://localhost/health
curl -k https://localhost/api/health

# Check from external network
curl https://medhasakthi.com/health
```

## 🔧 Management Commands

### Service Management
```bash
# Start all services
docker-compose -f docker-compose.local.yml up -d

# Stop all services
docker-compose -f docker-compose.local.yml down

# View logs
docker-compose -f docker-compose.local.yml logs -f

# Restart specific service
docker-compose -f docker-compose.local.yml restart backend
```

### Backup Management
```bash
# Create backup (Linux/macOS)
./backup-local.sh

# Create backup (Windows)
backup-local.bat

# View backups
ls -la backups/
```

### System Monitoring
```bash
# Check resource usage
docker stats

# Check disk usage
df -h

# Monitor logs
tail -f logs/*.log
```

## 🌐 Dynamic IP Solutions

If you don't have a static IP, use Dynamic DNS:

### Option 1: No-IP (Free)
1. Sign up at https://www.noip.com/
2. Create hostname: medhasakthi.ddns.net
3. Install No-IP DUC client
4. Point medhasakthi.com CNAME to medhasakthi.ddns.net

### Option 2: DuckDNS (Free)
1. Sign up at https://www.duckdns.org/
2. Create subdomain: medhasakthi.duckdns.org
3. Set up auto-update script
4. Point medhasakthi.com CNAME to medhasakthi.duckdns.org

### Option 3: Router DDNS
Many routers have built-in DDNS support:
- TP-Link: Advanced → Dynamic DNS
- Netgear: Dynamic DNS settings
- ASUS: Adaptive QoS → DDNS

## 🔒 Security Considerations

### Firewall Configuration
```bash
# Linux (UFW)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Windows Firewall
# Allow Docker Desktop through Windows Defender Firewall
```

### SSL Certificate Upgrade
```bash
# Replace self-signed with Let's Encrypt (requires domain access)
sudo certbot certonly --standalone -d medhasakthi.com -d www.medhasakthi.com
# Update nginx configuration to use new certificates
```

### Regular Updates
```bash
# Update Docker images
docker-compose -f docker-compose.local.yml pull
docker-compose -f docker-compose.local.yml up -d

# Update system packages
sudo apt update && sudo apt upgrade -y  # Linux
# Use Windows Update for Windows
```

## 🚀 Migration to Cloud

When ready to move to cloud:

```bash
# Run migration script
./migrate-to-cloud.sh

# Follow prompts to:
# 1. Specify cloud server details
# 2. Transfer all data and configuration
# 3. Update DNS to point to cloud server
# 4. Verify migration success
```

## 🔧 Troubleshooting

### Common Issues

1. **Docker not starting**
   ```bash
   # Restart Docker Desktop
   # Check system resources (RAM/CPU)
   # Update Docker Desktop
   ```

2. **Port forwarding not working**
   ```bash
   # Check router configuration
   # Verify internal IP address
   # Test with online port checker
   ```

3. **DNS not resolving**
   ```bash
   # Check DNS propagation: whatsmydns.net
   # Verify public IP hasn't changed
   # Clear DNS cache: ipconfig /flushdns
   ```

4. **SSL certificate warnings**
   ```bash
   # Expected with self-signed certificates
   # Click "Advanced" → "Proceed to site"
   # Or upgrade to Let's Encrypt certificate
   ```

### Performance Optimization

1. **Increase Docker resources**
   - Docker Desktop → Settings → Resources
   - Allocate more CPU/RAM to Docker

2. **Use SSD storage**
   - Move Docker data to SSD
   - Use SSD for application data

3. **Optimize network**
   - Use wired connection instead of Wi-Fi
   - Configure QoS for MEDHASAKTHI traffic

## 📊 Monitoring & Maintenance

### Daily Tasks
- Check service status: `docker-compose ps`
- Monitor resource usage: `docker stats`
- Review logs for errors

### Weekly Tasks
- Create backup: `./backup-local.sh`
- Check for updates
- Review monitoring dashboards

### Monthly Tasks
- Update Docker images
- Clean up old logs and backups
- Review security settings

## 💰 Cost Comparison

### Local Deployment
- **Hardware**: One-time cost (if upgrading)
- **Electricity**: ~$10-20/month
- **Internet**: Existing broadband
- **Total**: ~$10-20/month

### Cloud Deployment
- **Server**: $25-50/month
- **Bandwidth**: $5-10/month
- **Backups**: $5/month
- **Total**: $35-65/month

**Savings**: $300-600/year with local deployment!

## 🎯 When to Migrate to Cloud

Consider cloud migration when:
- **Traffic increases** (>1000 concurrent users)
- **Reliability requirements** increase (99.9% uptime)
- **Global audience** needs better performance
- **Team collaboration** requires shared access
- **Compliance** requires specific certifications

---

## 🎉 Success!

**MEDHASAKTHI is now running on your PC and accessible at https://medhasakthi.com!**

**Benefits achieved:**
- ✅ Zero monthly server costs
- ✅ Full control over your platform
- ✅ Immediate deployment and testing
- ✅ Easy migration path to cloud
- ✅ Professional domain (medhasakthi.com)

**You now have a production-ready educational platform running from your own computer!** 🚀
