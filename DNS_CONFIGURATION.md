# 🌐 DNS Configuration Guide for MEDHASAKTHI.COM

## 📋 Overview

This guide provides step-by-step instructions for configuring DNS records for medhasakthi.com to point to your production server.

## 🎯 Required DNS Records

### Basic Configuration

| Type | Name | Value | TTL | Priority |
|------|------|-------|-----|----------|
| A | @ | YOUR_SERVER_IP | 300 | - |
| A | www | YOUR_SERVER_IP | 300 | - |
| CNAME | api | medhasakthi.com | 300 | - |
| CNAME | admin | medhasakthi.com | 300 | - |

### Email Configuration (Optional)

| Type | Name | Value | TTL | Priority |
|------|------|-------|-----|----------|
| MX | @ | mail.medhasakthi.com | 300 | 10 |
| A | mail | YOUR_SERVER_IP | 300 | - |
| TXT | @ | "v=spf1 a mx ~all" | 300 | - |

### Security Records (Recommended)

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CAA | @ | 0 issue "letsencrypt.org" | 300 |
| TXT | @ | "v=DMARC1; p=quarantine; rua=mailto:admin@medhasakthi.com" | 300 |

## 🔧 Provider-Specific Instructions

### GoDaddy Configuration

1. **Login to GoDaddy**
   - Go to https://dcc.godaddy.com/
   - Login with your account credentials

2. **Navigate to DNS Management**
   - Click on your domain "medhasakthi.com"
   - Click "DNS" tab

3. **Add/Edit Records**
   ```
   Type: A
   Name: @
   Value: YOUR_SERVER_IP
   TTL: 5 minutes (300 seconds)
   
   Type: A
   Name: www
   Value: YOUR_SERVER_IP
   TTL: 5 minutes (300 seconds)
   ```

4. **Save Changes**
   - Click "Save" for each record
   - Changes may take up to 24 hours to propagate

### Namecheap Configuration

1. **Login to Namecheap**
   - Go to https://ap.www.namecheap.com/
   - Login with your account credentials

2. **Navigate to Domain List**
   - Click "Domain List" in the left sidebar
   - Click "Manage" next to medhasakthi.com

3. **Advanced DNS Settings**
   - Click "Advanced DNS" tab
   - Add the following records:

   ```
   Type: A Record
   Host: @
   Value: YOUR_SERVER_IP
   TTL: 5 min
   
   Type: A Record
   Host: www
   Value: YOUR_SERVER_IP
   TTL: 5 min
   ```

### Cloudflare Configuration (Recommended)

1. **Add Domain to Cloudflare**
   - Go to https://dash.cloudflare.com/
   - Click "Add a Site"
   - Enter "medhasakthi.com"

2. **Configure DNS Records**
   ```
   Type: A
   Name: medhasakthi.com
   IPv4 address: YOUR_SERVER_IP
   Proxy status: Proxied (orange cloud)
   
   Type: A
   Name: www
   IPv4 address: YOUR_SERVER_IP
   Proxy status: Proxied (orange cloud)
   ```

3. **Update Nameservers**
   - Copy the Cloudflare nameservers
   - Update them in your domain registrar
   - Wait for propagation (up to 24 hours)

4. **Configure SSL/TLS**
   - Go to SSL/TLS tab
   - Set encryption mode to "Full (strict)"
   - Enable "Always Use HTTPS"

## 🚀 Quick Setup Commands

### Check Current DNS

```bash
# Check current A record
dig medhasakthi.com A

# Check WWW record
dig www.medhasakthi.com A

# Check from different DNS servers
dig @8.8.8.8 medhasakthi.com A
dig @1.1.1.1 medhasakthi.com A
```

### Verify DNS Propagation

```bash
# Check global DNS propagation
curl -s "https://www.whatsmydns.net/api/details?server=world&type=A&query=medhasakthi.com"

# Check if domain points to your server
SERVER_IP="YOUR_SERVER_IP"
RESOLVED_IP=$(dig +short medhasakthi.com A)
if [[ "$RESOLVED_IP" == "$SERVER_IP" ]]; then
    echo "✅ DNS is correctly configured"
else
    echo "❌ DNS not yet propagated. Current: $RESOLVED_IP, Expected: $SERVER_IP"
fi
```

## 🔍 DNS Verification Script

Create this script to verify your DNS configuration:

