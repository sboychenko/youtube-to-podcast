#!/bin/bash
# Загрузка переменных окружения
source .env.prod

# Конфигурация
IMAGE_NAME="youtube-to-podcast-bot"
CONTAINER_NAME="youtube-to-podcast-bot"
REMOTE_DIR="~/youtube-to-podcast-bot"
COMPOSE_FILE="docker-compose.yml"

# Проверка наличия необходимых переменных
if [ -z "$REMOTE_HOST" ] || [ -z "$REMOTE_USER" ] || [ -z "$REMOTE_KEY" ]; then
    echo "Error: Missing required environment variables"
    echo "Please check your .env file and ensure REMOTE_HOST, REMOTE_USER and REMOTE_KEY are set"
    exit 1
fi

# Проверка наличия docker-compose файла
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "Error: $COMPOSE_FILE not found"
    exit 1
fi

# Сборка образа
echo "Building Docker image..."
docker build -t $IMAGE_NAME .

# Сохранение образа в tar архив
echo "Saving Docker image..."
docker save $IMAGE_NAME | gzip > $IMAGE_NAME.tar.gz

# Показать размер файла
echo "Archive size:"
ls -lh $IMAGE_NAME.tar.gz

# Отправка архива и docker-compose.yml на сервер
echo "Uploading files to server..."
scp -i $REMOTE_KEY $IMAGE_NAME.tar.gz $COMPOSE_FILE $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/

# Выполнение команд на сервере
echo "Deploying on server..."
ssh -i $REMOTE_KEY $REMOTE_USER@$REMOTE_HOST << EOF
    cd $REMOTE_DIR
    
    # Загрузка нового образа
    docker load < $IMAGE_NAME.tar.gz
    
    # Остановка и удаление старых контейнеров
    docker-compose -f $COMPOSE_FILE down
    
    # Запуск новых контейнеров
    docker-compose -f $COMPOSE_FILE up -d
    
    # Проверка статуса контейнеров
    docker-compose -f $COMPOSE_FILE ps

    rm $IMAGE_NAME.tar.gz
    docker image prune -f
EOF

# Очистка локальных файлов
echo "Cleaning up..."
rm $IMAGE_NAME.tar.gz

echo "Deployment completed!" 