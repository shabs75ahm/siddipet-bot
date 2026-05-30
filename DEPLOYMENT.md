# Deployment Guide - District Activity Monitor Bot

## Railway Platform Setup

### Prerequisites
- Railway account (https://railway.app)
- Telegram Bot Token from @BotFather
- GitHub repository with this code

### Step 1: Create Railway Project

1. Go to https://railway.app and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo" or "Deploy from template"
4. Connect your GitHub account and select this repository

### Step 2: Configure Environment Variables

In Railway project settings, add these environment variables:

**Required:**
```
TELEGRAM_BOT_TOKEN=<your_bot_token>
REPORT_CHANNEL_ID=<channel_id>
API_SECRET=<strong_random_secret>
```

**Optional:**
```
ADMIN_IDS=<comma_separated_user_ids>
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Step 3: Add PostgreSQL Plugin

1. In Railway dashboard, click "Add Plugin"
2. Select "PostgreSQL"
3. Railway will automatically set `DATABASE_URL`

### Step 4: Deploy

1. Click "Deploy" 
2. Railway will build and deploy automatically
3. Monitor deployment in the Railway dashboard

### Step 5: Verify Deployment

- Bot should connect within 30 seconds
- Check logs: `Railway Dashboard → Logs`
- Test with Telegram: `/start` command

---

## Local Development Setup

### Prerequisites
- Python 3.8+
- SQLite3
- pip

### Installation

```bash
# Clone repository
git clone <repo_url>
cd Siddipet-Telegram-Bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

### Configuration

Edit `.env` with your values:

```env
TELEGRAM_BOT_TOKEN=your_token_here
REPORT_CHANNEL_ID=-1001234567890
ADMIN_IDS=123456789
```

### Run Locally

```bash
python main.py
```

This will start:
- **Telegram Bot**: Listening for updates
- **API Server**: `http://localhost:5001`
- **Dashboard**: `http://localhost:5002`

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Telegram Bot (main.py)          │
├─────────────────────────────────────────┤
│  • Real-time message handling           │
│  • Activity collection                  │
│  • Alert dispatch                       │
│  • Periodic reports (hourly/daily)      │
└────────────┬────────────────────────────┘
             │
      ┌──────┴──────┐
      ▼             ▼
┌──────────┐  ┌──────────┐
│  Flask   │  │  Flask   │
│   API    │  │Dashboard │
│ (5001)   │  │ (5002)   │
└────┬─────┘  └─────┬────┘
     │              │
     └──────┬───────┘
            ▼
      ┌──────────────┐
      │  PostgreSQL  │
      │  Database    │
      └──────────────┘
```

---

## API Endpoints

### Activity Management

**Create Activity**
```bash
POST /api/v1/activity
{
  "category": "incident",
  "description": "Traffic accident",
  "location": "Main Street",
  "severity": "high",
  "latitude": 17.3569,
  "longitude": 78.4789
}
```

**List Activities**
```bash
GET /api/v1/activities?limit=50&hours=24&severity=high
```

**Get Activity Details**
```bash
GET /api/v1/activity/{id}
```

**Update Status**
```bash
POST /api/v1/activity/{id}/update
{
  "status": "resolved"
}
```

### Statistics

**Get Stats**
```bash
GET /api/v1/stats?hours=24
```

### Webhooks

**Traffic Updates**
```bash
POST /api/v1/webhook/traffic
{
  "location": "City Center",
  "description": "Heavy traffic on Main Rd",
  "severity": "medium"
}
```

**Weather Alerts**
```bash
POST /api/v1/webhook/weather
{
  "location": "District-wide",
  "description": "Heavy rainfall expected",
  "severity": "high"
}
```

**Emergency Reports**
```bash
POST /api/v1/webhook/incident
{
  "location": "Hospital Road",
  "description": "Medical emergency",
  "severity": "critical"
}
```

---

## Monitoring & Logs

### Railway Logs
```bash
# View real-time logs
railway logs -f

# Download logs
railway logs > bot.log
```

### Local Logs
Logs are saved to `bot.log` in the project directory.

### Health Check
```bash
curl https://your-app.railway.app/api/v1/health
```

---

## Troubleshooting

### Bot Not Responding
1. Check `TELEGRAM_BOT_TOKEN` is correct
2. Verify bot is polling: Check logs for "polling updates"
3. Restart: `railway up` or manually restart from dashboard

### Database Connection Failed
1. Verify `DATABASE_URL` format
2. Check PostgreSQL is running
3. Test connection: `psql $DATABASE_URL`

### High Memory/CPU Usage
1. Check activity count in database
2. Archive old activities: `UPDATE activities SET status='archived' WHERE created_at < ...`
3. Optimize queries in database.py

### API Returns 500 Error
1. Check logs for exception details
2. Verify database is accessible
3. Check required fields in request body

---

## Security Checklist

- [ ] Change `API_SECRET` to strong random value
- [ ] Set `TELEGRAM_BOT_TOKEN` from environment variable only
- [ ] Enable request signature verification for API
- [ ] Use HTTPS for dashboard (Railway provides this)
- [ ] Restrict admin access with `ADMIN_IDS`
- [ ] Regular database backups (Railway handles this)
- [ ] Monitor suspicious activity patterns
- [ ] Rotate secrets monthly

---

## Scaling & Performance

### Database Optimization
- Add indexes on frequently queried fields (done in models)
- Archive activities older than 90 days
- Use connection pooling (SQLAlchemy handles this)

### API Performance
- Cache statistics (TTL: 5 minutes)
- Paginate activity lists (limit: 100)
- Use database query limits

### Bot Performance
- Batch report generation
- Async message handling
- Connection pooling

---

## Maintenance

### Weekly Tasks
- Check error logs
- Monitor active users
- Review critical incidents

### Monthly Tasks
- Archive old activities
- Rotate API secrets
- Update dependencies: `pip list --outdated`

### Quarterly Tasks
- Security audit
- Database optimization
- Performance review

---

## Support & Issues

For issues, check:
1. Railway documentation: https://docs.railway.app
2. Telegram Bot API: https://core.telegram.org/bots/api
3. SQLAlchemy docs: https://docs.sqlalchemy.org

---

## License
MIT License - See LICENSE file
