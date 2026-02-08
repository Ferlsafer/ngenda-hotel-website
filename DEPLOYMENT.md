# Ngenda Hotel Website - Deployment Guide

## 🚀 Production Deployment Instructions

### 1. Environment Setup

#### Copy Production Environment File
```bash
# Copy the production environment template
cp .env.production .env
```

#### Update Production Values
Edit `.env` file with your actual production values:
- `HMS_API_URL`: Your HMS API endpoint
- `HMS_API_KEY`: Your production API key
- `HMS_AUTH_EMAIL`: HMS authentication email
- `HMS_AUTH_PASSWORD`: HMS authentication password

### 2. Install Dependencies

#### System Dependencies
```bash
# Update system packages
sudo apt update && sudo apt install -y python3 python3-pip python3-venv nginx

# Python dependencies
pip install -r requirements.txt
```

### 3. Production Server Setup

#### Using Gunicorn (Recommended)
```bash
# Install Gunicorn
pip install gunicorn

# Start production server
gunicorn --bind 0.0.0.0:5002 --workers 4 --timeout 120 app:app
```

#### Using uWSGI (Alternative)
```bash
# Install uWSGI
pip install uwsgi

# Start with uWSGI
uwsgi --http 0.0.0.0:5002 --wsgi-file app:app --processes 4 --threads 2
```

### 4. Web Server Configuration

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static {
        alias /path/to/your/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 5. SSL/HTTPS Setup

#### Let's Encrypt Certificate
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 6. Process Management

#### Systemd Service (Linux)
```ini
# /etc/systemd/system/ngenda-hotel.service
[Unit]
Description=Ngenda Hotel Website
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/venv/bin
ExecStart=/path/to/your/venv/bin/gunicorn --bind 0.0.0.0:5002 --workers 4 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Service
```bash
sudo systemctl enable ngenda-hotel.service
sudo systemctl start ngenda-hotel.service
sudo systemctl status ngenda-hotel.service
```

### 7. HMS API Integration

#### Production HMS Settings
- ✅ **API URL**: `https://api.ngendahotel.com`
- ✅ **Authentication**: JWT token-based
- ✅ **Fallback**: Mock rooms if HMS is down
- ✅ **Error Handling**: Graceful degradation

#### API Endpoints Used
- `GET /api/public/rooms` - Room availability
- `POST /api/bookings/` - Create bookings
- `POST /api/auth/login` - Get JWT token

### 8. Monitoring & Logging

#### Application Monitoring
```bash
# Application logs
tail -f /var/log/ngenda-hotel/app.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# System service logs
journalctl -u ngenda-hotel -f
```

#### Health Checks
```bash
# Application health check
curl -f http://localhost:5002/health || echo "App is down"

# HMS API connectivity check
curl -f https://api.ngendahotel.com/api/public/rooms || echo "HMS API is down"
```

### 9. Security Considerations

#### Production Security
- ✅ **Environment Variables**: Sensitive data in `.env` file
- ✅ **HTTPS**: SSL certificate installed
- ✅ **Firewall**: Only necessary ports open
- ✅ **Rate Limiting**: Prevent abuse
- ✅ **Input Validation**: All user inputs sanitized

#### File Permissions
```bash
# Secure application files
sudo chown -R www-data:www-data /path/to/your/app
sudo chmod -R 755 /path/to/your/app
sudo chmod -R 644 /path/to/your/app/.env
```

### 10. Deployment Checklist

#### Pre-Deployment Checklist
- [ ] Environment variables configured
- [ ] Database connection tested
- [ ] HMS API credentials verified
- [ ] SSL certificate obtained
- [ ] Domain DNS configured
- [ ] Firewall rules set
- [ ] Backup strategy planned

#### Post-Deployment Checklist
- [ ] Website accessible via HTTPS
- [ ] All static files loading
- [ ] Booking form functional
- [ ] HMS API connectivity confirmed
- [ ] Contact form working
- [ ] Mobile responsive design
- [ ] Performance optimized

### 11. Troubleshooting

#### Common Issues
1. **HMS API Connection Failed**
   - Check API URL and credentials
   - Verify network connectivity
   - Fallback to mock rooms activated

2. **Static Files Not Loading**
   - Check Nginx static file configuration
   - Verify file permissions
   - Clear browser cache

3. **Booking Form Not Working**
   - Check JavaScript console for errors
   - Verify form field names
   - Test HMS API endpoints

4. **High Memory Usage**
   - Reduce Gunicorn workers
   - Optimize database queries
   - Enable caching

### 12. Rollback Plan

#### Emergency Rollback
```bash
# Quick rollback to previous version
git checkout previous-stable-tag
sudo systemctl restart ngenda-hotel.service

# Database rollback (if needed)
# Restore from backup
mysql ngenda_hotel < backup.sql
# or
sqlite ngenda_hotel.db < backup.sql
```

---

## 🎯 Production Ready Features

### ✅ Current Implementation
- **Modern UI**: Horizontal booking form layout
- **Multiple Booking Channels**: Website, WhatsApp, Booking.com
- **HMS Integration**: Real-time room data with fallback
- **Mobile Responsive**: Optimized for all devices
- **Contact Management**: Multiple contact methods
- **Error Handling**: Graceful degradation
- **Security**: Input validation and sanitization

### 🔄 HMS Integration Status
- **API Ready**: Configured for production HMS endpoint
- **Fallback Active**: Mock rooms ensure functionality
- **Authentication**: JWT-based auth system ready
- **Error Recovery**: Automatic fallback on HMS failure

The website is production-ready and can be deployed immediately! 🚀
