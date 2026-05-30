#!/usr/bin/env python3
"""
District Activity Monitoring Bot
Real-time collection and reporting of district-wide activities
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import TelegramError

from database import init_db, add_activity, get_activities, get_stats, Activity
from reporter import ReportGenerator
from api_handler import setup_external_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Activity categories
ACTIVITY_CATEGORIES = {
    'incident': '🚨 Incident',
    'event': '🎉 Event',
    'announcement': '📢 Announcement',
    'traffic': '🚗 Traffic',
    'service': '🔧 Service',
    'emergency': '🆘 Emergency',
    'weather': '🌤️ Weather',
    'other': '📌 Other'
}

SEVERITY_LEVELS = {
    'low': '🟢 Low',
    'medium': '🟡 Medium',
    'high': '🔴 High',
    'critical': '🔴🔴 Critical'
}


class DistrictActivityBot:
    def __init__(self, token: str, admin_ids: list, report_channel_id: int):
        self.token = token
        self.admin_ids = admin_ids
        self.report_channel_id = report_channel_id
        self.app = None
        self.reporter = ReportGenerator()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command - show bot info"""
        keyboard = [
            [InlineKeyboardButton("📝 Report Activity", callback_data='report')],
            [InlineKeyboardButton("📊 View Stats", callback_data='stats')],
            [InlineKeyboardButton("📋 Recent Activities", callback_data='recent')],
            [InlineKeyboardButton("ℹ️ Help", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = """
🏘️ **District Activity Monitor Bot**

Real-time monitoring of all district activities and events.

**Features:**
• Report incidents, events, and announcements
• Real-time alerts for critical events
• Activity dashboard and statistics
• Hourly/daily summaries

**How to use:**
1. Click "Report Activity" to submit an event
2. View live statistics and recent activities
3. Receive real-time alerts for critical incidents

Use /help for detailed commands.
        """
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message"""
        help_text = """
**Commands:**
/start - Start the bot
/report - Report a new activity
/stats - View district statistics
/recent - See recent activities
/help - Show this help message

**Reporting Activities:**
When reporting, include:
• Category (incident, event, announcement, etc.)
• Location (district/area)
• Description
• Severity level (for incidents)
• Any relevant attachments

**Real-time Alerts:**
Critical and high-severity incidents are automatically broadcast to monitoring channels.

**Dashboard:**
Visit the web dashboard for live activity map and statistics.
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks"""
        query = update.callback_query
        await query.answer()

        if query.data == 'report':
            await self.report_activity(update, context)
        elif query.data == 'stats':
            await self.show_stats(update, context)
        elif query.data == 'recent':
            await self.show_recent(update, context)
        elif query.data == 'help':
            await self.help_command(update, context)

    async def report_activity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start activity reporting flow"""
        keyboard = [
            [InlineKeyboardButton(cat, callback_data=f'cat_{key}') for key, cat in list(ACTIVITY_CATEGORIES.items())[:2]],
            [InlineKeyboardButton(cat, callback_data=f'cat_{key}') for key, cat in list(ACTIVITY_CATEGORIES.items())[2:4]],
            [InlineKeyboardButton(cat, callback_data=f'cat_{key}') for key, cat in list(ACTIVITY_CATEGORIES.items())[4:6]],
            [InlineKeyboardButton(cat, callback_data=f'cat_{key}') for key, cat in list(ACTIVITY_CATEGORIES.items())[6:]],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.effective_message.edit_text(
            "Select activity category:",
            reply_markup=reply_markup
        )
        context.user_data['reporting'] = True
        context.user_data['stage'] = 'category'

    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show district statistics"""
        stats = get_stats()

        stats_text = f"""
📊 **District Activity Statistics**

**Last 24 Hours:**
• Total Activities: {stats.get('total_24h', 0)}
• Incidents: {stats.get('incidents_24h', 0)}
• Events: {stats.get('events_24h', 0)}
• Emergencies: {stats.get('emergencies_24h', 0)}

**This Week:**
• Total Activities: {stats.get('total_week', 0)}
• Critical Incidents: {stats.get('critical_week', 0)}

**High Severity (24h):**
{self._format_severity_stats(stats.get('severity_24h', {}))}

**Most Active Areas:**
{self._format_top_areas(stats.get('top_areas', []))}
        """

        await update.effective_message.edit_text(
            stats_text,
            parse_mode='Markdown'
        )

    async def show_recent(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show recent activities"""
        activities = get_activities(limit=10)

        if not activities:
            await update.effective_message.edit_text("No recent activities recorded.")
            return

        recent_text = "📋 **Recent Activities (Last 10):**\n\n"
        for activity in activities:
            time_ago = self._time_ago(activity.created_at)
            recent_text += f"""
{ACTIVITY_CATEGORIES.get(activity.category, activity.category)} | {activity.location}
{activity.description[:100]}...
⏰ {time_ago} ago
━━━━━━━━━━━━━━━━━━━
"""

        await update.effective_message.edit_text(
            recent_text,
            parse_mode='Markdown'
        )

    async def handle_report_submission(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming report text"""
        if not context.user_data.get('reporting'):
            await update.message.reply_text("Use /report to start reporting an activity.")
            return

        stage = context.user_data.get('stage')
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.full_name

        # Parse activity details from message
        try:
            activity_data = self._parse_activity_message(update.message.text)

            # Add to database
            activity = add_activity(
                category=context.user_data.get('category', 'other'),
                description=activity_data.get('description'),
                location=activity_data.get('location'),
                severity=activity_data.get('severity', 'low'),
                reported_by=username,
                reporter_id=user_id
            )

            await update.message.reply_text(
                f"✅ Activity recorded successfully!\n\n"
                f"Category: {ACTIVITY_CATEGORIES.get(activity.category)}\n"
                f"Location: {activity.location}\n"
                f"Severity: {SEVERITY_LEVELS.get(activity.severity)}"
            )

            # Send to reporting channel if high severity
            if activity.severity in ['high', 'critical']:
                await self._broadcast_alert(activity)

            context.user_data['reporting'] = False

        except Exception as e:
            logger.error(f"Error processing report: {e}")
            await update.message.reply_text(
                "❌ Error processing report. Please include location and description."
            )

    def _parse_activity_message(self, message: str) -> dict:
        """Parse activity details from message"""
        lines = message.split('\n')
        data = {
            'location': '',
            'description': message,
            'severity': 'low'
        }

        # Simple parsing - can be enhanced with NLP
        for line in lines:
            if 'location' in line.lower() or 'area' in line.lower():
                data['location'] = line.split(':')[1].strip() if ':' in line else line
            if 'severity' in line.lower():
                for severity in SEVERITY_LEVELS.keys():
                    if severity in line.lower():
                        data['severity'] = severity

        if not data['location']:
            data['location'] = 'Unknown'

        return data

    async def _broadcast_alert(self, activity: Activity):
        """Send alert for critical/high severity activities"""
        try:
            alert_msg = f"""
{SEVERITY_LEVELS.get(activity.severity)}  **{ACTIVITY_CATEGORIES.get(activity.category)}**

📍 Location: {activity.location}
📝 Details: {activity.description[:200]}
👤 Reported by: {activity.reported_by}
⏰ Time: {activity.created_at.strftime('%Y-%m-%d %H:%M:%S')}
            """

            await self.app.bot.send_message(
                chat_id=self.report_channel_id,
                text=alert_msg,
                parse_mode='Markdown'
            )
        except TelegramError as e:
            logger.error(f"Error broadcasting alert: {e}")

    def _format_severity_stats(self, severity_dict: dict) -> str:
        """Format severity statistics"""
        text = ""
        for severity, count in severity_dict.items():
            text += f"• {SEVERITY_LEVELS.get(severity)}: {count}\n"
        return text

    def _format_top_areas(self, areas: list) -> str:
        """Format top areas"""
        return '\n'.join([f"• {area[0]}: {area[1]} activities" for area in areas[:5]])

    @staticmethod
    def _time_ago(dt: datetime) -> str:
        """Calculate time ago string"""
        now = datetime.utcnow()
        diff = now - dt

        if diff.seconds < 60:
            return f"{diff.seconds}s"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60}m"
        elif diff.days == 0:
            return f"{diff.seconds // 3600}h"
        else:
            return f"{diff.days}d"

    async def setup_periodic_reports(self):
        """Setup periodic reporting tasks"""
        # Hourly report job
        self.app.job_queue.run_repeating(
            self.send_hourly_report,
            interval=3600,
            first=60
        )

        # Daily summary job
        self.app.job_queue.run_daily(
            self.send_daily_summary,
            time=datetime.strptime("08:00", "%H:%M").time()
        )

    async def send_hourly_report(self, context: ContextTypes.DEFAULT_TYPE):
        """Send hourly activity report"""
        try:
            report = self.reporter.generate_hourly_report()

            await self.app.bot.send_message(
                chat_id=self.report_channel_id,
                text=report,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error sending hourly report: {e}")

    async def send_daily_summary(self, context: ContextTypes.DEFAULT_TYPE):
        """Send daily activity summary"""
        try:
            report = self.reporter.generate_daily_summary()

            await self.app.bot.send_message(
                chat_id=self.report_channel_id,
                text=report,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")

    async def run(self):
        """Start the bot"""
        # Initialize database
        init_db()

        # Create application
        self.app = Application.builder().token(self.token).build()

        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("report", self.report_activity))
        self.app.add_handler(CommandHandler("stats", self.show_stats))
        self.app.add_handler(CommandHandler("recent", self.show_recent))

        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_report_submission))

        # Setup periodic reports
        await self.setup_periodic_reports()

        # Start bot
        logger.info("Starting District Activity Monitoring Bot...")
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()

        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Shutting down bot...")
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()


async def main():
    """Main entry point"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    admin_ids = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]
    report_channel_id = int(os.getenv('REPORT_CHANNEL_ID', '0'))

    if not token or not report_channel_id:
        raise ValueError("Missing required environment variables")

    # Initialize external API handler
    setup_external_api()

    bot = DistrictActivityBot(token, admin_ids, report_channel_id)
    await bot.run()


if __name__ == '__main__':
    asyncio.run(main())
