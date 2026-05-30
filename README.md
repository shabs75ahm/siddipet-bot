# 🏘️ District Activity Monitoring Bot

Real-time collection and reporting of district-wide activities across multiple data sources with intelligent alerts, analytics dashboard, and periodic summaries.

## ✨ Features

### Core Functionality
- **🤖 Telegram Bot**: Intuitive interface for real-time activity reporting
- **📊 Live Dashboard**: Web-based analytics and activity visualization
- **🚨 Real-time Alerts**: Instant notifications for critical incidents
- **📈 Analytics**: 24-hour trends, severity distribution, top active areas
- **📋 Periodic Reports**: Hourly summaries and daily digests
- **🔌 REST API**: External system integration via webhooks

### Activity Categories
- 🚨 Incidents
- 🎉 Events
- 📢 Announcements
- 🚗 Traffic Updates
- 🔧 Service Requests
- 🆘 Emergencies
- 🌤️ Weather Alerts
- 📌 General Updates

### Severity Levels
- 🟢 Low
- 🟡 Medium
- 🔴 High
- ⛔ Critical

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from @BotFather)
- PostgreSQL (for production) or SQLite (for development)

### Installation

```bash
# Clone repository
git clone <repo_url>
cd Siddipet-Telegram-Bot

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

Edit `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
REPORT_CHANNEL_ID=-1001234567890
ADMIN_IDS=123456789,987654321
API_SECRET=strong-secret-key
```

### Run Locally

```bash
python main.py
```

**Services:**
- **Telegram Bot**: Active and ready
- **API**: http://localhost:5001
- **Dashboard**: http://localhost:5002

---

## 📱 Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize bot and see main menu |
| `/report` | Report a new activity |
| `/stats` | View district statistics |
| `/recent` | Show recent activities (last 10) |
| `/help` | Display help message |

### Reporting Activities

1. Click "📝 Report Activity"
2. Select category (Incident, Event, etc.)
3. Provide:
   - Location
   - Description
   - Severity level (for incidents)
4. Submit

**Alerts:** High and critical severity activities are automatically broadcast to the reporting channel.

---

## 📊 Dashboard Features

Access at `http://localhost:5002`

### Real-time Stats
- Total activities (24h)
- Incident count
- Critical/High severity count

### Visualizations
- **Category Distribution**: Doughnut chart
- **Severity Levels**: Bar chart
- **Top Active Areas**: Horizontal bar chart
- **24-Hour Trend**: Line chart

### Activity Feed
- Latest 20 activities
- Filterable by category/severity
- Includes location, time, and reporter info

### Auto-Refresh
Dashboard updates every 30 seconds automatically.

---

## 🔌 API Documentation

### Base URL
```
http://localhost:5001/api/v1
```

### Create Activity

**POST** `/activity`

```json
{
  "category": "incident",
  "description": "Traffic collision at intersection",
  "location": "Main St & 5th Ave",
  "severity": "high",
  "reported_by": "User Name",
  "latitude": 17.3569,
  "longitude": 78.4789
}
```

**Response:**
```json
{
  "success": true,
  "activity_id": 123,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### List Activities

**GET** `/activities?limit=50&hours=24&severity=high`

```json
{
  "success": true,
  "count": 45,
  "activities": [
    {
      "id": 123,
      "category": "incident",
      "description": "Traffic collision...",
      "location": "Main St & 5th Ave",
      "severity": "high",
      "created_at": "2024-01-15T10:30:00Z",
      "view_count": 25
    }
  ]
}
```

### Get Statistics

**GET** `/stats?hours=24`

```json
{
  "success": true,
  "stats": {
    "total_24h": 45,
    "incidents_24h": 12,
    "emergencies_24h": 3,
    "severity_24h": {
      "critical": 2,
      "high": 8,
      "medium": 15,
      "low": 20
    },
    "top_areas": [
      ["Main Street", 15],
      ["Downtown", 12],
      ["Airport Road", 8]
    ]
  }
}
```

### Webhooks

**Traffic Update**
```bash
POST /webhook/traffic
{
  "location": "Highway 101",
  "description": "Heavy traffic due to accident",
  "severity": "medium"
}
```

**Weather Alert**
```bash
POST /webhook/weather
{
  "location": "District-wide",
  "description": "Heavy rainfall expected",
  "severity": "high"
}
```

**Emergency Report**
```bash
POST /webhook/incident
{
  "location": "Hospital Road",
  "description": "Medical emergency call",
  "severity": "critical"
}
```

---

## 📦 Deployment

### Railway Platform (Recommended)

1. **Setup Railway Project**
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli
   
   # Login
   railway login
   ```

