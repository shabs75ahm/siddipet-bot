#!/usr/bin/env python3
"""
Main entry point - combines Telegram bot and Flask API/Dashboard
Runs both concurrently using threading
"""

import os
import sys
import logging
import asyncio
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Force UTF-8 encoding on stdout for Windows BEFORE logging
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configure logging with UTF-8 encoding for emoji support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(stream=sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

from bot import DistrictActivityBot
from api_handler import api_app
from dashboard import dashboard


def run_flask_apps():
    """Run Flask apps (API and Dashboard) on different ports"""
    api_port = int(os.getenv('API_PORT', 5001))
    dashboard_port = int(os.getenv('DASHBOARD_PORT', 5002))

    logger.info(f"Starting API server on port {api_port}...")
    logger.info(f"Starting Dashboard on port {dashboard_port}...")

    # Run API in thread
    api_thread = threading.Thread(
        target=lambda: api_app.run(
            host='0.0.0.0',
            port=api_port,
            debug=False,
            use_reloader=False
        ),
        daemon=True
    )

    # Run Dashboard in thread
    dashboard_thread = threading.Thread(
        target=lambda: dashboard.run(
            host='0.0.0.0',
            port=dashboard_port,
            debug=False,
            use_reloader=False
        ),
        daemon=True
    )

    api_thread.start()
    dashboard_thread.start()

    logger.info(f"✅ API available at: http://0.0.0.0:{api_port}")
    logger.info(f"✅ Dashboard available at: http://0.0.0.0:{dashboard_port}")


async def main():
    """Main entry point"""
    try:
        # Validate environment variables
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        admin_ids = os.getenv('ADMIN_IDS', '').split(',')
        report_channel_id = int(os.getenv('REPORT_CHANNEL_ID', '0'))

        if not token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not set")
            sys.exit(1)

        if not report_channel_id:
            logger.error("❌ REPORT_CHANNEL_ID not set")
            sys.exit(1)

        logger.info("=" * 60)
        logger.info("🚀 DISTRICT ACTIVITY MONITORING BOT")
        logger.info("=" * 60)
        logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        logger.info(f"Database: {os.getenv('DATABASE_URL', 'SQLite')}")
        logger.info(f"Report Channel ID: {report_channel_id}")

        # Start Flask apps in background thread
        flask_thread = threading.Thread(target=run_flask_apps, daemon=True)
        flask_thread.start()

        # Give Flask time to start
        await asyncio.sleep(2)

        # Create and run bot
        bot = DistrictActivityBot(
            token=token,
            admin_ids=[int(id.strip()) for id in admin_ids if id.strip()],
            report_channel_id=report_channel_id
        )

        logger.info("🤖 Starting Telegram Bot...")
        await bot.run()

    except KeyboardInterrupt:
        logger.info("\n⏹️  Shutting down...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
