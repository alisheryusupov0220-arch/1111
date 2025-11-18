#!/bin/bash
# Этот скрипт автоматически активирует venv и запускает бота

# 1. Активировать venv
echo "Активация venv..."
source venv/bin/activate

# 2. Запустить бота
echo "Запуск бота (Нажмите Ctrl+C для остановки)..."
python3 telegram_bot.py

# 3. Деактивировать (когда бот остановится)
echo "Бот остановлен. Деактивация venv."
deactivate
