#!/usr/bin/env python3
"""
Background scheduler for periodic data collection and reporting
Integrates scrapers with the main bot
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class BotScheduler:
    """Manage scheduled tasks for bot operations"""

    def __init__(self, bot_app=None, reporter=None):
        self.scheduler = AsyncIOScheduler()
        self.bot_app = bot_app
        self.reporter = reporter
        self.is_running = False

    async def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return

        self.scheduler.start()
        self.is_running = True
        logger.info("Scheduler started successfully")

    async def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            return

        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Scheduler stopped")

    def add_job(self, func: Callable, trigger, job_id: str, **kwargs):
        """Add a scheduled job"""
        try:
            self.scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                replace_existing=True,
                **kwargs
            )
            logger.info(f"Job added: {job_id}")
        except Exception as e:
            logger.error(f"Error adding job {job_id}: {e}")

    def schedule_interval(self, func: Callable, minutes: int, job_id: str, **kwargs):
        """Schedule a job to run every N minutes"""
        self.add_job(
            func,
            IntervalTrigger(minutes=minutes),
            job_id,
            **kwargs
        )

    def schedule_daily(self, func: Callable, hour: int, minute: int, job_id: str, **kwargs):
        """Schedule a job to run daily at specific time"""
        self.add_job(
            func,
            CronTrigger(hour=hour, minute=minute),
            job_id,
            **kwargs
        )

    def schedule_hourly(self, func: Callable, minute: int, job_id: str, **kwargs):
        """Schedule a job to run hourly at specific minute"""
        self.add_job(
            func,
            CronTrigger(minute=minute),
            job_id,
            **kwargs
        )


class ScraperJobs:
    """Scheduled scraping jobs"""

    def __init__(self, bot_app=None, report_channel_id: Optional[int] = None):
        self.bot_app = bot_app
        self.report_channel_id = report_channel_id
        self.last_scrape_time = {}

    async def scrape_news(self):
        """Scheduled news scraping"""
        try:
            from scrapers import DataAggregator

            logger.info("Starting scheduled news scraping...")
            aggregator = DataAggregator()

            # Collect news data
            data = await aggregator.collect_all_data()
            added = await aggregator.feed_to_database(data)

            logger.info(f"News scraping complete: {added} activities added")

            # Broadcast high-severity items
            if self.bot_app and self.report_channel_id:
                await self._broadcast_critical_items(data)

        except Exception as e:
            logger.error(f"Error in scrape_news job: {e}")

    async def generate_hourly_report(self):
        """Generate and broadcast hourly report"""
        try:
            if not self.bot_app or not self.report_channel_id:
                logger.warning("Bot app or channel not configured for hourly report")
                return

            from reporter import ReportGenerator

            logger.info("Generating hourly report...")
            reporter = ReportGenerator()
            report = reporter.generate_hourly_report()

            await self.bot_app.bot.send_message(
                chat_id=self.report_channel_id,
                text=report,
                parse_mode='Markdown'
            )

            logger.info("Hourly report sent")

        except Exception as e:
            logger.error(f"Error generating hourly report: {e}")

    async def generate_daily_summary(self):
        """Generate and broadcast daily summary"""
        try:
            if not self.bot_app or not self.report_channel_id:
                logger.warning("Bot app or channel not configured for daily summary")
                return

            from reporter import ReportGenerator

            logger.info("Generating daily summary...")
            reporter = ReportGenerator()
            summary = reporter.generate_daily_summary()

            await self.bot_app.bot.send_message(
                chat_id=self.report_channel_id,
                text=summary,
                parse_mode='Markdown'
            )

            logger.info("Daily summary sent")

        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")

    async def check_trends(self):
        """Monitor trending topics"""
        try:
            from scrapers import TwitterTrendScraper, GoogleTrendsScraper

            logger.info("Checking current trends...")

            # Twitter trends
            twitter_scraper = TwitterTrendScraper()
            twitter_data = await twitter_scraper.scrape_trending_hashtags()

            # Google trends
            trends_scraper = GoogleTrendsScraper()
            google_trends = await trends_scraper.scrape_trends()

            logger.info(f"Found {len(twitter_data)} trending tweets, {len(google_trends)} Google trends")

            # Feed to database
            from scrapers import DataAggregator
            aggregator = DataAggregator()
            await aggregator.feed_to_database(twitter_data + google_trends)

        except Exception as e:
            logger.error(f"Error checking trends: {e}")

    async def cleanup_old_activities(self):
        """Archive old activities"""
        try:
            from database import get_db_handler
            from sqlalchemy import delete

            handler = get_db_handler()
            session = handler.get_session()

            # Archive activities older than 90 days
            cutoff_date = datetime.utcnow() - timedelta(days=90)

            from database import Activity

            result = session.query(Activity).filter(
                Activity.created_at < cutoff_date,
                Activity.status != 'archived'
            ).update({'status': 'archived'})

            session.commit()
            logger.info(f"Archived {result} old activities")

        except Exception as e:
            logger.error(f"Error cleaning up activities: {e}")

    async def health_check(self):
        """Periodic health check"""
        try:
            from database import get_db_handler

            handler = get_db_handler()
            session = handler.get_session()

            # Test database connection
            result = session.execute("SELECT 1")
            session.close()

            logger.info("✅ Health check passed - All systems operational")

        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")

    async def _broadcast_critical_items(self, data: list):
        """Broadcast critical items to report channel"""
        try:
            critical_items = [
                item for item in data
                if item.get('severity') in ['critical', 'high']
            ]

            if not critical_items:
                return

            for item in critical_items[:5]:  # Limit to 5 per cycle
                message = f"""
🚨 **CRITICAL ALERT**

**Source:** {item.get('source')}
**Category:** {item.get('category', 'Unknown').upper()}
**Title:** {item.get('title', item.get('content', '')[:100])}

⚠️ Please take necessary action
                """

                await self.bot_app.bot.send_message(
                    chat_id=self.report_channel_id,
                    text=message,
                    parse_mode='Markdown'
                )

        except Exception as e:
            logger.error(f"Error broadcasting critical items: {e}")


def setup_scheduler(bot_app, report_channel_id: int) -> BotScheduler:
    """Setup and configure scheduler with all jobs"""

    scheduler = BotScheduler(bot_app=bot_app)
    jobs = ScraperJobs(bot_app=bot_app, report_channel_id=report_channel_id)

    # News scraping - every 30 minutes
    scheduler.schedule_interval(
        jobs.scrape_news,
        minutes=30,
        job_id='scrape_news',
        name='News Scraping'
    )

    # Trend monitoring - every 1 hour
    scheduler.schedule_interval(
        jobs.check_trends,
        minutes=60,
        job_id='check_trends',
        name='Trend Monitoring'
    )

    # Hourly report - top of every hour
    scheduler.schedule_hourly(
        jobs.generate_hourly_report,
        minute=0,
        job_id='hourly_report',
        name='Hourly Report'
    )

    # Daily summary - 8:00 AM
    scheduler.schedule_daily(
        jobs.generate_daily_summary,
        hour=8,
        minute=0,
        job_id='daily_summary',
        name='Daily Summary'
    )

    # Cleanup old data - weekly (Sundays at 2 AM)
    scheduler.add_job(
        jobs.cleanup_old_activities,
        CronTrigger(day_of_week='6', hour=2, minute=0),
        job_id='cleanup_activities',
        name='Cleanup Old Activities'
    )

    # Health check - every 6 hours
    scheduler.schedule_interval(
        jobs.health_check,
        minutes=360,
        job_id='health_check',
        name='Health Check'
    )

    logger.info("Scheduler configured with all jobs")
    return scheduler
