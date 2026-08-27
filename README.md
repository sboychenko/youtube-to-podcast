# YouTube в Подкаст — бот для Telegram

Проект превращает видео с YouTube в эпизоды подкаста через Telegram-бота. Для каждого пользователя создаётся
персональная RSS-лента, которую можно добавить в любой подкаст-плеер.

## Возможности

- Telegram-бот для удобного взаимодействия
- Конвертация видео с YouTube в MP3
- Персональная RSS-лента для каждого пользователя
- Управление эпизодами (список, удаление)
- Развёртывание в Docker

## Установка

### Установка через Docker

1. Склонируйте репозиторий
2. Скопируйте `.env.example` в `.env` и заполните значения:
   - `TELEGRAM_BOT_TOKEN` — токен вашего Telegram-бота от @BotFather
   - `DOMAIN` — доменное имя для генерации RSS-ленты
   - `DATABASE_URL` — строка подключения к PostgreSQL (значение по умолчанию подходит для локальной разработки)

3. Соберите и запустите через Docker Compose:
```bash
docker-compose up --build
```

### Локальная разработка

1. Склонируйте репозиторий
2. Создайте и активируйте виртуальное окружение с Python 3.13:
```bash
# На macOS с Homebrew
brew install python@3.13
python3.13 -m venv venv

# На Ubuntu/Debian
sudo apt-get install python3.13 python3.13-venv
python3.13 -m venv venv

# На Windows
# Скачайте и установите Python 3.13 с https://www.python.org/downloads/
python -m venv venv

# Активация виртуального окружения
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установите системные зависимости:

#### На macOS:
```bash
# Установите Homebrew, если ещё не установлен
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установите необходимые пакеты
brew install ffmpeg rust openssl

# Установите Docker, если ещё не установлен
brew install --cask docker

# Задайте переменные окружения для сборки psycopg2
export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib -L/opt/homebrew/opt/postgresql@15/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include -I/opt/homebrew/opt/postgresql@15/include"
```

#### На Ubuntu/Debian:
```bash
sudo apt-get update && sudo apt-get install -y \
    ffmpeg \
    python3-dev \
    build-essential \
    rustc \
    cargo \
    libpq-dev \
    libssl-dev

# Установите Docker, если ещё не установлен
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

#### На Windows:
- Установите FFmpeg с https://ffmpeg.org/download.html
- Установите Docker Desktop с https://www.docker.com/products/docker-desktop
- Установите Rust с https://rustup.rs/

4. Запустите PostgreSQL в Docker:
```bash
docker-compose -f docker-compose.dev.yml up -d
```

5. Установите Python-зависимости:
```bash
# Обновите pip и установите wheel
pip install --upgrade pip wheel

# Установите инструменты сборки
pip install --upgrade setuptools build

# Установите psycopg2-binary вместо psycopg2
pip install psycopg2-binary

# Установите остальные зависимости
pip install -r requirements.txt
```

6. Скопируйте `.env.example` в `.env` и заполните значения:
   - `TELEGRAM_BOT_TOKEN` — токен вашего Telegram-бота от @BotFather
   - `DOMAIN` — доменное имя для генерации RSS-ленты (для локальной разработки используйте `localhost:8000`)
   - `DATABASE_URL` — для локальной разработки используйте `postgresql://postgres:postgres@localhost:5432/podcast`

7. Запустите приложение:
```bash
python main.py
```

8. Чтобы остановить PostgreSQL по завершении работы:
```bash
docker-compose -f docker-compose.dev.yml down
```

## Решение проблем

### Частые проблемы

1. **Ошибка при сборке psycopg2**
   - На macOS убедитесь, что заданы переменные окружения:
     ```bash
     export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib -L/opt/homebrew/opt/postgresql@15/lib"
     export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include -I/opt/homebrew/opt/postgresql@15/include"
     ```
   - Попробуйте использовать psycopg2-binary вместо psycopg2:
     ```bash
     pip uninstall psycopg2
     pip install psycopg2-binary
     ```
   - Убедитесь, что PostgreSQL установлен:
     ```bash
     brew install postgresql@15
     ```

2. **Проблемы с подключением к PostgreSQL**
   - Проверьте, запущен ли контейнер PostgreSQL:
     ```bash
     docker ps
     ```
   - Проверьте строку подключения в файле .env
   - Попробуйте подключиться через psql:
     ```bash
     docker exec -it youtube-to-podcast-db-1 psql -U postgres -d podcast
     ```

3. **FFmpeg не найден**
   - Проверьте установку FFmpeg:
     ```bash
     ffmpeg -version
     ```
   - Убедитесь, что FFmpeg добавлен в PATH

