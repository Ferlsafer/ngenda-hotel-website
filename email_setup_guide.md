# Email Setup Guide for Ngenda Hotel Contact Form

## Hotel Email Configuration

### Step 1: Determine Email Provider for info@ngendahotel.co.tz
First, find out who hosts the hotel email:
- Is it Gmail? (Google Workspace)
- Is it Outlook/Hotmail? 
- Is it a domain hosting service?
- Is it a custom email server?

### Step 2: Get SMTP Settings
You'll need:
- **SMTP Server**: smtp.gmail.com, smtp.office365.com, etc.
- **Port**: Usually 587 (TLS) or 465 (SSL)
- **Username**: info@ngendahotel.co.tz
- **Password**: Hotel email password
- **Security**: TLS/SSL settings

### Step 3: Common Email Provider Settings

#### If using Gmail/Google Workspace:
```python
sender_email = 'info@ngendahotel.co.tz'
sender_password = 'hotel-app-password'  # Use app password, not regular password
smtp_server = 'smtp.gmail.com'
smtp_port = 587
```

#### If using Outlook/Office 365:
```python
sender_email = 'info@ngendahotel.co.tz'
sender_password = 'hotel-email-password'
smtp_server = 'smtp.office365.com'
smtp_port = 587
```

#### If using other providers:
Check their SMTP documentation for correct settings.

### Step 4: Update the Email Configuration
In `app.py`, update these lines:

```python
# Replace with actual hotel email settings
sender_email = 'info@ngendahotel.co.tz'
sender_password = 'hotel-actual-password'  # Update this line
```

Also update SMTP server if not using Gmail:
```python
server = smtplib.SMTP('actual-smtp-server', port)
```

### Step 5: Test the Contact Form
1. Start the Flask application
2. Go to the contact page: http://localhost:5000/contact
3. Fill out the form with test data
4. Click "Submit"
5. Check email at info@ngendahotel.co.tz

## Security Notes
- Use app passwords instead of regular passwords when possible
- Store credentials securely (environment variables recommended)
- Consider using email service APIs for production

## Troubleshooting
- Check SMTP server and port settings
- Verify email password is correct
- Ensure firewall allows SMTP traffic
- Check if 2FA requires app password
