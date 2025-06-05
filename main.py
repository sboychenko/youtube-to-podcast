import os
import asyncio
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from models import init_db
from bot import PodcastBot
from server import app
import uvicorn
import sys
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Load environment variables
logger.info("Loading environment variables...")
load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")
if not token:
    logger.error("TELEGRAM_BOT_TOKEN is not set in .env file!")
else:
    logger.info("TELEGRAM_BOT_TOKEN is set")
domain = os.getenv("DOMAIN")
logger.info(f"DOMAIN is set to: {domain}")

# Initialize database
DATABASE_URL = os.getenv("DATABASE_URL")
logger.info(f"Using database URL: {DATABASE_URL}")
engine = init_db(DATABASE_URL)
Session = sessionmaker(bind=engine)

bot_instance = None
server = None


def handle_exit(signum, frame):
    logger.info("Received exit signal, shutting down...")
    if server:
        server.should_exit = True

async def main():
    global server, bot_instance
    # Set up signal handlers
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # Создаем бота
    bot_instance = PodcastBot(
        token=token,
        domain=domain,
        session=Session()
    )

    # Создаем сервер
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
    server = uvicorn.Server(config)

    # Запускаем обе задачи параллельно
    bot_task = asyncio.create_task(bot_instance.start())
    server_task = asyncio.create_task(server.serve())

    done, pending = await asyncio.wait(
        [bot_task, server_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    # Если одна из задач завершилась — останавливаем вторую
    for task in pending:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    # Останавливаем бота, если он еще не остановлен
    await bot_instance.stop()
    logger.info("Application shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    finally:
        logger.info("Application shutdown complete") 