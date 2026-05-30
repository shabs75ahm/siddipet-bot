# 🔗 Scraper Integration Guide

## Overview

The multi-source scraper system is fully integrated with the District Activity Monitor Bot. Data from newspapers, social media, and trends feeds automatically into the system.

---

## 🏗️ Architecture

### Component Integration

```
┌──────────────────────────────────────┐
│         main.py (Entry Point)        │
├──────────────────────────────────────┤
│  • Initializes bot                   │
│  • Starts Flask servers              │
│  • Launches scheduler                │
│  • Coordinates all services          │
└────────────┬─────────────────────────┘
             │
    ┌────────┴────────┐
    ↓                 ↓
┌─────────────┐  ┌──────────────────┐
│ Telegram    │  │ Scheduler       │
│ Bot Layer   │  │ (APScheduler)   │
└─────────────┘  └────────┬─────────┘
                          │
            ┌─────────────┼─────────────┐
            ↓             ↓             ↓
      ┌──────────┐  ┌──────────┐  ┌──────────┐
      │ Scrapers │  │ Reporter │  │ Flask    │
      │(Parallel)│  │(Reports) │  │(API/Web) │
      └────┬─────┘  └──────────┘  └──────────┘
           │
           ↓
      ┌─────────────────┐
      │ Database Layer  │
      │ (SQLAlchemy)    │
      └──────┬──────────┘
             │
      ┌──────┴──────┐
      ↓             ↓
  ┌────────┐  ┌──────────┐
  │ SQLite │  │PostgreSQL│
  │ (Dev)  │  │  (Prod)  │
  └────────┘  └──────────┘
```

---

## 🔄 Data Flow

### Collection Pipeline

```
1. Scheduled Scraper Job Triggers
   ↓
2. DataAggregator.collect_all_data()
   ├─ NewsSourceScraper.scrape_all_news()
   │  ├─ scrape_eenadu()
   │  ├─ scrape_thehindu()
   │  ├─ scrape_times_of_india()
   │  └─ [Result: List of articles]
   │
   ├─ TwitterTrendScraper.scrape_twitter_trends()
   │  ├─ TwitterSearchScraper with keywords
   │  └─ [Result: List of tweets]
   │
   ├─ GoogleTrendsScraper.scrape_trends()
   │  └─ [Result: Trending searches]
   │
   └─ YouTubeScraper.scrape_youtube()
      └─ [Result: Video metadata]
   ↓
3. Data Aggregation & Deduplication
   ↓
4. Auto-Categorization (Incident/Traffic/Event/etc)
   ↓
5. Severity Determination (Low/Medium/High/Critical)
   ↓
6. Feed to Database
   ↓
7. Broadcast Alerts (if critical/high)
```

---

## 📅 Scheduling Configuration

### Default Schedule

Edit `scheduler.py` to customize:

```python
# News scraping - every 30 minutes
scheduler.schedule_interval(
    jobs.scrape_news,
    minutes=30,
    job_id='scrape_news'
)

# Trend monitoring - every 1 hour
scheduler.schedule_interval(
    jobs.check_trends,
    minutes=60,
    job_id='check_trends'
)

# Hourly report - top of every hour
scheduler.schedule_hourly(
    jobs.generate_hourly_report,
    minute=0,
    job_id='hourly_report'
)

# Daily summary - 8:00 AM
scheduler.schedule_daily(
    jobs.generate_daily_summary,
    hour=8, minute=0,
    job_id='daily_summary'
)
```

### Adjusting Intervals

```python
# Increase frequency (more real-time but higher load)
scheduler.schedule_interval(jobs.scrape_news, minutes=15)

# Decrease frequency (less load but slower updates)
scheduler.schedule_interval(jobs.scrape_news, minutes=60)

# Add new schedule
scheduler.schedule_daily(custom_job, hour=12, minute=30, job_id='noon_report')
```

---

## 🚀 Running the System

### Complete Startup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your Telegram token, channel ID, etc

