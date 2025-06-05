from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from models import User, Track, init_db
import os
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from typing import Optional
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)
app = FastAPI()

# Initialize database and create session factory
engine = init_db(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_rss_feed(user: User, tracks: list[Track], domain: str) -> str:
    rss = ET.Element("rss", version="2.0", 
                    attrib={"xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
                           "xmlns:content": "http://purl.org/rss/1.0/modules/content/"})
    channel = ET.SubElement(rss, "channel")
    
    # Основные теги
    ET.SubElement(channel, "title").text = f"Podcast Feed by @{user.username}"
    ET.SubElement(channel, "link").text = f"https://app.sboychenko.ru/y2p"
    ET.SubElement(channel, "description").text = "Create with tg bot @YouTubeToPodcastBot"
    ET.SubElement(channel, "language").text = "ru-ru"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    # iTunes специфичные теги
    ET.SubElement(channel, "itunes:author").text = f"{user.username}"
    ET.SubElement(channel, "itunes:summary").text = "Create with tg bot @YouTubeToPodcastBot"
    ET.SubElement(channel, "itunes:explicit").text = "no"
    ET.SubElement(channel, "itunes:category", text="Other")
    ET.SubElement(channel, "itunes:owner")
    ET.SubElement(channel.find("itunes:owner"), "itunes:name").text = f"{user.username}"
    #ET.SubElement(channel.find("itunes:owner"), "itunes:email").text = "your-email@example.com"  # Можно добавить в модель User

    # Обложка подкаста
    if user.image:
        image = ET.SubElement(channel, "image")
        ET.SubElement(image, "url").text = f"https://{domain}/image/{user.uuid}.jpg"
        ET.SubElement(image, "title").text = f"Podcast Feed for User {user.telegram_id}"
        ET.SubElement(image, "link").text = f"https://{domain}/rss/{user.uuid}"
        # iTunes обложка
        ET.SubElement(channel, "itunes:image", href=f"https://{domain}/image/{user.uuid}.jpg")

    for track in tracks:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = track.title
        ET.SubElement(item, "link").text = track.youtube_url
        ET.SubElement(item, "description").text = f"Audio from {track.youtube_url}"
        ET.SubElement(item, "pubDate").text = track.created_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
        ET.SubElement(item, "guid").text = track.file_name
        
        # iTunes специфичные теги для каждого эпизода
        ET.SubElement(item, "itunes:author").text = f"{user.username}"
        ET.SubElement(item, "itunes:summary").text = f"Audio from {track.youtube_url}"
        ET.SubElement(item, "itunes:explicit").text = "no"
        ET.SubElement(item, "itunes:duration").text = f"{track.duration}"  # Можно добавить длительность в модель Track
        
        enclosure = ET.SubElement(item, "enclosure")
        enclosure.set("url", f"https://{domain}/audio/{user.uuid}/{track.file_name}")
        enclosure.set("type", "audio/mpeg")
        enclosure.set("length", str(os.path.getsize(f"data/{user.uuid}/{track.file_name}")))

    return ET.tostring(rss, encoding="unicode")

@app.get("/rss/{uuid}")
async def get_rss_feed(uuid: str, db: Session = Depends(get_db)):
    logger.info(f"Received RSS feed request for UUID: {uuid}")
    user = db.query(User).filter_by(uuid=uuid).first()
    if not user:
        logger.error(f"User not found for UUID: {uuid}")
        raise HTTPException(status_code=404, detail="User not found")

    tracks = db.query(Track).filter_by(user_id=user.id).order_by(Track.created_at.desc()).all()
    logger.info(f"Found {len(tracks)} tracks for user {user.telegram_id}")
    
    domain = os.getenv("DOMAIN")
    logger.info(f"Using domain: {domain}")
    
    rss_content = create_rss_feed(user, tracks, domain)
    return Response(content=rss_content, media_type="application/xml")

@app.get("/audio/{user_uuid}/{file_name}")
async def get_audio(user_uuid: str, file_name: str, db: Session = Depends(get_db)):
    """Get audio file"""
    user = db.query(User).filter_by(uuid=user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    track = db.query(Track).filter_by(user_id=user.id, file_name=file_name).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
        
    file_path = f"data/{user_uuid}/{track.file_name}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(file_path)

@app.get("/image/{user_uuid}.jpg")
async def get_user_image(user_uuid: str):
    image_path = f"data/{user_uuid}/image.jpg"
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path, media_type="image/jpeg")