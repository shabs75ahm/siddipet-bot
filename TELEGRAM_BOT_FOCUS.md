# 🤖 Telegram Bot - Primary Interface

## ⚠️ IMPORTANT: This is a Telegram Bot

**The Telegram Bot is the PRIMARY interface** for the entire District Activity Monitoring system. Everything else (scrapers, API, dashboard) exists to support the bot.

---

## 🎯 How Everything Works Together

```
TELEGRAM BOT (Primary Interface)
    ↓
    ├─ Users report activities via /report
    ├─ Scrapers automatically feed data via scheduler
    ├─ Reporter generates hourly/daily summaries
    └─ All goes to: DATABASE
             ↓
         (Central Hub)
             ↓
    ┌────────┴────────┬─────────────┐
    ↓                 ↓             ↓
Telegram        REST API         Dashboard
(Bot/Channel)   (External)        (Web UI)
```

---

## 📱 Telegram Bot Features

### User Commands

```
/start              → Show main menu
/report             → Report an activity
/stats              → View district statistics  
/recent             → See latest activities
/help               → Display help

Inline Buttons:
  📝 Report Activity
  📊 View Stats
  📋 Recent Activities
  ℹ️ Help
```

### How Scraped Data Flows to Telegram

```
1. Scheduler triggers every 30 minutes
   ↓
2. Scrapers collect data from:
   - Newspapers (Eenadu, Hindu, TOI)
   - Twitter/X trends
   - Google Trends
   - YouTube
   ↓
3. Data is categorized & severity checked
   ↓
4. Data added to database as "Activities"
   ↓
5. Critical/High severity → BROADCAST TO TELEGRAM CHANNEL
   (Automatic alert sent immediately)
   ↓
6. User sees in /recent command
   ↓
7. Included in /stats command
   ↓
8. Part of hourly/daily reports
```

---

## 🔔 Real-Time Telegram Alerts

### What Gets Broadcast Immediately

**Critical Items** 🔴
```
🚨 CRITICAL ALERT

Source: Eenadu
Category: EMERGENCY
Title: Fire breaks out at warehouse in Siddipet

⚠️ Please take necessary action
```

**High Severity Items** 🟠
```
🔴 HIGH SEVERITY

Source: Twitter
Category: TRAFFIC
Title: Major accident reported on Hyderabad bypass

Location: Hyderabad
Reported: Just now
```

### Hourly Report to Telegram Channel

```
📊 Hourly Activity Report
⏰ 2024-01-15 14:00 UTC
━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
• Total Activities: 47
• Incidents: 12
• Traffic: 8
• Emergencies: 2

By Category:
  🚨 Incident: 12
  🚗 Traffic: 8
  🎉 Event: 15
  📢 Announcement: 12

🔴 Critical/High Severity (5):
  🔴 Emergency @ Hospital Road
  🔴 Traffic accident @ Bypass
  🔴 Fire @ Industrial area
  ...

💡 Use `/recent` to see all activities
```

### Daily Summary to Telegram Channel

```
📋 Daily Activity Summary
📅 2024-01-15 UTC
━━━━━━━━━━━━━━━━━━━━━━━

Overview:
• Total Activities: 847
• Incidents: 234
• Events: 156
• Emergencies: 47

Distribution:
█████░░░░ Incidents (27.6%)
████░░░░░ Events (18.4%)
███████░░ Traffic (32.5%)
██░░░░░░░ Announcements (21.5%)

Critical Incidents:
1. Fire @ Warehouse - Siddipet
2. Multi-vehicle collision - Hyderabad
3. Medical emergency - Hospital Road

Top Active Areas:
1. Main Street: 45 activities
2. Downtown: 38 activities
3. Airport Road: 32 activities

Insights:
⚠️ High critical incident rate
📍 Focus on Main Street area
📊 Traffic incidents up 15%
```

---

## 👥 User Workflow

### 1️⃣ Citizen Reports Activity via Telegram

