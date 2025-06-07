from typing import Dict, Any

class Locale:
    def __init__(self, code: str, name: str, translations: Dict[str, Any]):
        self.code = code
        self.name = name
        self.translations = translations

# English translations
EN = {
    'welcome': (
        "🎙 *Welcome to YouTube to Podcast Bot!*\n\n"
        "I'll help you create your own podcast feed from YouTube videos.\n\n"
        "📝 *Quick Start Guide:*\n"
        "1. Send me any YouTube video URL\n"
        "2. I'll convert it to podcast format\n"
        "3. Add this RSS feed to your podcast app (ex. Apple Podcasts):\n\n"
        " `{rss_url}` \n\n"
        "🎨 *Customization:*\n"
        "• Use /setimage to set your own podcast cover\n"
        "• Use /list to see your videos\n"
        "• Use /delete to remove videos\n\n"
        "❓ Use /help for more information"
    ),
    'help': (
        "🤖 *YouTube to Podcast Bot - Detailed Guide*\n\n"
        "This bot helps you create your own podcast feed from YouTube videos. Here's how to use it:\n\n"
        "📱 *Getting Started*\n"
        "1. Send any YouTube video URL to the bot\n"
        "2. The bot will automatically download and convert it to podcast format\n"
        "3. Add your RSS feed (use /feed command) to your favorite podcast app\n\n"
        "🎨 *Customizing Your Podcast*\n"
        "• Set your own podcast cover using /setimage\n"
        "• The cover will be automatically resized and optimized\n"
        "• You can change the cover anytime\n\n"
        "📋 *Managing Your Content*\n"
        "• Use /list to see all videos in your feed\n"
        "• Use /delete to remove unwanted videos\n"
        "• Videos are processed in high quality (192kbps)\n\n"
        "📝 *Available Commands:*\n"
        "• `/start` - Start the bot and get your RSS feed\n"
        "• `/setimage` - Set your podcast cover image\n"
        "• `/list` - Show list of added videos\n"
        "• `/delete` - Delete video from the list\n"
        "• `/feed` - Get your podcast RSS feed\n"
        "• `/help` - Show this help message\n\n"
        "💡 *Tips*\n"
        "• Your feed updates automatically when you add new videos\n\n"
        "🌐 *Links:*\n"
        "Web: [page on internet](https://app.sboychenko.ru)\n"
        "Author: @sboychenko\\_life"
    ),
    'feed': (
        "🎵 *Your Podcast RSS Feed*\n\n"
        "Add this URL to your podcast app:\n"
        "`{rss_url}`\n\n"
        "*Note:* Make sure to add a cover image using /setimage for better appearance!"
    ),
    'list_empty': (
        "📭 *Your feed is empty*\n\n"
        "Send me a YouTube URL to add your first video!"
    ),
    'list': (
        "📋 *Your Podcast Feed*\n\n"
        "{tracks}\n\n"
        "Use /delete to remove videos from your feed."
    ),
    'delete_invalid': (
        "❌ *Invalid command format*\n\n"
        "Usage: `/delete <number>`\n\n"
        "*Your videos:*\n"
        "{tracks}"
    ),
    'delete_invalid_number': (
        "❌ *Invalid video number*\n\n"
        "Please choose a number from the list:\n"
        "{tracks}"
    ),
    'delete_success': (
        "✅ *Video deleted successfully!*\n\n"
        "Removed: *{title}*"
    ),
    'setimage_prompt': (
        "🖼 *Send me an image to use as your podcast cover*\n\n"
        "The image will be resized and text will be added automatically."
    ),
    'setimage_success': (
        "✅ *Image set as podcast cover!*\n\n"
        "Your podcast feed will now show this image as the cover."
    ),
    'setimage_error': (
        "❌ *Error setting image*\n\n"
        "Please try again or use a different image."
    ),
    'download_start': "Downloading and processing your video...",
    'download_success': "Successfully added '{title}' to your podcast feed!",
    'download_error': "Error processing video: {error}",
    'start_first': "❌ Please use /start first",
    'new_user_notification': (
        "🆕 *New User Joined*\n\n"
        "👤 User: @{username}\n"
        "🆔 ID: `{user_id}`"
    ),
    'stats': (
        "📊 *Bot Statistics*\n\n"
        "{stats}"
    ),
    'no_users': "No users found",
    'track_item': "{number}. {title} - [(YouTube)]({url})",
    'stats_item': (
        "👤 @{username} (ID: {user_id}):\n"
        "   • Tracks: {track_count}\n"
        "   • Storage: {storage}"
    )
}

