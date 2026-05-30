# 📰 Data Sources & Web Scraping

## Overview

The District Activity Monitor automatically collects real-time data from multiple Telangana/Siddipet news and social media sources. Data is processed, categorized, and fed into the system as activities.

---

## 🗞️ News & Newspaper Sources

### Supported Publications

| Source | Type | Coverage | Status |
|--------|------|----------|--------|
| **Eenadu** | Telegu Newspaper | Telangana focus | ✅ Active |
| **The Hindu** | English Newspaper | Hyderabad edition | ✅ Active |
| **Times of India** | English Newspaper | Hyderabad & Telangana | ✅ Active |
| **Deccan Chronicle** | English Newspaper | Hyderabad | ✅ Active |
| **Great Andhra** | Online News Portal | Telangana news | ✅ Active |
| **HM Post** | Online News | Local coverage | ✅ Active |

### Scraping Strategy

**Article Extraction:**
```python
# Headlines and summaries from newspaper websites
# Updates: Every 30 minutes
# Parsing: BeautifulSoup4 for HTML parsing
# Storage: Database with categorization
```

**Data Fields:**
- Title
- Summary/Content
- Source publication
- URL
- Publication time
- Category (auto-categorized)

**Example Categories from News:**
- 🚗 **Traffic** - Road accidents, congestion reports
- 🚨 **Incidents** - Crime, theft, public disturbances
- 🆘 **Emergency** - Fire, medical emergencies
- 🌤️ **Weather** - Rainfall, floods, warnings
- 🎉 **Events** - Festivals, functions, celebrations

---

## 🐦 Twitter/X Data

### Tracking

**Keywords Monitored:**
- `Siddipet` - City-specific
- `Telangana` - State-wide
- `Hyderabad` - Regional hub
- `#TelanganaNews` - Official hashtag
- Incident-related: `traffic`, `accident`, `fire`, `police`
- Emergency: `alert`, `warning`, `urgent`

**Data Collection:**
```python
# Using snscrape (no API key required)
# Tweets collected: Last 24 hours
# Update frequency: Every 1 hour
# Language: English only
# Filters: No retweets, original content
```

**Tweet Analysis:**
```python
# Tweet content → Category classification
# Keywords → Severity determination
# Time → Real-time tracking
# Engagement → Importance ranking
```

**Example Tweet Processing:**
```
Tweet: "Major traffic jam at Karimnagar bypass due to accident"
↓
Category: traffic
Severity: high
Location: Karimnagar
Source: Twitter/X
Status: Active
```

### Trending Hashtags

**Monitored Hashtags:**
- `#Siddipet`
- `#Telangana`
- `#Hyderabad`
- `#TelanganaTraffic`
- `#TelanganaNews`
- `#HydCity`

**Trending Analysis:**
- Peak hours tracking
- Topic clustering
- Sentiment analysis (ready to implement)
- Engagement metrics

---

## 📊 Google Trends

### Trend Monitoring

**What's Tracked:**
- Search volume trends
- Related searches
- Geographic breakdown (Telangana focus)
- Time-based trends (24h, 7d, 30d)

**Data Points:**
```python
Trending Search: "Siddipet Road Work"
Interest Over Time: [100, 95, 87, 92, ...]
Related Searches:
  - "Siddipet to Hyderabad"
  - "Siddipet Traffic"
  - "Siddipet News Today"
```

**Use Cases:**
- Identify emerging news topics
- Monitor public interest
- Correlate with activities
- Predictive analysis

**Implementation:**
```python
from pytrends.request import TrendReq

pytrends = TrendReq(hl='en-US', tz=360)
pytrends.build_payload(
    ['Siddipet'],
    cat=0,
    timeframe='now 7-d',
    geo='IN-TG'  # Telangana region
)
interest = pytrends.interest_over_time()
```

---

## 🎥 YouTube

### Video Search & Monitoring

**Search Terms:**
- "Siddipet news"
- "Telangana updates"
- "Hyderabad incidents"
- "Traffic in Siddipet"
- "Breaking news Telangana"

**Video Extraction:**
- Video title
- Channel name
- Upload time
- Description
- Views (as indicator of importance)

**Data Processing:**
- Title → Auto-categorization
- Description → Content analysis
- Metadata → Source credibility

**Limitations:**
- YouTube requires API key for full data
- Current implementation: Search page scraping
- Alternative: YouTube Data API v3 (requires quota)

---

## 🔴 Reddit

### Subreddit Monitoring

**Relevant Subreddits:**
- r/Telangana
- r/Hyderabad
- r/India (Telangana posts)
- r/news (India section)

**Discussion Topics Tracked:**
- Local incidents
- Traffic situations
- Events and gatherings
- Public service issues
- Weather warnings

**Data Collection:**
- Post title & content
- Author & timestamp
- Upvotes (relevance indicator)
- Comments (discussion value)
- Thread discussion

**Implementation Note:**
Reddit scraping requires either:
1. PRAW (Reddit API wrapper) - requires registration
2. Alternative scraping - respecting robots.txt
3. RSS feed parsing

