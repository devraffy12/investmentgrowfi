# Security Monitoring Checklist for Investment Platform

## 🛡️ ATTACK DETECTION SIGNS

### 1. **Brute Force Attacks**
- ❌ Multiple failed login attempts from same IP
- ❌ Unusual spike in registration attempts
- ❌ Multiple accounts with similar patterns
- ❌ Rapid-fire requests to login endpoint

### 2. **Financial Fraud**
- ❌ Large amount deposits from new accounts
- ❌ Immediate withdrawals after deposits
- ❌ Multiple accounts with same payment details
- ❌ Transactions outside normal hours

### 3. **Data Breaches**
- ❌ Unauthorized admin access
- ❌ Unusual database queries
- ❌ Mass data exports
- ❌ Changes to user permissions

### 4. **System Compromise**
- ❌ New admin accounts created
- ❌ Code changes in production
- ❌ Unusual server resource usage
- ❌ Unexpected file modifications

## 🔍 MONITORING COMMANDS

### Daily Security Check:
```bash
python security_monitor.py
```

### Weekly Deep Scan:
```bash
python manage.py shell -c "
from django.contrib.auth.models import User
from myproject.models import UserProfile, Transaction
from datetime import timedelta
from django.utils import timezone

week_ago = timezone.now() - timedelta(days=7)
print(f'New users this week: {User.objects.filter(date_joined__gte=week_ago).count()}')
print(f'Total transactions this week: {Transaction.objects.filter(created_at__gte=week_ago).count()}')
print(f'Large transactions (≥₱10,000): {Transaction.objects.filter(amount__gte=10000, created_at__gte=week_ago).count()}')
"
```

### Check for Suspicious Users:
```bash
python manage.py shell -c "
from django.contrib.auth.models import User
from myproject.models import UserProfile
from django.db.models import Count

# Users with no profiles
orphaned = User.objects.filter(userprofile__isnull=True)
print(f'Users without profiles: {orphaned.count()}')
for user in orphaned[:5]:
    print(f'  - {user.username} (joined: {user.date_joined})')

# High balance accounts
high_balance = UserProfile.objects.filter(balance__gte=10000)
print(f'High balance accounts: {high_balance.count()}')
for profile in high_balance[:5]:
    print(f'  - {profile.user.username}: ₱{profile.balance}')
"
```

## 🚨 IMMEDIATE ACTIONS IF ATTACKED

### 1. **Identify Attack Type**
```bash
# Run security scan
python security_monitor.py

# Check recent activity
python manage.py shell -c "
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

hour_ago = timezone.now() - timedelta(hours=1)
recent_users = User.objects.filter(date_joined__gte=hour_ago)
print(f'Users created in last hour: {recent_users.count()}')
if recent_users.count() > 0:
    print('Recent registrations:')
    for user in recent_users:
        print(f'  - {user.username} at {user.date_joined}')
"
```

### 2. **Emergency Response**
- 🚨 **Backup database immediately**
- 🚨 **Change all admin passwords**
- 🚨 **Enable maintenance mode**
- 🚨 **Check server logs**
- 🚨 **Contact hosting provider**

### 3. **Database Backup**
```bash
# Create emergency backup
python manage.py dumpdata > emergency_backup_$(date +%Y%m%d_%H%M%S).json

# Or copy database file
cp db.sqlite3 backup_db_$(date +%Y%m%d_%H%M%S).sqlite3
```

### 4. **Block Suspicious IPs**
```python
# Add to Django settings.py for production
ALLOWED_HOSTS = ['your-domain.com']  # Restrict hosts

# In nginx/Apache config:
# deny 192.168.1.100;  # Block specific IP
```

## 📊 SECURITY LOGS TO CHECK

### Django Application Logs:
- User login attempts
- Failed authentication
- Admin panel access
- Database queries

### Server Access Logs:
- HTTP request patterns
- IP addresses
- Request frequency
- Error codes (404, 500)

### Database Activity:
- Large data exports
- Permission changes
- Schema modifications
- Unusual query patterns

## 🔐 PREVENTIVE MEASURES

### 1. **Rate Limiting**
```python
# In views.py - limit registration attempts
from django.core.cache import cache
from django.http import HttpResponseTooManyRequests

def register(request):
    ip = request.META.get('REMOTE_ADDR')
    cache_key = f'reg_attempts_{ip}'
    attempts = cache.get(cache_key, 0)
    
    if attempts >= 5:  # Max 5 attempts per hour
        return HttpResponseTooManyRequests('Too many registration attempts')
    
    cache.set(cache_key, attempts + 1, 3600)  # 1 hour timeout
    # ... rest of registration logic
```

### 2. **Strong Password Policy**
```python
# In settings.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8,}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

### 3. **HTTPS Only**
```python
# In settings.py for production
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

## 📱 AUTOMATED ALERTS

### Email Alert Script:
```python
import smtplib
from email.mime.text import MIMEText

def send_security_alert(threat_details):
    msg = MIMEText(f"Security threat detected: {threat_details}")
    msg['Subject'] = 'SECURITY ALERT - Investment Platform'
    msg['From'] = 'alerts@yoursite.com'
    msg['To'] = 'admin@yoursite.com'
    
    # Configure your SMTP settings
    # smtp_server.send_message(msg)
```

## 🎯 SECURITY CHECKLIST

### Daily:
- [ ] Run `python security_monitor.py`
- [ ] Check user registration patterns
- [ ] Review large transactions
- [ ] Monitor system resources

### Weekly:
- [ ] Deep security scan
- [ ] Review admin access logs
- [ ] Check database integrity
- [ ] Update security signatures

### Monthly:
- [ ] Security audit
- [ ] Password policy review
- [ ] Backup verification
- [ ] Incident response drill

Remember: **Prevention is better than cure!** 🛡️
