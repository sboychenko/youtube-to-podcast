from PIL import Image, ImageDraw, ImageFont
import io
import os

def process_podcast_cover(image: bytes, username: str) -> bytes:
    """
    Process podcast cover image: resize, add text and background.
    Args:
        image: Original image bytes
        username: Username to add to the cover
    Returns:
        Processed image as bytes
    """
    # Open image with Pillow
    image = Image.open(io.BytesIO(image))
    target_size = 512
    ratio = min(target_size / image.width, target_size / image.height)
    new_size = (int(image.width * ratio), int(image.height * ratio))
    image = image.resize(new_size, Image.Resampling.LANCZOS)
    image_with_text = image.copy().convert('RGBA')
    draw = ImageDraw.Draw(image_with_text)

    text = f"Feed by {username}"
    target_text_width = image.width * 0.8

    # Try to load Arial, fallback to default
    def get_font(size):
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except IOError:
            return ImageFont.load_default()

    # Binary search for font size
    min_size, max_size = 10, 200
    font = get_font(min_size)
    while min_size < max_size:
        mid = (min_size + max_size) // 2
        font = get_font(mid)
        text_width = draw.textlength(text, font=font)
        if text_width < target_text_width:
            min_size = mid + 1
        else:
            max_size = mid
    font = get_font(min_size - 1)
    text_width = draw.textlength(text, font=font)
    text_height = font.getbbox(text)[3] - font.getbbox(text)[1]

    x = (image.width - text_width) // 2
    y = image.height - text_height - 50

    # Draw semi-transparent background
    padding = 10
    background_rect = [x - padding, y - padding, x + text_width + padding, y + text_height + padding]
    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(background_rect, fill=(0, 0, 0, 128))
    image_with_text = Image.alpha_composite(image_with_text, overlay)
    draw = ImageDraw.Draw(image_with_text)

    # Draw text shadow and text
    draw.text((x+2, y+2), text, font=font, fill='black')
    draw.text((x, y), text, font=font, fill='white')

    # Convert back to RGB and to bytes
    result = image_with_text.convert('RGB')
    img_byte_arr = io.BytesIO()
    result.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def calculate_user_storage(user_uuid: str) -> int:
    """Calculate total disk space used by user's audio files
    
    Args:
        user_uuid: User's UUID to find their directory
        
    Returns:
        int: Total size in bytes
    """
    total_size = 0
    user_dir = f"data/{user_uuid}"
    if os.path.exists(user_dir):
        for file in os.listdir(user_dir):
            if file.endswith('.mp3'):
                file_path = os.path.join(user_dir, file)
                total_size += os.path.getsize(file_path)
    return total_size

def format_size(size_bytes: int) -> str:
    """Convert bytes to human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string (e.g. "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} GB"