# ⚡ Quick Start Guide

Get the District Activity Bot running in 5 minutes!

---

## Option 1: Local Development (Fastest)

### Step 1: Clone & Setup (1 min)

```bash
# Navigate to project directory
cd "C:\Users\ZOI\Desktop\CAT-HORNET\SiddipetBot\Siddipet (Telegram Bot)"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure (1 min)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values:
# TELEGRAM_BOT_TOKEN=<from_BotFather>
# REPORT_CHANNEL_ID=<your_channel_id>
```

**Get Telegram Bot Token:**
1. Open Telegram
2. Chat with @BotFather
3. Send `/newbot`
4. Follow instructions
5. Copy the token

**Get Channel ID:**
1. Create a Telegram channel
2. Send any message
3. Forward to @userinfobot
4. Copy the channel ID

### Step 3: Run (1 min)

```bash
python main.py
```

**What starts:**
- 🤖 Telegram Bot (listening)
- 📊 API Server: http://localhost:5001
- 🎨 Dashboard: http://localhost:5002

### Step 4: Test (2 min)

1. **Find your bot** in Telegram
2. **Send** `/start`
3. **Click** "Report Activity"
4. **Visit** http://localhost:5002 (Dashboard)

✅ Done!

---

## Option 2: Railway (Production Deployment)

### Step 1: Prepare GitHub (2 min)

```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/siddipet-bot.git
git push -u origin main
```

### Step 2: Railway Setup (3 min)

1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose this repository
6. Railway auto-detects Python project

### Step 3: Configure Variables (1 min)

In Railway Dashboard:

```
TELEGRAM_BOT_TOKEN = your_token
REPORT_CHANNEL_ID = -1001234567890
API_SECRET = generate-random-secret-here
ENVIRONMENT = production
```

### Step 4: Deploy (2 min)

1. Click "Deploy"
2. Wait for build & deployment
3. Check "Logs" tab
4. Bot should be active!

**Access:**
- 🤖 Bot: Telegram (@your_bot)
- 📊 API: https://your-app.railway.app/api/v1
- 🎨 Dashboard: https://your-app.railway.app

✅ Done!

---

## Troubleshooting

### "Bot not responding"
```bash
# Check logs
tail -f bot.log

# Verify token
echo $TELEGRAM_BOT_TOKEN

# Test Telegram API
curl https://api.telegram.org/botYOUR_TOKEN/getMe
```

### "Database connection failed"
```bash
# Check .env DATABASE_URL
# SQLite (local): sqlite:///activities.db
# PostgreSQL (prod): postgresql://user:pass@host/db

# Test local SQLite
python -c "from database import init_db; init_db()"
```

### "Port already in use"
```bash
# Change ports in .env
API_PORT=5001
DASHBOARD_PORT=5002

# Or kill process using port
lsof -i :5001  # Find process
kill -9 PID    # Kill it
```

### "Import errors"
```bash
# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

## Common Commands

### Telegram Bot

| Command | Action |
|---------|--------|
| `/start` | Initialize bot |
| `/report` | Report activity |
| `/stats` | View statistics |
| `/recent` | Recent activities |
| `/help` | Show help |

### API (curl examples)

```bash
# Create activity
curl -X POST http://localhost:5001/api/v1/activity \
  -H "Content-Type: application/json" \
  -d '{
    "category": "incident",
    "description": "Test incident",
    "location": "Main Street",
    "severity": "high"
  }'

# Get activities
curl http://localhost:5001/api/v1/activities?limit=10

# Get stats
curl http://localhost:5001/api/v1/stats
```


---

## File Guide

| File | Purpose |
|------|---------|
| `main.py` | Entry point |
| `bot.py` | Telegram bot logic |
| `database.py` | Database models |
| `api_handler.py` | REST API |
| `dashboard.py` | Web dashboard |
| `reporter.py` | Report generation |
| `.env.example` | Environment template |
| `requirements.txt` | Python dependencies |
| `docker-compose.yml` | Docker setup |
| `README.md` | Full documentation |
| `DEPLOYMENT.md` | Deployment guide |
| `SECURITY.md` | Security guidelines |

---

## Next Steps

1. **Customize bot** - Edit ACTIVITY_CATEGORIES in bot.py
2. **Add webhooks** - Integrate external systems via API
3. **Create dashboard** - Custom filters and visualizations
4. **Set up monitoring** - Configure alerts
5. **Deploy to production** - Railway or Docker

---

## Support

- 📚 **Full Docs**: See README.md
- 🚀 **Deployment**: See DEPLOYMENT.md
- 🔒 **Security**: See SECURITY.md
- 🤖 **Telegram API**: https://core.telegram.org/bots/api
- 🚄 **Railway Docs**: https://docs.railway.app

---

**Need help?** Check the docs or see troubleshooting section above.

**Happy monitoring! 🏘️**