2. **Deploy**
   ```bash
   railway up
   ```

3. **Configure Environment Variables** in Railway Dashboard:
   - `TELEGRAM_BOT_TOKEN`
   - `REPORT_CHANNEL_ID`
   - `API_SECRET`
   - Database auto-configured

4. **Access Deployed Services**
   - Bot: Automatically active
   - API: `https://your-app.railway.app/api/v1`
   - Dashboard: `https://your-app.railway.app/`

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## 🏗️ Project Structure

```
.
├── main.py                 # Entry point - runs bot + Flask apps
├── bot.py                  # Telegram bot logic
├── database.py             # SQLAlchemy models & ORM
├── reporter.py             # Report generation
├── api_handler.py          # REST API & webhooks
├── dashboard.py            # Web dashboard
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── railway.json           # Railway deployment config
├── Procfile               # Process definitions
├── DEPLOYMENT.md          # Deployment guide
└── README.md              # This file
```

---

## 🔒 Security

### Best Practices
1. **Environment Variables**: Never commit secrets to git
2. **API Signatures**: Verify webhook requests with HMAC-SHA256
3. **Database**: Use PostgreSQL with strong credentials
4. **Admin Access**: Restrict with `ADMIN_IDS`
5. **HTTPS**: Railway provides automatic SSL/TLS

### API Security Headers
```
X-Signature: hmac-sha256 signature for verification
Authorization: Bearer token (future implementation)
```

---

## 📈 Performance

### Optimization Tips
- Database indexes on frequently queried fields
- Activity archiving for old records
- Caching of statistics (5-minute TTL)
- Async message processing
- Connection pooling

### Typical Capacity
- **Activities/day**: 10,000+
- **Concurrent users**: 100+
- **API RPS**: 1,000+
- **Dashboard refresh**: 30 seconds

---

## 🐛 Troubleshooting

### Bot Not Responding
```bash
# Check logs
tail -f bot.log

# Verify token
echo $TELEGRAM_BOT_TOKEN

# Test API endpoint
curl https://api.telegram.org/bot$TOKEN/getMe
```

### Database Connection Error
```bash
# Test PostgreSQL connection
psql $DATABASE_URL

# Check connection string format
# postgresql://user:password@host:5432/dbname
```

### High Memory Usage
```bash
# Archive old activities
DELETE FROM activities WHERE created_at < NOW() - INTERVAL '90 days'

# Check active connections
SELECT * FROM pg_stat_activity;
```

---

## 📚 Technologies

- **Bot Framework**: python-telegram-bot
- **Web Framework**: Flask
- **Database**: SQLAlchemy + PostgreSQL
- **Frontend**: Vanilla JS + Chart.js
- **Hosting**: Railway Platform
- **Async**: asyncio + threading

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 📞 Support

For issues and questions:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md) for setup help
2. Review [Telegram Bot API](https://core.telegram.org/bots/api) documentation
3. Check Railway [documentation](https://docs.railway.app)

---

## 🎯 Future Enhancements

- [ ] Map-based activity visualization
- [ ] Machine learning for anomaly detection
- [ ] Multi-language support
- [ ] Mobile app (iOS/Android)
- [ ] Integration with emergency services
- [ ] Predictive analytics
- [ ] Community rating system
- [ ] Photo/video attachments

---

**Made with ❤️ for real-time district monitoring**
#   s i d d i p e t - b o t  
 #   s i d d i p e t - b o t  
 