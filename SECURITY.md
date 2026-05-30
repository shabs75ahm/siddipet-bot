# 🔒 Security Guidelines

## Overview

This document outlines security best practices for the District Activity Monitoring Bot system, covering data protection, API security, and operational security.

---

## 🛡️ Data Protection

### Sensitive Data Classification

| Data | Sensitivity | Protection |
|------|-------------|-----------|
| Telegram Bot Token | **CRITICAL** | Environment variable only |
| Database Credentials | **CRITICAL** | Environment variable, encrypted |
| API Secrets | **HIGH** | HMAC key rotation monthly |
| User IDs | **MEDIUM** | Stored in database, never logged |
| Activity Reports | **MEDIUM** | Database encryption at rest |
| Location Data | **MEDIUM** | Access controlled, audit logged |

### Encryption

```python
# Database encryption at rest (PostgreSQL)
ALTER DATABASE activities SET search_path TO public;

# Use pgcrypto extension for sensitive fields
CREATE EXTENSION pgcrypto;

# Encrypt sensitive columns
ALTER TABLE activities ADD COLUMN sensitive_data_encrypted TEXT;

UPDATE activities 
SET sensitive_data_encrypted = pgp_sym_encrypt(sensitive_data, 'encryption-key')
WHERE sensitive_data IS NOT NULL;
```

---

## 🔐 API Security

### Request Signing

All external API calls should include HMAC signature verification:

```python
import hmac
import hashlib

# Client side - sending request
def sign_request(data, secret):
    signature = hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

# Server side - verifying
def verify_signature(data, signature, secret):
    expected = hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### API Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    key_func=lambda: request.remote_addr,
    storage_uri="memory://"
)

@api_app.route('/api/v1/activity', methods=['POST'])
@limiter.limit("100 per hour")
def create_activity():
    pass
```

### CORS Configuration

```python
from flask_cors import CORS

CORS(api_app, 
     origins=['https://your-domain.com'],
     methods=['GET', 'POST'],
     allow_headers=['Content-Type', 'X-Signature']
)
```

---

## 🤖 Bot Security

### Token Protection

```bash
# ❌ NEVER commit token
git add .env
echo ".env" >> .gitignore

# ✅ Use environment variables only
export TELEGRAM_BOT_TOKEN="your_token"

# ✅ Verify in code
if not os.getenv('TELEGRAM_BOT_TOKEN'):
    raise ValueError("Missing TELEGRAM_BOT_TOKEN")
```

### Command Access Control

```python
# Restrict admin commands
async def admin_only(update, context):
    user_id = update.effective_user.id
    admin_ids = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',')]
    
    if user_id not in admin_ids:
        await update.message.reply_text("❌ Unauthorized")
        return False
    return True

async def delete_activity(update, context):
    if not await admin_only(update, context):
        return
    # Admin action...
```

### Input Validation

```python
# Validate all user inputs
from pydantic import BaseModel, validator

class ActivityInput(BaseModel):
    category: str
    description: str
    location: str
    severity: str = 'low'
    
    @validator('category')
    def validate_category(cls, v):
        allowed = ['incident', 'event', 'announcement', 'traffic', 
                   'service', 'emergency', 'weather', 'other']
        if v not in allowed:
            raise ValueError(f'Invalid category: {v}')
        return v
    
    @validator('description')
    def validate_description(cls, v):
        if len(v) < 10 or len(v) > 500:
            raise ValueError('Description must be 10-500 chars')
        return v
```

---

## 🗄️ Database Security

### Connection Security

```python
# SQLAlchemy with SSL
DATABASE_URL = "postgresql+psycopg2://user:pass@host:5432/db"

# Add SSL mode
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require",
        "sslcert": "/path/to/client-cert.pem",
        "sslkey": "/path/to/client-key.pem",
        "sslrootcert": "/path/to/server-ca.pem"
    }
)
```

### SQL Injection Prevention

```python
# ✅ Use parameterized queries (SQLAlchemy does this)
query = session.query(Activity).filter(
    Activity.location == user_input  # Parameterized!
)

# ❌ NEVER use string formatting
# query = f"SELECT * FROM activities WHERE location = '{user_input}'"
```

### Access Control

```sql
-- Create read-only user for API
CREATE ROLE api_read_only;
GRANT CONNECT ON DATABASE activities TO api_read_only;
GRANT USAGE ON SCHEMA public TO api_read_only;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO api_read_only;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO api_read_only;

-- Create application user with limited privileges
CREATE ROLE app_user WITH PASSWORD 'strong_password';
GRANT app_user TO app_role;
```

---

## 📋 Logging & Monitoring

### Secure Logging