```
User: /report
Bot: Select category
User: Selects "Incident"
User: Types "Traffic accident on Siddipet bypass"
Bot: ✅ Activity recorded!
     Category: Traffic
     Location: Siddipet
     Severity: High

→ Alert sent to report channel immediately
→ Activity visible to all users via /recent
```

### 2️⃣ Scrapers Feed Data Automatically

```
08:30 AM - News scraper runs
         - Collects from Eenadu, Hindu, TOI
         - Finds 15 new articles
         - Categorizes as incidents/events/announcements
         - Adds to database

09:00 AM - Twitter trends checked
         - Scrapes #Siddipet, #Telangana
         - Finds 12 trending tweets
         - Checks for emergencies/traffic

09:30 AM - News scraper runs again
         - Continues monitoring

→ All data feeds into same bot system
→ Users see combined data via /recent
```

### 3️⃣ User Views Stats via Telegram

```
User: /stats
Bot: Shows 24-hour statistics
     • Total Activities: 847
     • Critical: 5
     • High: 23
     • By Category: ...
     • Top Areas: ...

All data includes:
  ✅ User reports
  ✅ Scraped news
  ✅ Twitter updates
  ✅ Trends data
```

### 4️⃣ Reports Auto-Generated

```
Every Hour (Top of hour):
- Reporter generates hourly summary
- Sends to REPORT_CHANNEL_ID (Telegram channel)
- Shows last 60 minutes of activities

Every Day (8:00 AM):
- Reporter generates daily summary
- Sends to REPORT_CHANNEL_ID
- Shows last 24 hours of activities
```

---

## 🔗 Data Integration Points

### Scrapers → Database → Telegram Bot

```python
# scrapers.py
activity = add_activity(
    category='incident',           # from news content
    description='Article title',   # from scraper
    location='Siddipet',          # extracted
    severity='high',              # auto-determined
    reported_by='Eenadu',         # source name
    reporter_id=0                 # system reporter
)

# Result: Activity in database

# bot.py - User Command
async def show_recent(update, context):
    activities = get_activities(limit=10)
    # Shows BOTH:
    # - User-reported activities
    # - Scraped activities
```

### Real-Time Alert Flow

```python
# scrapers.py - After adding activity
if activity.severity in ['high', 'critical']:
    await _broadcast_alert(activity)

# _broadcast_alert() sends to Telegram channel
await self.app.bot.send_message(
    chat_id=self.report_channel_id,
    text=alert_message,
    parse_mode='Markdown'
)

# Telegram channel receives instant alert
# All subscribers see it
```

---

## 📋 Complete Data Sources for Telegram Users

### Via /recent Command
Users see activities from:
- ✅ Direct Telegram reports (/report)
- ✅ Eenadu news scraper
- ✅ The Hindu newspaper
- ✅ Times of India
- ✅ Deccan Chronicle
- ✅ Twitter/X trending
- ✅ Google Trends
- ✅ YouTube videos
- ✅ Reddit discussions
- ✅ Facebook pages

### Via /stats Command
Statistics include:
- ✅ Total count from all sources
- ✅ Category breakdown (all sources)
- ✅ Severity distribution
- ✅ Top active areas
- ✅ Trending topics

### Via Hourly Reports
Telegram channel receives:
- ✅ Latest activities (all sources)
- ✅ Critical incidents
- ✅ Top active areas
- ✅ Trends summary

---

## 🎯 Primary User Interactions

### Main Interface: Telegram Bot

**Users interact ONLY with Telegram:**
- Send /report → creates activity
- Send /stats → sees aggregated data
- Send /recent → sees all activities
- Receive alerts → real-time notifications
- Receive reports → hourly/daily summaries

**Users DO NOT need:**
- REST API (internal use only)
- Dashboard (optional monitoring)
- Database access (managed by bot)

---

## 🚀 Deployment Flow

