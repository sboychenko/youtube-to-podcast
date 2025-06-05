import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from sqlalchemy.orm import Session
from models import User, Track
import uuid
import asyncio
from datetime import datetime
import logging
import re
import unicodedata
from utils import process_podcast_cover

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PodcastBot:
    def __init__(self, token: str, domain: str, session: Session):
        logger.info("Initializing PodcastBot...")
        try:
            self.application = Application.builder().token(token).build()
            logger.debug("Application builder created successfully")
            self.domain = domain
            self.session = session
            self.setup_handlers()
            logger.info("PodcastBot initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing PodcastBot: {e}", exc_info=True)
            raise

    def setup_handlers(self):
        logger.info("Setting up message handlers...")
        try:
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("feed", self.feed_command))
            self.application.add_handler(CommandHandler("list", self.list_command))
            self.application.add_handler(CommandHandler("delete", self.delete_command))
            self.application.add_handler(CommandHandler("setimage", self.set_image_command))
            self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_image))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_youtube_url))
            logger.info("Message handlers setup completed")
        except Exception as e:
            logger.error(f"Error setting up handlers: {e}", exc_info=True)
            raise

    async def start(self):
        logger.info("Starting bot polling...")
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            logger.info("Bot polling started successfully")
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            logger.info("Bot polling cancelled, shutting down...")
        except Exception as e:
            logger.error(f"Error starting bot: {e}", exc_info=True)
            raise

    async def stop(self):
        logger.info("Stopping bot...")
        try:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Bot stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}", exc_info=True)
            raise

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = self.session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            user = User(
                telegram_id=update.effective_user.id,
                uuid=str(uuid.uuid4()),
                username=update.effective_user.username
            )
            self.session.add(user)
            self.session.commit()
            
        welcome_text = (
            "🎙 *Welcome to YouTube to Podcast Bot!*\n\n"
            "I'll help you create your own podcast feed from YouTube videos.\n\n"
            "Just send me a YouTube video URL to add it to your podcast feed!\n"
            "or use ❓ `/help` - Show help message\n"
        )
        await update.message.reply_text(welcome_text, parse_mode='Markdown')

    async def feed_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /feed command"""
        user = self.session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await update.message.reply_text("❌ Please use /start first")
            return
            
        domain = os.getenv("DOMAIN")
        rss_url = f"https://{domain}/rss/{user.uuid}"
        
        await update.message.reply_text(
            f"🎵 *Your Podcast RSS Feed*\n\n"
            f"Add this URL to your podcast app:\n"
            f"`{rss_url}`\n\n"
            f"*Note:* Make sure to add a cover image using /setimage for better appearance!",
            parse_mode='Markdown'
        )

    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command"""
        user = self.session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await update.message.reply_text("❌ Please use /start first")
            return
            
        tracks = self.session.query(Track).filter_by(user_id=user.id).order_by(Track.created_at.desc()).all()
        if not tracks:
            await update.message.reply_text(
                "📭 *Your feed is empty*\n\n"
                "Send me a YouTube URL to add your first video!",
                parse_mode='Markdown'
            )
            return
            
        message = "📋 *Your Podcast Feed*\n\n"
        for i, track in enumerate(tracks, 1):
            message += f"{i}. {track.title}\n"
            
        message += "\nUse /delete to remove videos from your feed."
        await update.message.reply_text(message, parse_mode='Markdown')

    async def delete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /delete command"""
        user = self.session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await update.message.reply_text("❌ Please use /start first")
            return
            
        tracks = self.session.query(Track).filter_by(user_id=user.id).order_by(Track.created_at.desc()).all()
        if not tracks:
            await update.message.reply_text(
                "📭 *Your feed is empty*\n\n"
                "Send me a YouTube URL to add your first video!",
                parse_mode='Markdown'
            )
            return

        try:
            track_num = int(context.args[0])
        except (IndexError, ValueError):
            message = (
                "❌ *Invalid command format*\n\n"
                "Usage: `/delete <number>`\n\n"
                "*Your videos:*\n"
            )
            for i, track in enumerate(tracks, 1):
                message += f"{i}. {track.title}\n"
            await update.message.reply_text(message, parse_mode='Markdown')
            return

        if not 1 <= track_num <= len(tracks):
            message = (
                "❌ *Invalid video number*\n\n"
                "Please choose a number from the list:\n"
            )
            for i, track in enumerate(tracks, 1):
                message += f"{i}. {track.title}\n"
            await update.message.reply_text(message, parse_mode='Markdown')
            return
            
        track = tracks[track_num - 1]
        file_path = f"data/{user.uuid}/{track.file_name}"
        try:
            os.remove(file_path)
        except OSError:
            pass  # File might not exist

        self.session.delete(track)
        self.session.commit()
        
        await update.message.reply_text(
            f"✅ *Video deleted successfully!*\n\n"
            f"Removed: *{track.title}*",
            parse_mode='Markdown'
        )

    async def set_image_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setimage command"""
        user = self.session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await update.message.reply_text("❌ Please use /start first")
            return
            
        context.user_data['waiting_for_image'] = True
        await update.message.reply_text(
            "🖼 *Send me an image to use as your podcast cover*\n\n"
            "The image will be resized and text will be added automatically.",
            parse_mode='Markdown'
        )

    async def handle_youtube_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.text or not update.message.text.startswith(("https://www.youtube.com/", "https://youtu.be/")):
            return

        user = self.session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await update.message.reply_text("Please use /start first.")
            return

        await update.message.reply_text("Downloading and processing your video...")

        # Create user directory if it doesn't exist
        user_dir = f"data/{user.uuid}"
        os.makedirs(user_dir, exist_ok=True)

        # Download audio
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{user_dir}/%(id)s.%(ext)s',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(update.message.text, download=True)
                title = info['title']
                video_id = info['id']
                file_name = f"{video_id}.mp3"
                file_path = f"{user_dir}/{file_name}"

                # Wait a moment to ensure the file is fully written
                await asyncio.sleep(1)

                # Check if the original file exists
                if not os.path.exists(file_path):
                    logger.error(f"Original file not found: {file_path}")
                    await update.message.reply_text("Error: Downloaded file not found")
                    return

                # Save to database
                track = Track(
                    user_id=user.id,
                    title=title,
                    youtube_url=update.message.text,
                    file_name=f"{video_id}.mp3"
                )
                self.session.add(track)
                self.session.commit()

                await update.message.reply_text(f"Successfully added '{title}' to your podcast feed!")
        except Exception as e:
            logger.error(f"Error processing video: {e}", exc_info=True)
            await update.message.reply_text(f"Error processing video: {str(e)}")

    async def handle_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle image upload - save as podcast cover"""
        if not context.user_data.get('waiting_for_image'):
            return

        user = self.session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await update.message.reply_text("❌ Please use /start first")
            return

        try:
            # Get the photo file
            photo = await update.message.photo[-1].get_file()
            
            # Download the image
            image_bytes = await photo.download_as_bytearray()
            
            # Process the image
            processed_image = process_podcast_cover(image_bytes, f'@{update.effective_user.username}')
            
            # Save the modified image
            os.makedirs(f"data/{user.uuid}", exist_ok=True)
            with open(f"data/{user.uuid}/image.jpg", "wb") as f:
                f.write(processed_image)
            
            user.image = True
            self.session.commit()
            
            await update.message.reply_text(
                "✅ *Image set as podcast cover!*\n\n"
                "Your podcast feed will now show this image as the cover.",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error setting image: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ *Error setting image*\n\n"
                "Please try again or use a different image.",
                parse_mode='Markdown'
            )
        finally:
            context.user_data['waiting_for_image'] = False 

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "🤖 *YouTube to Podcast Bot*\n\n"
            "This bot converts YouTube videos to your custom podcast feed.\n\n"
            "📝 *Available commands:*\n"
            "• `/start` - Start the bot\n"
            "• `/setimage` - Set podcast cover image\n"
            "• `/list` - Show list of added videos\n"
            "• `/delete` - Delete video from the list\n"
            "• `/feed` - Get podcast RSS feed\n"
            "• `/help` - Show this message\n\n"
            "🌐 *Links:*\n"
            "Web: [page on internet](https://app.sboychenko.ru)\n"
            "Author: @sboychenko\\_life"
        )
        
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown',
            disable_web_page_preview=True
        ) 