# 3. Start the complete system
python main.py
```

**Services Started:**
- ✅ Telegram Bot (listening for commands)
- ✅ API Server (http://localhost:5001)
- ✅ Dashboard (http://localhost:5002)
- ✅ Scheduler (running all scraper jobs)
- ✅ Database (SQLite/PostgreSQL connected)

### Logs Output

```
2024-01-15 10:30:15 - bot - INFO - 🚀 DISTRICT ACTIVITY MONITORING BOT
2024-01-15 10:30:15 - bot - INFO - Environment: development
2024-01-15 10:30:16 - scheduler - INFO - Scheduler configured with all jobs
2024-01-15 10:30:17 - bot - INFO - 🤖 Starting Telegram Bot...
2024-01-15 10:30:18 - bot - INFO - Starting API server on port 5001...
2024-01-15 10:30:18 - bot - INFO - Starting Dashboard on port 5002...
2024-01-15 10:30:20 - scheduler - INFO - ✅ API available at: http://0.0.0.0:5001
2024-01-15 10:30:20 - scheduler - INFO - ✅ Dashboard available at: http://0.0.0.0:5002
2024-01-15 10:30:45 - scrapers - INFO - Starting scheduled news scraping...
2024-01-15 10:30:52 - scrapers - INFO - Scraped 15 articles from Eenadu
2024-01-15 10:31:05 - scrapers - INFO - Scraped 8 articles from The Hindu
2024-01-15 10:31:18 - scrapers - INFO - News scraping complete: 23 activities added
```

---

## 🔧 Customization

### Adding Custom Scraper

```python
# 1. Create new scraper class in scrapers.py

class CustomScraper:
    async def scrape(self) -> List[Dict]:
        """Scrape custom source"""
        return [
            {
                'title': 'Article title',
                'description': 'Content',
                'source': 'Custom Source',
                'category': 'announcement',
                'timestamp': datetime.utcnow()
            }
        ]

# 2. Add to DataAggregator

async def _collect_custom(self) -> List[Dict]:
    scraper = CustomScraper()
    return await scraper.scrape()

# 3. Add to collect_all_data

tasks = [
    self._collect_news(),
    self._collect_twitter(),
    self._collect_custom()  # Add here
]

# 4. Schedule in scheduler.py

def setup_scheduler(bot_app, report_channel_id):
    # ... existing jobs ...
    
    scheduler.schedule_interval(
        jobs.scrape_custom,
        minutes=30,
        job_id='scrape_custom'
    )
```

### Modifying Categories

Edit `_categorize_news()` in `scrapers.py`:

```python
@staticmethod
def _categorize_news(title: str) -> str:
    """Categorize news based on keywords"""
    title_lower = title.lower()
    
    # Add your own categories
    if any(word in title_lower for word in ['water', 'supply', 'pipeline']):
        return 'water_supply'
    
    # ... existing categories ...
```

### Changing Severity Rules

Edit `_determine_severity()`:

```python
@staticmethod
def _determine_severity(content: str) -> str:
    """Determine severity"""
    content_lower = content.lower()
    
    # Critical
    if 'bomb' in content_lower or 'terror' in content_lower:
        return 'critical'
    
    # ... other levels ...
```

---

## 📊 Monitoring Scrapers

### Check Scraper Status

```bash
# View live scraper logs
tail -f bot.log | grep scraper

# View last 100 lines
tail -100 bot.log | grep -E "scraped|scraping|twitter|news"

# Count activities by source
grep "source" bot.log | cut -d"'" -f2 | sort | uniq -c
```

### Query Collected Data

```bash
# Connect to database
python -c "
from database import get_activities
activities = get_activities(limit=5, hours=1)
for a in activities:
    print(f'{a.created_at}: {a.source} - {a.category}')
"
```

### Check Scheduler Health

```python
# In Python shell
from scheduler import BotScheduler

scheduler = BotScheduler()
print(f"Scheduler running: {scheduler.is_running}")
for job in scheduler.scheduler.get_jobs():
    print(f"{job.id}: {job.name} (next run: {job.next_run_time})")
```

---

## 🐛 Troubleshooting

### Scrapers Not Running

**Symptom**: No new activities from scrapers

**Solutions:**
```bash
# 1. Check scheduler is started
grep "Scheduler started" bot.log

# 2. Check for scraper errors
grep ERROR bot.log | grep scraper

# 3. Verify sources are accessible
curl -I https://www.eenadu.net/

# 4. Manually test scraper
python -c "
import asyncio
from scrapers import NewsSourceScraper
scraper = NewsSourceScraper()
articles = asyncio.run(scraper.scrape_eenadu())
print(f'Got {len(articles)} articles')
"
```

### Rate Limited

**Symptom**: `429 Too Many Requests` errors

**Solutions:**
```python
# Increase intervals in scheduler.py
# From: minutes=30
# To:   minutes=60

# Add delays between requests in scrapers.py
import time
time.sleep(2)  # 2 second delay between requests

# Rotate user agents
headers = {
    'User-Agent': random.choice(USER_AGENTS_LIST)
}
```

### Memory Leaks

**Symptom**: Memory usage increases over time

**Solutions:**
```python
# Close sessions properly
session.close()

# Clear large objects
del articles
del tweets