4. **Ошибка `Sign in to confirm you're not a bot`**
   - YouTube требует подтверждения, что запрос не от бота — обычно это происходит с IP облачных/VPS-провайдеров.
   - Решение: экспортировать cookies из авторизованного в YouTube браузера (например, расширением
     [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc))
     и положить файл на сервер в `data/cookies.txt` (рядом с остальными данными пользователей — том уже
     примонтирован в `/app/data`, перезапуск контейнера не потребуется).
   - Подробнее: [yt-dlp FAQ про cookies](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp).

5. **Ошибка `The page needs to be reloaded`**
   - Известный баг на стороне YouTube (принудительный SABR-стриминг), из-за которого старые версии yt-dlp падают с
     этой ошибкой; иногда ошибка остаётся нестабильной даже на свежей версии.
   - В `requirements.txt` версия yt-dlp указана как нижняя граница (`>=`) без верхней — но GitHub Actions кэширует
     слои Docker-сборки (`cache-from/cache-to: type=gha`), поэтому слой `pip install` может не переустанавливаться
     месяцами, пока содержимое `requirements.txt` не изменится. Если ошибка вернулась — поднимите версию в
     `requirements.txt` (даже на дату той же версии, что уже стоит, — главное, чтобы строка изменилась) и запушьте,
     это форсирует пересборку с актуальным yt-dlp.
   - Проверить версию в уже запущенном контейнере:
     ```bash
     docker exec -it youtube-to-podcast-bot_app_1 pip show yt-dlp
     ```

## Использование

1. Начните чат с вашим Telegram-ботом
2. Отправьте `/start`, чтобы создать свою персональную ленту
3. Отправьте любую ссылку на YouTube, чтобы преобразовать её в эпизод подкаста
4. Используйте `/feed`, чтобы получить URL своей RSS-ленты
5. Используйте `/list`, чтобы посмотреть свои эпизоды
6. Используйте `/delete <номер>`, чтобы удалить эпизод

## Разработка

Проект состоит из двух основных компонентов:

1. Telegram-бот (`bot.py`):
   - Обрабатывает взаимодействия с пользователем
   - Скачивает и обрабатывает видео с YouTube
   - Управляет данными пользователей и эпизодами

2. FastAPI-сервер (`server.py`):
   - Генерирует RSS-ленты
   - Раздаёт аудиофайлы
   - Обрабатывает API-запросы

## Требования

- Python 3.13
- Docker и Docker Compose
- FFmpeg
- Rust (для сборки некоторых Python-пакетов)


## CI/CD

При пуше в `main` GitHub Actions ([.github/workflows/deploy.yml](.github/workflows/deploy.yml)) собирает Docker-образ,
пушит его в GitHub Container Registry (`ghcr.io/sboychenko/youtube-to-podcast`) и разворачивает на VPS по SSH через
`docker-compose`. В pull request'ах и других ветках выполняется только проверка синтаксиса и сборки образа, без
публикации и деплоя.

Для автодеплоя нужно один раз добавить в **Settings → Secrets and variables → Actions** секреты:

- `REMOTE_HOST` — адрес VPS
- `REMOTE_USER` — пользователь для SSH
- `REMOTE_KEY` — приватный SSH-ключ (содержимое файла, не путь)

Значения можно взять из `.env`, который уже используется скриптом `deploy.sh`.

На сервере в `~/youtube-to-podcast-bot` должны лежать `docker-compose.yml` и `.env` (workflow их не создаёт и не
перезаписывает, только выполняет `docker-compose pull app && docker-compose up -d`). Директория `~/youtube-to-podcast-bot/data`
и volume `postgres_data` переживают передеплой.

Ручной деплой через `deploy.sh` (сборка образа локально, `scp` + `docker load` на сервере) продолжает работать и может
использоваться как запасной вариант, если недоступен GHCR.

## Nginx
```
sudo nginx -t
sudo systemctl reload nginx
nginx -s reload
tail -f /var/log/nginx/error.log
```


## БД

Физические файлы базы Postgres лежат в `./data/postgres` (bind-mount, не Docker volume) — рядом с `./data`, где
хранятся аудио и обложки. При первом запуске каталог должен принадлежать пользователю `postgres` из образа
`postgres:15` (uid/gid `999`), иначе контейнер упадёт с ошибкой прав доступа:
```
mkdir -p data/postgres
sudo chown -R 999:999 data/postgres
```

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

Смотреть логи
```
docker ps
docker logs -f -t youtube-to-podcast-bot_app_1
```