---

## 💬 Discord

### Server Monitoring

**Integration Method:**
- Bot token authentication
- Channel-based monitoring
- Webhook receivers
- Role-based filtering

**Monitored Content:**
- Incident reports
- Live updates
- Emergency alerts
- Community discussions

**Example Setup:**
```python
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_message(message):
    if message.channel.id == SIDDIPET_NEWS_CHANNEL:
        # Process message
        # Extract activity
        # Add to database
```

---

## 👨‍👩‍👧‍👦 Facebook Pages

### Public Page Monitoring

**Tracked Pages:**
- Siddipet Local News
- Telangana Government
- Hyderabad Traffic Updates
- Emergency Services (Official)
- Community Groups (public)

**Data Points:**
- Post text content
- Shared links
- Comments & reactions
- Timestamps
- Engagement metrics

**Implementation:**
```python
# Facebook Graph API (requires access token)
# OR
# Public page scraping (no authentication)

# Get page posts:
# - Title/content
# - Photos/videos
# - Shares & comments
# - Timestamp
```

---

## 🔄 Scraping Schedule

### Automated Collection Timetable

| Task | Frequency | Time | Source |
|------|-----------|------|--------|
| News Scraping | Every 30 min | * | Newspapers |
| Twitter Trends | Every 1 hour | * | Twitter/X |
| Google Trends | Every 6 hours | * | Google Trends |
| YouTube | Daily | 8:00 AM | YouTube |
| Trend Analysis | Every 1 hour | * | All sources |
| Cleanup Old Data | Weekly | Sun 2 AM | Database |
| Health Check | Every 6 hours | * | All systems |

### Concurrent Processing

```
Scraper Jobs (Parallel Execution):
┌─────────────────────────────────┐
│  News Sources (BeautifulSoup)   │ → 30 min interval
├─────────────────────────────────┤
│  Twitter/X (snscrape)           │ → 1 hour interval
├─────────────────────────────────┤
│  Google Trends (pytrends)       │ → 6 hour interval
├─────────────────────────────────┤
│  YouTube (scraping)             │ → Daily
└─────────────────────────────────┘
        ↓
    Data Aggregation
    ↓
    Categorization
    ↓
    Severity Determination
    ↓
    Database Storage
    ↓
    Alert Broadcasting
```

---

## 🏷️ Auto-Categorization Rules

### Category Mapping

**Traffic** 🚗
- Keywords: accident, crash, jam, road, collision, traffic, bypass, highway
- Severity: Based on incident type

**Incident** 🚨
- Keywords: crime, theft, robbery, assault, police, arrest, case
- Severity: Based on crime type

**Emergency** 🆘
- Keywords: fire, ambulance, hospital, emergency, rescue, help, urgent
- Severity: Usually high/critical

**Weather** 🌤️
- Keywords: rain, flood, storm, weather, wind, heavy, alert
- Severity: Based on weather intensity

**Event** 🎉
- Keywords: event, festival, celebration, function, program, ceremony
- Severity: Usually low

**Announcement** 📢
- Default category for unclassified items
- Public notifications, notices
- Severity: Low/Medium

### Severity Determination

```python
# Critical 🔴
- "death", "fatal", "emergency", "critical", "urgent", "severe"
- Multiple incidents in same area
- High engagement/views

# High 🟠
- Accidents, fires, major incidents
- Road blockages
- Unusual activity

# Medium 🟡
- Traffic updates
- Minor incidents
- Notifications

# Low 🟢
- General announcements
- Events
- Standard updates
```

---

## 🔍 Data Quality & Validation

### Quality Checks

1. **Duplicate Detection**
   - Hash similar titles
   - Check against recent entries
   - Merge duplicate reports

2. **Source Verification**
   - Check source credibility
   - Verify URL validity
   - Track source history

3. **Content Validation**
   - Minimum length check
   - Language detection (English/Telugu)
   - Relevance scoring

4. **Timeliness**
   - Timestamp validation
   - Freshness scoring
   - Archive old content

### Error Handling

```python
try:
    # Scrape source
    data = scraper.fetch()
except NetworkError:
    logger.error("Network unreachable")
    # Retry after 5 minutes
except ParsingError:
    logger.error("HTML parsing failed")
    # Skip source, try next
except RateLimit:
    logger.warning("Rate limited")
    # Exponential backoff
```

---

## 🔐 Scraping Ethics & Compliance

### Best Practices

✅ **Respect robots.txt**
```
User-agent: *
Disallow: /
Allow: /public/
```

✅ **User-Agent Header**
```python
headers = {
    'User-Agent': 'Mozilla/5.0 ... DistrictActivityBot/1.0'
}
```

✅ **Rate Limiting**
- News sites: 1 request per 30 seconds
- Social media: Respect platform limits
- Trends: 1 request per hour

✅ **Terms of Service**
- Check ToS before scraping
- Attribute sources properly
- Don't republish copyrighted content

