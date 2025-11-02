#!/bin/bash

# Цветной вывод
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Exchange Bot - Запуск ===${NC}\n"

# Проверка наличия .env
if [ ! -f .env ]; then
    echo -e "${RED}Ошибка: Файл .env не найден!${NC}"
    echo -e "${YELLOW}Пожалуйста, создайте файл .env и заполните необходимые переменные.${NC}"
    exit 1
fi

# Проверка наличия BOT_TOKEN
if ! grep -q "BOT_TOKEN=your_bot_token_here" .env; then
    echo -e "${GREEN}✓ BOT_TOKEN настроен${NC}"
else
    echo -e "${RED}✗ BOT_TOKEN не настроен в .env${NC}"
    echo -e "${YELLOW}Получите токен у @BotFather и укажите в .env${NC}"
    exit 1
fi

# Остановка существующих контейнеров
echo -e "\n${YELLOW}Остановка существующих контейнеров...${NC}"
docker-compose down

# Сборка и запуск
echo -e "\n${GREEN}Сборка и запуск контейнеров...${NC}"
docker-compose up -d --build

# Ожидание запуска
echo -e "\n${YELLOW}Ожидание запуска сервисов...${NC}"
sleep 5

# Проверка статуса
echo -e "\n${GREEN}Статус контейнеров:${NC}"
docker-compose ps

# Просмотр логов
echo -e "\n${GREEN}Логи бота (Ctrl+C для выхода):${NC}"
docker-compose logs -f bot

