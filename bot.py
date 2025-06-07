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
from utils import process_podcast_cover, calculate_user_storage, format_size
from locales import get_text
import mutagen

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_lang(update: Update) -> str:
    """Get user's language code or default to 'en'"""
    return update.effective_user.language_code or 'en'


class PodcastBot:
    def __init__(self, token: str, domain: str, session: Session, admin_id: int):
        logger.info("Initializing PodcastBot...")
        try:
            self.application = Application.builder().token(token).build()
            logger.debug("Application builder created successfully")
            self.domain = domain
            self.session = session
            self.admin_id = admin_id
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
            # Admin commands    
            self.application.add_handler(CommandHandler("stat", self.stat_command))
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

    async def _process_and_save_image(self, image_bytes: bytes, user: User, username: str) -> bool:
        """Process and save podcast cover image
        
        Args:
            image_bytes: Raw image bytes
            user: User object
            username: Username to display on the cover
            
        Returns:
            bool: True if image was processed and saved successfully
        """
        try:
            # Process the image
            processed_image = process_podcast_cover(image_bytes, f'@{username}')
            
            # Save the modified image
            os.makedirs(f"data/{user.uuid}", exist_ok=True)
            with open(f"data/{user.uuid}/image.jpg", "wb") as f:
                f.write(processed_image)
            
            user.image = True
            self.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error processing image: {e}", exc_info=True)
            return False

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = self.session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        is_new_user = False
        
        if not user:
            user = User(
                telegram_id=update.effective_user.id,
                uuid=str(uuid.uuid4()),
                username=update.effective_user.username
            )
            self.session.add(user)
            self.session.commit()
            is_new_user = True
            
        # Try to get user's profile photo
        try:
            photos = await update.effective_user.get_profile_photos(limit=1)
            if photos and photos.photos:
                # Get the largest photo
                photo = photos.photos[0][-1]
                photo_file = await photo.get_file()
                image_bytes = await photo_file.download_as_bytearray()
                
                await self._process_and_save_image(image_bytes, user, update.effective_user.username)
        except Exception as e:
            logger.error(f"Error setting default image from avatar: {e}", exc_info=True)
            
        domain = os.getenv("DOMAIN")
        rss_url = f"https://{domain}/rss/{user.uuid}"
            
        welcome_text = get_text(get_lang(update), 'welcome', rss_url=rss_url)
        await update.message.reply_text(welcome_text, parse_mode='Markdown')

        # Notify admin about new user
        if is_new_user and self.admin_id:
            try:
                admin_notification = get_text(get_lang(update), 'new_user_notification',
                    username=update.effective_user.username or 'Unknown',
                    user_id=update.effective_user.id
                )
                await context.bot.send_message(
                    chat_id=self.admin_id,
                    text=admin_notification,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error sending admin notification: {e}", exc_info=True)

    async def feed_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /feed command"""
        user = self.session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await update.message.reply_text(get_text(get_lang(update), 'start_first'))
            return
            
        domain = os.getenv("DOMAIN")
        rss_url = f"https://{domain}/rss/{user.uuid}"
        
        await update.message.reply_text(
            get_text(get_lang(update), 'feed', rss_url=rss_url),
            parse_mode='Markdown'
        )

    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command"""
        user = self.session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await update.message.reply_text(get_text(get_lang(update), 'start_first'))
            return
            
        tracks = self.session.query(Track).filter_by(user_id=user.id).order_by(Track.created_at.desc()).all()
        if not tracks:
            await update.message.reply_text(
                get_text(get_lang(update), 'list_empty'),
                parse_mode='Markdown'
            )
            return
            
        tracks_text = []
        for i, track in enumerate(tracks, 1):
            tracks_text.append(get_text(get_lang(update), 'track_item',
                number=i,
                title=track.title,
                url=track.youtube_url
            ))
            
        await update.message.reply_text(
            get_text(get_lang(update), 'list', tracks='\n'.join(tracks_text)),
            parse_mode='Markdown',
            disable_web_page_preview=True
        )

    async def delete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /delete command"""
        user = self.session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await update.message.reply_text(get_text(get_lang(update), 'start_first'))
            return
            
        tracks = self.session.query(Track).filter_by(user_id=user.id).order_by(Track.created_at.desc()).all()
        if not tracks:
            await update.message.reply_text(
                get_text(get_lang(update), 'list_empty'),
                parse_mode='Markdown'
            )
            return

        try:
            track_num = int(context.args[0])
        except (IndexError, ValueError):
            tracks_text = []
            for i, track in enumerate(tracks, 1):
                tracks_text.append(f"{i}. {track.title}")
            
            await update.message.reply_text(
                get_text(get_lang(update), 'delete_invalid', tracks='\n'.join(tracks_text)),
                parse_mode='Markdown'
            )
            return

        if not 1 <= track_num <= len(tracks):
            tracks_text = []
            for i, track in enumerate(tracks, 1):
                tracks_text.append(f"{i}. {track.title}")
            
            await update.message.reply_text(
                get_text(get_lang(update), 'delete_invalid_number', tracks='\n'.join(tracks_text)),
                parse_mode='Markdown'
            )
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
            get_text(get_lang(update), 'delete_success', title=track.title),
            parse_mode='Markdown'
        )

    async def set_image_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setimage command"""
        user = self.session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await update.message.reply_text(get_text(get_lang(update), 'start_first'))
            return
            
        context.user_data['waiting_for_image'] = True
        await update.message.reply_text(
            get_text(get_lang(update), 'setimage_prompt'),
            parse_mode='Markdown'
        )

    async def handle_youtube_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.text or not update.message.text.startswith(("https://www.youtube.com/", "https://youtu.be/")):
            return

        user = self.session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await update.message.reply_text(get_text(get_lang(update), 'start_first'))
            return

        await update.message.reply_text(get_text(get_lang(update), 'download_start'))

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
                    await update.message.reply_text(get_text(get_lang(update), 'download_error', error="Downloaded file not found"))
                    return

                # Process the audio file
                audio = mutagen.File(file_path)
                duration = str(int(audio.info.length))

                # Save to database
                track = Track(
                    user_id=user.id,
                    title=title,
                    youtube_url=update.message.text,
                    file_name=f"{video_id}.mp3",
                    duration=duration
                )
                self.session.add(track)
                self.session.commit()

                await update.message.reply_text(get_text(get_lang(update), 'download_success', title=title))
        except Exception as e:
            logger.error(f"Error processing video: {e}", exc_info=True)
            await update.message.reply_text(get_text(get_lang(update), 'download_error', error=str(e)))

    async def handle_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle image upload - save as podcast cover"""
        if not context.user_data.get('waiting_for_image'):
            return

        user = self.session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await update.message.reply_text(get_text(get_lang(update), 'start_first'))
            return

        try:
            # Get the photo file
            photo = await update.message.photo[-1].get_file()
            
            # Download the image
            image_bytes = await photo.download_as_bytearray()
            
            # Process and save the image
            success = await self._process_and_save_image(image_bytes, user, update.effective_user.username)
            
            if success:
                await update.message.reply_text(
                    get_text(get_lang(update), 'setimage_success'),
                    parse_mode='Markdown'
                )
            else:
                raise Exception("Failed to process image")
                
        except Exception as e:
            logger.error(f"Error setting image: {e}", exc_info=True)
            await update.message.reply_text(
                get_text(get_lang(update), 'setimage_error'),
                parse_mode='Markdown'
            )
        finally:
            context.user_data['waiting_for_image'] = False

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        logger.info(f"Help command called by {update.effective_user}")
        user = self.session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            await update.message.reply_text(get_text(get_lang(update), 'start_first'))
            return
            
        await update.message.reply_text(
            get_text(get_lang(update), 'help'),
            parse_mode='Markdown',
            disable_web_page_preview=True
        )

    async def stat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stat command - show statistics for admin"""
        logger.info(f"Admin ID: {self.admin_id}")
        if update.effective_user.id != self.admin_id:
            #await update.message.reply_text("❌ Access denied")
            return

        # Get all users with their track counts
        users = self.session.query(User).all()
        stats = []
        
        for user in users:
            username = user.username or 'Unknown'
            # Escape underscores in username for Markdown
            escaped_username = username.replace('_', '\\_')
            track_count = self.session.query(Track).filter_by(user_id=user.id).count()
            
            # Calculate total disk space used using utility function
            total_size = calculate_user_storage(user.uuid)
            
            stats.append(get_text(get_lang(update), 'stats_item',
                username=escaped_username,
                user_id=user.telegram_id,
                track_count=track_count,
                storage=format_size(total_size)
            ))
        
        if not stats:
            await update.message.reply_text(get_text(get_lang(update), 'no_users'))
            return
            
        await update.message.reply_text(
            get_text(get_lang(update), 'stats', stats='\n'.join(stats)),
            parse_mode='Markdown'
        ) 