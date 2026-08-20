from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, create_engine, inspect, text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
import logging
import uuid

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    uuid = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    image = Column(Boolean, nullable=False, default=False)
    tracks = relationship("Track", back_populates="user", cascade="all, delete-orphan")

class Track(Base):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    youtube_url = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    duration = Column(String)
    channel_name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    user = relationship("User", back_populates="tracks")

def _add_missing_columns(engine):
    """Add columns that exist in the models but not yet in the database.

    Only handles additive, nullable columns (the common case when extending a
    model). Anything else - renames, type changes, NOT NULL/default changes,
    dropped columns - still needs a manual entry in migrations/migration.md.
    """
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            existing_columns = {col['name'] for col in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing_columns:
                    continue
                col_type = column.type.compile(dialect=engine.dialect)
                logger.info(f"Auto-migration: adding column {table.name}.{column.name} ({col_type})")
                conn.execute(text(f'ALTER TABLE {table.name} ADD COLUMN {column.name} {col_type}'))

def init_db(database_url):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    _add_missing_columns(engine)
    return engine