### Platform-Specific Policies

**Twitter/X:**
- Use snscrape (respects platform)
- Don't store media
- Respect rate limits

**Google:**
- Google Trends API (free)
- Terms allow academic use
- Respectful usage required

**News Sites:**
- Check individual ToS
- Most allow aggregation
- Proper attribution required

**YouTube:**
- API has quota limits
- Requires API key
- Public data only

---

## 📊 Data Flow Architecture

```
┌─────────────────────────────────────────────────┐
│         DATA COLLECTION LAYER                   │
├─────────────────────────────────────────────────┤
│  News Scrapers  │  Social Media  │  Trends     │
│  - Eenadu       │  - Twitter     │  - Google   │
│  - The Hindu    │  - Reddit      │  - YouTube  │
│  - TOI          │  - Facebook    │  - Discord  │
│  - DC           │  - Discord     │             │
└────────────────────┬────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────┐
│       DATA AGGREGATION & PROCESSING             │
├─────────────────────────────────────────────────┤
│  - Duplicate Detection                          │
│  - Category Classification                      │
│  - Severity Determination                       │
│  - Quality Validation                           │
│  - Deduplication                                │
└────────────────────┬────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────┐
│         DATABASE STORAGE                        │
├─────────────────────────────────────────────────┤
│  Activities Table (SQLAlchemy ORM)              │
│  - Auto-indexed for performance                 │
│  - Timestamp-based queries                      │
│  - Category grouping                            │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
    ┌────────┐  ┌────────┐  ┌────────┐
    │ Alerts │  │Dashboard│ │Reports │
    │(Telegram)│ │(Web UI) │ │(Hourly)│
    └────────┘  └────────┘  └────────┘
```

---

## 🛠️ Configuration

### Environment Variables

```bash
# Scraper Settings
SCRAPER_ENABLED=true
SCRAPER_NEWS_INTERVAL=30          # Minutes
SCRAPER_TWITTER_INTERVAL=60       # Minutes
SCRAPER_TRENDS_INTERVAL=360       # Minutes (6 hours)
SCRAPER_YOUTUBE_INTERVAL=1440     # Minutes (24 hours)

# Rate Limiting
SCRAPER_REQUEST_TIMEOUT=10        # Seconds
SCRAPER_RETRY_COUNT=3
SCRAPER_BACKOFF_FACTOR=2

# Data Filtering
MIN_ARTICLE_LENGTH=50             # Characters
DUPLICATE_CHECK_DAYS=7            # Days
AUTO_ARCHIVE_DAYS=90              # Days
```

### Source Priority

```python
SOURCE_PRIORITY = {
    'twitter': 0.9,      # High priority (real-time)
    'news': 0.8,         # High priority
    'trends': 0.7,       # Medium
    'youtube': 0.6,      # Medium
    'reddit': 0.5,       # Lower
    'discord': 0.4       # Context-dependent
}
```

---

## 📈 Analytics & Insights

### Metrics Collected

- **Volume**: Activities per hour/day
- **Categories**: Distribution across types
- **Severity**: Critical/high incidents
- **Sources**: Data source breakdown
- **Trending**: Most active areas/topics
- **Recency**: Data freshness

### Reporting

```python
# Included in hourly reports:
- Total activities scraped
- Top 3 news sources
- Current trending topics
- Critical incidents
- Most active areas
```

---

## 🔧 Advanced Features (Roadmap)

- [ ] Sentiment analysis on social media
- [ ] Predictive alerts (ML model)
- [ ] Spam detection
- [ ] Image/video analysis
- [ ] Multi-language support
- [ ] Custom scraper addition
- [ ] Source credibility scoring
- [ ] Misinformation detection

---

## 📞 Troubleshooting

### Scraper Not Running

```bash
# Check logs
tail -f bot.log | grep scraper

# Check scheduler status
python -c "from scheduler import setup_scheduler; print(scheduler.is_running)"

# Manually trigger scraper
python -c "import asyncio; from scrapers import DataAggregator; asyncio.run(DataAggregator().collect_all_data())"
```

### No Data Being Collected

1. Check internet connection
2. Verify source websites are accessible
3. Check rate limiting (too many requests)
4. Review parsing rules (HTML structure changed)
5. Check database connection

### High Memory Usage

```python
# Reduce scraper frequency
SCRAPER_NEWS_INTERVAL = 60  # Changed from 30

# Reduce batch size
MAX_ARTICLES_PER_SOURCE = 5  # Instead of 10

# Archive old data
DELETE FROM activities WHERE created_at < NOW() - INTERVAL '30 days'
```

---

## 📚 References

- **BeautifulSoup4**: https://www.crummy.com/software/BeautifulSoup/
- **snscrape**: https://github.com/JustAnotherArchivist/snscrape
- **pytrends**: https://github.com/GeneralMills/pytrends
- **APScheduler**: https://apscheduler.readthedocs.io/

---

**Data collection is real-time, automated, and 24x7 operational!**
