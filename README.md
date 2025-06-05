# YouTube to Podcast Converter

This project converts YouTube videos to podcast episodes through a Telegram bot. It creates a personal RSS feed for each user that can be added to any podcast player.

## Features

- Telegram bot for easy interaction
- YouTube video to MP3 conversion
- Personal RSS feed for each user
- Track management (list, delete)
- Docker deployment

## Setup

### Docker Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your values:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
   - `DOMAIN`: Your domain name for RSS feed generation
   - `DATABASE_URL`: PostgreSQL connection string (default is fine for local development)

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

### Local Development Setup

1. Clone the repository
2. Create and activate a virtual environment with Python 3.13:
```bash
# On macOS with Homebrew
brew install python@3.13
python3.13 -m venv venv

# On Ubuntu/Debian
sudo apt-get install python3.13 python3.13-venv
python3.13 -m venv venv

# On Windows
# Download and install Python 3.13 from https://www.python.org/downloads/
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install system dependencies:

#### On macOS:
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required packages
brew install ffmpeg rust openssl

# Install Docker if not installed
brew install --cask docker

# Set up environment variables for psycopg2 build
export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib -L/opt/homebrew/opt/postgresql@15/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include -I/opt/homebrew/opt/postgresql@15/include"
```

#### On Ubuntu/Debian:
```bash
sudo apt-get update && sudo apt-get install -y \
    ffmpeg \
    python3-dev \
    build-essential \
    rustc \
    cargo \
    libpq-dev \
    libssl-dev

# Install Docker if not installed
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

#### On Windows:
- Install FFmpeg from https://ffmpeg.org/download.html
- Install Docker Desktop from https://www.docker.com/products/docker-desktop
- Install Rust from https://rustup.rs/

4. Start PostgreSQL in Docker:
```bash
docker-compose -f docker-compose.dev.yml up -d
```

5. Install Python dependencies:
```bash
# Upgrade pip and install wheel
pip install --upgrade pip wheel

# Install build tools
pip install --upgrade setuptools build

# Install psycopg2-binary instead of psycopg2
pip install psycopg2-binary

# Install other dependencies
pip install -r requirements.txt
```

6. Copy `.env.example` to `.env` and fill in your values:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
   - `DOMAIN`: Your domain name for RSS feed generation (use `localhost:8000` for local development)
   - `DATABASE_URL`: Use `postgresql://postgres:postgres@localhost:5432/podcast` for local development

7. Run the application:
```bash
python main.py
```

8. To stop PostgreSQL when done:
```bash
docker-compose -f docker-compose.dev.yml down
```

## Troubleshooting

### Common Issues

1. **Error building psycopg2**
   - On macOS, make sure you have set the environment variables:
     ```bash
     export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib -L/opt/homebrew/opt/postgresql@15/lib"
     export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include -I/opt/homebrew/opt/postgresql@15/include"
     ```
   - Try using psycopg2-binary instead:
     ```bash
     pip uninstall psycopg2
     pip install psycopg2-binary
     ```
   - Make sure PostgreSQL is installed:
     ```bash
     brew install postgresql@15
     ```

2. **PostgreSQL connection issues**
   - Check if PostgreSQL container is running:
     ```bash
     docker ps
     ```
   - Verify connection string in .env file
   - Try connecting with psql:
     ```bash
     docker exec -it youtube-to-podcast-db-1 psql -U postgres -d podcast
     ```

3. **FFmpeg not found**
   - Verify FFmpeg installation:
     ```bash
     ffmpeg -version
     ```
   - Make sure FFmpeg is in your PATH

## Usage

1. Start a chat with your Telegram bot
2. Send `/start` to create your personal feed
3. Send any YouTube URL to convert it to a podcast episode
4. Use `/feed` to get your RSS feed URL
5. Use `/list` to see your episodes
6. Use `/delete <number>` to remove an episode

## Development

The project consists of two main components:

1. Telegram Bot (`bot.py`):
   - Handles user interactions
   - Downloads and processes YouTube videos
   - Manages user data and tracks

2. FastAPI Server (`server.py`):
   - Generates RSS feeds
   - Serves audio files
   - Handles API endpoints

## Requirements

- Python 3.13
- Docker and Docker Compose
- FFmpeg
- Rust (for building some Python packages)


## Nginx
```
sudo nginx -t
sudo systemctl reload nginx
```


## DB
Зайти внутрь контейнера
Найдите имя контейнера:
```
docker ps
```

Подключитесь к контейнеру:
```
docker exec -it <container_name> bash
```

Внутри контейнера выполните:
```
psql -U postgres123 -d podcast
```