# Reduce batch sizes
MAX_ARTICLES_PER_SOURCE = 5  # from 10

# Enable garbage collection
import gc
gc.collect()
```

### Parsing Failures

**Symptom**: `ParsingError` when site structure changes

**Solutions:**
```python
# Update CSS selectors
# Old: article = soup.find('article')
# New: article = soup.find('div', class_='news-item')

# Add error handling
try:
    title = article.find('h2').text
except AttributeError:
    title = "Title not found"
    logger.warning(f"Could not parse title from {source}")

# Test scraper independently
python scrapers.py
```

---

## 🔐 Security Considerations

### API Rate Limiting

```python
# News sites expect 1 req/minute
import time
time.sleep(60)  # Between requests

# Twitter/snscrape (respectful scraping)
# No API key needed, but respect rate limits

# Google Trends
# Free API, no auth needed, 1 req/min recommended
```

### User Agent

```python
# Identify your bot properly
headers = {
    'User-Agent': 'DistrictActivityMonitorBot/1.0 (+http://your-domain/)'
}
```

### Robots.txt Compliance

```python
# Check and respect robots.txt
from urllib.robotparser import RobotFileParser

rp = RobotFileParser()
rp.set_url("https://example.com/robots.txt")
rp.read()

if rp.can_fetch("*", "https://example.com/news"):
    # Safe to scrape
    pass
else:
    # Don't scrape
    logger.warning("Scraping not allowed by robots.txt")
```

---

## 📈 Performance Optimization

### Parallel Scraping

Currently uses `asyncio.gather()` for concurrent requests:

```python
# Scrape multiple sources in parallel
results = await asyncio.gather(
    self.scrape_eenadu(),
    self.scrape_thehindu(),
    self.scrape_times_of_india(),
    return_exceptions=True
)
```

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_created_at ON activities(created_at);
CREATE INDEX idx_category ON activities(category);
CREATE INDEX idx_severity ON activities(severity);
CREATE INDEX idx_location ON activities(location);

-- Archive old records
DELETE FROM activities 
WHERE created_at < NOW() - INTERVAL '90 days'
AND status = 'archived';
```

### Caching

```python
# Cache trending data (1 hour TTL)
from functools import lru_cache
import time

@lru_cache(maxsize=10)
def get_cached_trends(ttl=3600):
    now = time.time()
    return scraper.get_trends()
```

---

## 📋 Maintenance Tasks

### Weekly
- [ ] Review scraper logs
- [ ] Check for parsing errors
- [ ] Verify data quality
- [ ] Monitor system resources

### Monthly
- [ ] Update news source selectors (if sites change)
- [ ] Archive old activities (>90 days)
- [ ] Review duplicate detection rules
- [ ] Test manual scraper runs

### Quarterly
- [ ] Add new data sources
- [ ] Optimize category rules
- [ ] Review severity determination
- [ ] Audit scraper performance

---

## 📚 Code Reference

### Key Files

| File | Purpose |
|------|---------|
| `scrapers.py` | All scraper classes (1000+ lines) |
| `scheduler.py` | Job scheduling and management |
| `database.py` | Data storage and queries |
| `reporter.py` | Report generation |
| `main.py` | Orchestrates all components |

### Key Classes

- `DataAggregator` - Main orchestrator
- `NewsSourceScraper` - Newspaper scraping
- `TwitterTrendScraper` - Twitter/X data
- `GoogleTrendsScraper` - Trends data
- `BotScheduler` - Job scheduling
- `ScraperJobs` - Scheduled tasks

---

## 🚀 Deployment Notes

### Railway Deployment

Scrapers run automatically after deployment:

```bash
# 1. Push to GitHub
git push origin main

# 2. Railway auto-deploys
# 3. Scheduler starts automatically
# 4. Scrapers begin collecting data
```

### Environment Variables for Production

```bash
# .env (Railway)
SCRAPER_ENABLED=true
SCRAPER_NEWS_INTERVAL=30
SCRAPER_TWITTER_INTERVAL=60
SCRAPER_TRENDS_INTERVAL=360

# Increase timeouts for cloud
SCRAPER_REQUEST_TIMEOUT=15
```

---

## ✅ Verification Checklist

- [ ] All scraper modules imported correctly
- [ ] Scheduler starts without errors
- [ ] Database connection successful
- [ ] First scraper job runs after startup
- [ ] Activities appear in database
- [ ] Dashboard shows new data
- [ ] Telegram channel receives updates
- [ ] No scraper errors in logs
- [ ] Memory usage stable
- [ ] CPU usage normal

---

**System is fully integrated and ready to collect data 24/7! 🎉**