```
1. User starts bot: python main.py

2. What starts:
   ✅ Telegram Bot
      └─ Listening for /start, /report, /stats, /help
      └─ Ready to broadcast alerts
      └─ Connected to database
   
   ✅ Scheduler
      └─ Starts scraper jobs
      └─ Feeds data to database
      └─ Bot broadcasts alerts
      └─ Bot sends hourly/daily reports
   
   ✅ Flask API (background)
      └─ For external integrations
      └─ Optional, bot-independent
   
   ✅ Dashboard (background)
      └─ For monitoring
      └─ Optional, bot-independent

3. Telegram Channel
   ├─ Receives alerts (critical/high severity)
   ├─ Receives hourly reports (8:00 AM)
   ├─ Receives daily summaries (each day)
   └─ All users subscribed see updates
```

---

## 📱 Telegram Channel Setup

### Create Monitoring Channel

```bash
1. Open Telegram
2. Create new channel: "Siddipet Activity Monitor"
3. Get channel ID: @userinfobot → forward a message
4. Note the negative channel ID: -1001234567890
5. Add to .env: REPORT_CHANNEL_ID=-1001234567890
6. Restart bot
```

### What Happens in Channel

```
Channel Members Receive:
├─ 🚨 Real-time critical alerts (immediate)
├─ 🟠 High severity incident alerts
├─ 📊 Hourly summaries (top of every hour)
├─ 📋 Daily digest (8:00 AM)
├─ 📈 Trending topics
└─ 🔴 Health check status
```

---

## ✅ Verification Checklist

Before deployment, verify:

- [ ] TELEGRAM_BOT_TOKEN is set in .env
- [ ] REPORT_CHANNEL_ID is set in .env
- [ ] Bot responds to /start
- [ ] /report command works
- [ ] /stats shows data
- [ ] Scrapers running (check logs)
- [ ] Data appearing in database
- [ ] Alerts being sent to Telegram channel
- [ ] Hourly reports arriving
- [ ] Dashboard accessible (optional)
- [ ] API endpoints working (optional)

---

## 🎯 System Architecture (Telegram-Focused)

```
                    ┌──────────────────────────┐
                    │   Telegram Users         │
                    │                          │
                    │  /start, /report,       │
                    │  /stats, /recent        │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │  TELEGRAM BOT            │ ← PRIMARY
                    │  (bot.py)               │
                    │                          │
                    │  • Handle commands      │
                    │  • Broadcast alerts     │
                    │  • Send reports         │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │  DATABASE               │
                    │  (SQLAlchemy ORM)       │
                    │                          │
                    │  Activities table       │
                    │  Updates table          │
                    └────────┬────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  Scrapers   │  │  Reporter   │  │ API/Dashboard
    │ (Optional)  │  │ (Optional)  │  │ (Optional)
    └─────────────┘  └─────────────┘  └─────────────┘
         │                 │
         │ Feed data       │ Generate reports
         │                 │
         └─────────┬───────┘
                   │
                   ▼
         Telegram Channel
       (Alerts & Reports)
```

---

## 🔴 REMEMBER

**THIS IS A TELEGRAM BOT**

- ✅ Primary interface: Telegram
- ✅ Primary user interaction: /report command
- ✅ Primary alert method: Telegram channel
- ✅ Primary monitoring: Telegram commands
- ✅ Everything feeds INTO the bot
- ✅ Nothing requires leaving Telegram

**Scrapers, API, Dashboard are just SUPPORTING SYSTEMS**

---

## 🚀 Quick Start (Telegram Focus)

```bash
# 1. Setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env with:
#   TELEGRAM_BOT_TOKEN=your_token
#   REPORT_CHANNEL_ID=-1001234567890

# 2. Start
python main.py

# 3. Use on Telegram
#    - Find your bot
#    - /start
#    - /report
#    - /stats
#    - Receive alerts in channel
```

**That's it! Everything else is automatic.** ✅

---

**The Telegram Bot is the heart of this system.** 💚