```python
import logging
import logging.handlers

# Don't log sensitive data
logger = logging.getLogger(__name__)

# ✅ Good: Log only necessary info
logger.info(f"Activity created by user_id={user_id}")

# ❌ Bad: Logging sensitive data
logger.info(f"Report from {username} with location {location}")

# Setup file logging with rotation
handler = logging.handlers.RotatingFileHandler(
    'bot.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

### Audit Logging

```python
class AuditLog(Base):
    """Track important system events"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    action = Column(String(100), nullable=False)
    user_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String(500))
    ip_address = Column(String(45))
    
def log_audit(action, user_id, details, ip_address):
    session = get_session()
    log = AuditLog(
        action=action,
        user_id=user_id,
        details=details,
        ip_address=ip_address
    )
    session.add(log)
    session.commit()
```

### Monitoring Alerts

```python
# Alert on suspicious activity
def check_suspicious_activity():
    # Multiple failed reports from same IP
    failed = get_failed_reports_by_ip(limit_hours=1)
    for ip, count in failed:
        if count > 10:
            logger.warning(f"Suspicious activity from IP: {ip}")
            # Send alert to admins
```

---

## 🌐 Network Security

### HTTPS/TLS

```python
# Railway auto-enables HTTPS
# Redirect HTTP to HTTPS
from flask import redirect, request

@api_app.before_request
def https_redirect():
    if not request.is_secure and os.getenv('ENVIRONMENT') == 'production':
        return redirect(request.url.replace('http://', 'https://', 1))
```

### CORS Headers

```python
# Secure CORS configuration
@api_app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

---

## 🔄 Secrets Management

### Rotation Strategy

```bash
# Monthly secret rotation
# 1. Generate new secret
NEW_SECRET=$(openssl rand -hex 32)

# 2. Update in Railway
railway env NEW_SECRET=$NEW_SECRET

# 3. Deploy
railway up

# 4. Revoke old secret after deployment
# 5. Document in security log
```

### Environment Variable Handling

```python
# Load with validation
import os
from dotenv import load_dotenv

load_dotenv()

REQUIRED_VARS = [
    'TELEGRAM_BOT_TOKEN',
    'REPORT_CHANNEL_ID',
    'API_SECRET',
    'DATABASE_URL'
]

for var in REQUIRED_VARS:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required env var: {var}")
```

---

## 👤 Authentication & Authorization

### User Roles

```python
class UserRole(Enum):
    CITIZEN = "citizen"      # Report activities
    MODERATOR = "moderator"  # Approve reports
    ADMIN = "admin"          # Full access

# Role-based access control
def require_role(*roles):
    def decorator(func):
        async def wrapper(update, context, *args, **kwargs):
            user_role = get_user_role(update.effective_user.id)
            if user_role not in roles:
                await update.message.reply_text("❌ Insufficient permissions")
                return
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

@require_role(UserRole.ADMIN)
async def delete_activity(update, context):
    # Admin-only action
    pass
```

---

## 📱 Telegram Security

### Bot Permissions

Only request necessary Telegram permissions:

```python
# Minimal required permissions
# - Read messages
# - Send messages
# - Access user ID
# - NO access to user phone
# - NO access to user location (unless needed)
```

### Webhook Security (If Using)

```python
# Verify Telegram signature
import hashlib
import hmac

def verify_telegram_webhook(data, signature):
    secret = hashlib.sha256(
        os.getenv('TELEGRAM_BOT_TOKEN').encode()
    ).digest()
    
    hash_obj = hmac.new(secret, data, hashlib.sha256)
    expected = hash_obj.hexdigest()
    
    return hmac.compare_digest(expected, signature)
```

---

## 🧪 Security Testing

### OWASP Top 10 Checks

```python
# 1. Injection - Use parameterized queries ✓
# 2. Authentication - Role-based access ✓
# 3. Sensitive Data - Encrypt at rest ✓
# 4. XML External Entities - Not applicable
# 5. Broken Access Control - Use decorators ✓
# 6. Security Misconfiguration - Review SECURITY.md ✓
# 7. XSS - Use template escaping ✓
# 8. Insecure Deserialization - Validate input ✓
# 9. Using Components with Vulnerabilities - Keep deps updated ✓
# 10. Insufficient Logging - Audit logs ✓
```

### Dependency Auditing

```bash
# Check for vulnerable packages
pip install safety
safety check

# Or use pip audit (Python 3.9+)
pip install pip-audit
pip-audit
```

---

## 🚨 Incident Response

### Security Incident Checklist

1. **Detect** - Monitor logs and alerts
2. **Contain** - Disable affected service/user
3. **Investigate** - Review audit logs
4. **Remediate** - Fix vulnerability
5. **Document** - Record incident details
6. **Notify** - Inform affected users

### Emergency Access

```python
# Revoke all access in case of breach
def emergency_lockdown():
    # Clear all active sessions
    # Reset all API keys
    # Disable all webhooks
    # Notify administrators
    logger.critical("EMERGENCY LOCKDOWN INITIATED")
```

---

## 🔒 Deployment Checklist

Before production deployment:

- [ ] All secrets in environment variables
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Input validation implemented
- [ ] Audit logging enabled
- [ ] Database backups configured
- [ ] Monitoring alerts set up
- [ ] Security headers added
- [ ] CORS properly configured
- [ ] Dependencies audited
- [ ] Admin credentials changed
- [ ] API signatures enabled
- [ ] Logging configured (no sensitive data)
- [ ] Database encryption enabled
- [ ] SSH keys for deployment
- [ ] DDoS protection (Railway provides this)

---

## 📚 Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/sql-security.html)
- [Telegram Bot Security](https://core.telegram.org/bots/api#getme)
- [Flask Security](https://flask.palletsprojects.com/en/2.3.x/security/)

---

## 📞 Report Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. Email: security@yourdomain.com with details
3. Include: vulnerability description, impact, reproduction steps
4. Allow 48 hours for acknowledgment

---

**Last Updated:** 2024-01-15
**Version:** 1.0
**Maintained By:** Security Team
