import asyncio
import logging
import os
import signal
import sys
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# Import handlers
from handlers import start, admin, menu

# Import utilities
from utils.database import init_database
from utils.sheets import test_connection

# Load environment variables
load_dotenv()

# Global shutdown flag
shutdown_event = asyncio.Event()

# Configure logging (stdout only for Docker compatibility)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("BOT_TOKEN not found in environment variables")
    sys.exit(1)

# Create bot and dispatcher
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Use memory storage for FSM
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Include routers
dp.include_router(start.router)
dp.include_router(admin.router)
dp.include_router(menu.router)

async def on_startup():
    """Bot startup tasks"""
    logger.info("Starting Lethai Concierge Referral Bot...")
    
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)
    
    # Test Google Sheets connection
    try:
        if test_connection():
            logger.info("Google Sheets connection successful")
        else:
            logger.warning("Google Sheets connection failed - check credentials")
    except Exception as e:
        logger.error(f"Google Sheets connection test failed: {e}")
    
    # Get bot info
    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot started successfully: @{bot_info.username}")
    except Exception as e:
        logger.error(f"Failed to get bot info: {e}")
    
    logger.info("Bot startup completed")

async def on_shutdown():
    """Bot shutdown tasks"""
    logger.info("Shutting down bot...")
    
    # Close bot session
    await bot.session.close()
    
    logger.info("Bot shutdown completed")

async def handle_shutdown(sig):
    """Handle shutdown signals"""
    logger.info(f"Received signal {sig.name}, initiating graceful shutdown...")
    shutdown_event.set()
    
    # Stop the dispatcher
    await dp.stop_polling()

async def main():
    """Main function"""
    # Setup signal handlers
    loop = asyncio.get_running_loop()
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(handle_shutdown(s))
        )
    
    try:
        # Run startup tasks
        await on_startup()
        
        # Start polling
        logger.info("Starting bot polling...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        # Run shutdown tasks
        await on_shutdown()
        logger.info("Bot shutdown complete")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)