```bash
#!/bin/bash
# dns-check.sh

DOMAIN="medhasakthi.com"
SERVER_IP="YOUR_SERVER_IP"

echo "🔍 Checking DNS configuration for $DOMAIN..."

# Check A record
A_RECORD=$(dig +short $DOMAIN A)
if [[ "$A_RECORD" == "$SERVER_IP" ]]; then
    echo "✅ A record: $A_RECORD"
else
    echo "❌ A record: $A_RECORD (expected: $SERVER_IP)"
fi

# Check WWW record
WWW_RECORD=$(dig +short www.$DOMAIN A)
if [[ "$WWW_RECORD" == "$SERVER_IP" ]]; then
    echo "✅ WWW record: $WWW_RECORD"
else
    echo "❌ WWW record: $WWW_RECORD (expected: $SERVER_IP)"
fi

# Check if website is accessible
if curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN | grep -q "200\|301\|302"; then
    echo "✅ Website is accessible"
else
    echo "❌ Website is not accessible"
fi

echo "DNS check completed!"
```

## ⚡ Fast DNS Propagation Tips

1. **Use Low TTL Values**
   - Set TTL to 300 seconds (5 minutes) during setup
   - Increase to 3600 seconds (1 hour) after confirmation

2. **Flush DNS Cache**
   ```bash
   # Linux
   sudo systemctl flush-dns
   
   # macOS
   sudo dscacheutil -flushcache
   
   # Windows
   ipconfig /flushdns
   ```

3. **Use Multiple DNS Checkers**
   - https://www.whatsmydns.net/
   - https://dnschecker.org/
   - https://www.dnswatch.info/

## 🔧 Troubleshooting

### Common Issues

1. **DNS Not Propagating**
   ```bash
   # Check if nameservers are correct
   dig NS medhasakthi.com
   
   # Check from authoritative nameserver
   dig @ns1.your-provider.com medhasakthi.com A
   ```

2. **Mixed Content Errors**
   - Ensure all resources use HTTPS
   - Check for HTTP links in your application

3. **SSL Certificate Issues**
   ```bash
   # Test SSL certificate
   openssl s_client -connect medhasakthi.com:443 -servername medhasakthi.com
   
   # Check certificate expiry
   echo | openssl s_client -connect medhasakthi.com:443 2>/dev/null | openssl x509 -noout -dates
   ```

### Emergency DNS Configuration

If you need immediate access while DNS propagates:

```bash
# Add to /etc/hosts (Linux/macOS) or C:\Windows\System32\drivers\etc\hosts (Windows)
YOUR_SERVER_IP medhasakthi.com
YOUR_SERVER_IP www.medhasakthi.com
```

## 📊 DNS Performance Optimization

### Recommended Settings

1. **TTL Values**
   - A/AAAA records: 300-3600 seconds
   - CNAME records: 300-1800 seconds
   - MX records: 3600-86400 seconds

2. **Use CDN (Cloudflare)**
   - Faster global access
   - DDoS protection
   - SSL termination
   - Caching optimization

3. **Monitor DNS Performance**
   ```bash
   # Check DNS response time
   dig medhasakthi.com | grep "Query time"
   
   # Test from multiple locations
   for server in 8.8.8.8 1.1.1.1 208.67.222.222; do
       echo "Testing $server:"
       dig @$server medhasakthi.com | grep "Query time"
   done
   ```

## ✅ Final Verification Checklist

Before deploying MEDHASAKTHI:

- [ ] A record points to server IP
- [ ] WWW record points to server IP
- [ ] DNS propagation completed globally
- [ ] Domain accessible via HTTP
- [ ] SSL certificate can be generated
- [ ] All subdomains resolve correctly
- [ ] Email records configured (if using email)
- [ ] Security records (CAA, DMARC) configured

## 🎯 Next Steps

Once DNS is configured:

1. **Run Deployment Script**
   ```bash
   # For AWS
   sudo ./deploy-aws.sh
   
   # For DigitalOcean
   sudo ./deploy-digitalocean.sh
   
   # For other providers
   sudo DOMAIN=medhasakthi.com EMAIL=admin@medhasakthi.com ./deploy.sh
   ```

2. **Verify Deployment**
   ```bash
   ./system-status.sh
   ```

3. **Test All Functionality**
   - User registration
   - Payment system
   - Admin panel
   - API endpoints

---

**🎉 Once DNS is configured, MEDHASAKTHI will be live at https://medhasakthi.com in 30 minutes!**
