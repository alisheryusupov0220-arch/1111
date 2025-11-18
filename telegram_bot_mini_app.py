#!/usr/bin/env python3
"""
Добавление кнопки Mini App в Telegram бот
Вставь этот код в свой telegram_bot.py
"""

from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

# ========== ЗАМЕНИ URL НА СВОЙ! ==========
MINI_APP_URL = "https://твой-username.github.io/finance-mini-app/mini_app.html"
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню с кнопкой Mini App"""
    
    keyboard = [
        [
            # КНОПКА MINI APP ⭐
            KeyboardButton(
                "📱 Создать отчёт",
                web_app=WebAppInfo(url=MINI_APP_URL)
            )
        ],
        ["💰 Балансы", "📊 Отчёты"],
        ["⚙️ Настройки"]
    ]
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    await update.message.reply_text(
        "👋 Добро пожаловать!\n\n"
        "Нажмите '📱 Создать отчёт' для заполнения дневного отчёта",
        reply_markup=reply_markup
    )


# Альтернативный вариант - через InlineKeyboard
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def show_mini_app_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Открыть Mini App через inline кнопку"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                "📱 Открыть форму отчёта",
                web_app=WebAppInfo(url=MINI_APP_URL)
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Нажмите кнопку ниже для создания отчёта:",
        reply_markup=reply_markup
    )


# ========== ПРИМЕР ПОЛНОГО БОТА ==========

from telegram.ext import Application, CommandHandler, MessageHandler, filters

def main():
    """Запуск бота"""
    
    # Твой токен
    TOKEN = "YOUR_BOT_TOKEN"
    
    # Создаём приложение
    app = Application.builder().token(TOKEN).build()
    
    # Обработчики
    app.add_handler(CommandHandler("start", start))
    
    # Запускаем
    print("🤖 Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