# Russian translations
RU = {
    'welcome': (
        "🎙 *Добро пожаловать в YouTube to Podcast Bot!*\n\n"
        "Я помогу вам создать свой подкаст из видео с YouTube.\n\n"
        "📝 *Краткое руководство:*\n"
        "1. Отправьте мне ссылку на видео с YouTube\n"
        "2. Я конвертирую его в формат подкаста\n"
        "3. Добавьте эту RSS-ленту в приложение для подкастов (например, Apple Podcasts):\n\n"
        " `{rss_url}` \n\n"
        "🎨 *Настройка:*\n"
        "• Используйте /setimage для установки обложки подкаста\n"
        "• Используйте /list для просмотра видео\n"
        "• Используйте /delete для удаления видео\n\n"
        "❓ Используйте /help для получения подробной информации"
    ),
    'help': (
        "🤖 *YouTube to Podcast Bot - Подробное руководство*\n\n"
        "Этот бот помогает создать свой подкаст из видео с YouTube. Вот как им пользоваться:\n\n"
        "📱 *Начало работы*\n"
        "1. Отправьте ссылку на видео с YouTube\n"
        "2. Бот автоматически скачает и конвертирует его в формат подкаста\n"
        "3. Добавьте вашу RSS-ленту (команда /feed) в любимое приложение для подкастов\n\n"
        "🎨 *Настройка подкаста*\n"
        "• Установите свою обложку с помощью /setimage\n"
        "• Обложка будет автоматически оптимизирована\n"
        "• Вы можете изменить обложку в любое время\n\n"
        "📋 *Управление контентом*\n"
        "• Используйте /list для просмотра всех видео\n"
        "• Используйте /delete для удаления ненужных видео\n"
        "• Видео обрабатываются в высоком качестве (192kbps)\n\n"
        "📝 *Доступные команды:*\n"
        "• `/start` - Начать работу с ботом и получить RSS-ленту\n"
        "• `/setimage` - Установить обложку подкаста\n"
        "• `/list` - Показать список добавленных видео\n"
        "• `/delete` - Удалить видео из списка\n"
        "• `/feed` - Получить RSS-ленту подкаста\n"
        "• `/help` - Показать это сообщение\n\n"
        "💡 *Советы*\n"
        "• Ваша лента обновляется автоматически при добавлении новых видео\n\n"
        "🌐 *Ссылки:*\n"
        "Сайт: [страница в интернете](https://app.sboychenko.ru)\n"
        "Автор: @sboychenko\\_life"
    ),
    'feed': (
        "🎵 *Ваша RSS-лента подкаста*\n\n"
        "Добавьте этот URL в приложение для подкастов:\n"
        "`{rss_url}`\n\n"
        "*Примечание:* Не забудьте добавить обложку через /setimage для лучшего отображения!"
    ),
    'list_empty': (
        "📭 *Ваша лента пуста*\n\n"
        "Отправьте мне ссылку на YouTube, чтобы добавить первое видео!"
    ),
    'list': (
        "📋 *Ваш подкаст*\n\n"
        "{tracks}\n\n"
        "Используйте /delete для удаления видео из ленты."
    ),
    'delete_invalid': (
        "❌ *Неверный формат команды*\n\n"
        "Использование: `/delete <номер>`\n\n"
        "*Ваши видео:*\n"
        "{tracks}"
    ),
    'delete_invalid_number': (
        "❌ *Неверный номер видео*\n\n"
        "Пожалуйста, выберите номер из списка:\n"
        "{tracks}"
    ),
    'delete_success': (
        "✅ *Видео успешно удалено!*\n\n"
        "Удалено: *{title}*"
    ),
    'setimage_prompt': (
        "🖼 *Отправьте мне изображение для обложки подкаста*\n\n"
        "Изображение будет автоматически обработано и оптимизировано."
    ),
    'setimage_success': (
        "✅ *Обложка подкаста установлена!*\n\n"
        "Ваша RSS-лента теперь будет отображать эту обложку."
    ),
    'setimage_error': (
        "❌ *Ошибка установки обложки*\n\n"
        "Пожалуйста, попробуйте еще раз или используйте другое изображение."
    ),
    'download_start': "Скачиваю и обрабатываю ваше видео...",
    'download_success': "Видео '{title}' успешно добавлено в ваш подкаст!",
    'download_error': "Ошибка обработки видео: {error}",
    'start_first': "❌ Пожалуйста, сначала используйте /start",
    'new_user_notification': (
        "🆕 *Новый пользователь*\n\n"
        "👤 Пользователь: @{username}\n"
        "🆔 ID: `{user_id}`"
    ),
    'stats': (
        "📊 *Статистика бота*\n\n"
        "{stats}"
    ),
    'no_users': "Пользователи не найдены",
    'track_item': "{number}. {title} - [(YouTube)]({url})",
    'stats_item': (
        "👤 @{username} (ID: {user_id}):\n"
        "   • Треков: {track_count}\n"
        "   • Место: {storage}"
    )
}

# Available locales
LOCALES = {
    'en': Locale('en', 'English', EN),
    'ru': Locale('ru', 'Русский', RU)
}

def get_locale(language_code: str) -> Locale:
    """Get locale by language code, fallback to English if not found"""
    return LOCALES.get(language_code, LOCALES['en'])

def get_text(language_code: str, key: str, **kwargs) -> str:
    """Get localized text by key with optional formatting"""
    locale = get_locale(language_code)
    text = locale.translations.get(key, LOCALES['en'].translations.get(key, key))
    return text.format(**kwargs) if kwargs else text 