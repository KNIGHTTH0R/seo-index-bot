export BOT_CONTAINER_NAME=bot
docker exec ${BOT_CONTAINER_NAME} alembic upgrade head