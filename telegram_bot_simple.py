#!/usr/bin/env python3
"""
Telegram бот для Air Waffle (упрощённая версия)
Работает на python-telegram-bot
"""

import logging
from datetime import date
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from database_v5 import FinanceSystemV5

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ВАЖНО: Замените на ваш токен от @BotFather
BOT_TOKEN = "8188072633:AAE6TavFNHlbyAcfR8Z5Tnsp4jpQsXj1jHw"

db = FinanceSystemV5()

# Состояния разговора
(SELECTING_LOCATION, ENTERING_TOTAL, ENTERING_PAYMENTS, 
 COUNTING_CASH, ENTERING_EXPENSES) = range(5)

# Временное хранилище
user_data = {}

# ========== КЛАВИАТУРЫ ==========

def main_keyboard():
    """Главное меню"""
    keyboard = [
        ['📊 Новый отчёт'],
        ['💰 Балансы', '📋 Помощь']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def locations_keyboard():
    """Клавиатура точек"""
    locations = db.get_locations()
    keyboard = [[loc['name']] for loc in locations]
    keyboard.append(['❌ Отмена'])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def yes_no_keyboard():
    """Да/Нет"""
    keyboard = [['✅ Да', '❌ Нет']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ========== ОБРАБОТЧИКИ ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text(
        f"👋 Привет, {update.effective_user.first_name}!\n\n"
        "Я бот для учёта финансов Air Waffle.\n\n"
        "Выберите действие:",
        reply_markup=main_keyboard()
    )
    return ConversationHandler.END

async def new_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать новый отчёт"""
    user_id = update.effective_user.id
    user_data[user_id] = {
        'date': date.today(),
        'payments': {},
        'payment_index': 0
    }
    
    await update.message.reply_text(
        "📍 Выберите точку продаж:",
        reply_markup=locations_keyboard()
    )
    return SELECTING_LOCATION

async def select_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор точки"""
    if update.message.text == "❌ Отмена":
        await update.message.reply_text("Отменено", reply_markup=main_keyboard())
        return ConversationHandler.END
    
    user_id = update.effective_user.id
    locations = db.get_locations()
    location = next((loc for loc in locations if loc['name'] == update.message.text), None)
    
    if not location:
        await update.message.reply_text("❌ Выберите точку из списка")
        return SELECTING_LOCATION
    
    user_data[user_id]['location_id'] = location['id']
    user_data[user_id]['location_name'] = location['name']
    
    await update.message.reply_text(
        f"📅 Дата: {date.today().strftime('%d.%m.%Y')}\n"
        f"📍 Точка: {location['name']}\n\n"
        "💰 Введите общую сумму продаж с учётом скидок:",
        reply_markup=ReplyKeyboardRemove()
    )
    return ENTERING_TOTAL

async def enter_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод общей суммы"""
    try:
        total_sales = float(update.message.text.replace(',', '').replace(' ', ''))
        if total_sales <= 0:
            await update.message.reply_text("❌ Сумма должна быть больше 0")
            return ENTERING_TOTAL
        
        user_id = update.effective_user.id
        user_data[user_id]['total_sales'] = total_sales
        
        # Создаём отчёт
        report_id = db.create_daily_report(
            date.today(),
            user_data[user_id]['location_id'],
            total_sales,
            update.effective_user.username
        )
        user_data[user_id]['report_id'] = report_id
        
        # Получаем методы оплаты
        user_data[user_id]['payment_methods'] = db.get_payment_methods()
        user_data[user_id]['payment_index'] = 0
        user_data[user_id]['total_cashless'] = 0
        
        await ask_payment(update, user_id)
        return ENTERING_PAYMENTS
    
    except ValueError:
        await update.message.reply_text("❌ Введите корректное число")
        return ENTERING_TOTAL

async def ask_payment(update: Update, user_id: int):
    """Запросить платёж"""
    idx = user_data[user_id]['payment_index']
    methods = user_data[user_id]['payment_methods']
    
    if idx >= len(methods):
        await finalize_payments(update, user_id)
        return
    
    method = methods[idx]
    emoji = {'terminal': '📟', 'online': '🌐', 'delivery': '🚚'}.get(method['method_type'], '💳')
    
    await update.message.reply_text(
        f"{emoji} {method['name']}\n"
        f"Комиссия: {method['commission_percent']}%\n\n"
        f"Введите сумму или 0 для пропуска:"
    )

async def enter_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод платежа"""
    user_id = update.effective_user.id
    
    try:
        amount = float(update.message.text.replace(',', '').replace(' ', ''))
        
        if amount > 0:
            idx = user_data[user_id]['payment_index']
            method = user_data[user_id]['payment_methods'][idx]
            
            db.add_report_payment(
                user_data[user_id]['report_id'],
                method['id'],
                method['default_account_id'],
                amount
            )
            
            net = amount * (1 - method['commission_percent']/100)
            user_data[user_id]['total_cashless'] += amount
            
            await update.message.reply_text(f"✅ {amount:,.0f} → {net:,.0f} сум")
        
        user_data[user_id]['payment_index'] += 1
        await ask_payment(update, user_id)
        return ENTERING_PAYMENTS
    
    except ValueError:
        await update.message.reply_text("❌ Введите число")
        return ENTERING_PAYMENTS

async def finalize_payments(update: Update, user_id: int):
    """Завершить платежи"""
    total_sales = user_data[user_id]['total_sales']
    total_cashless = user_data[user_id]['total_cashless']
    cash_expected = total_sales - total_cashless
    
    user_data[user_id]['cash_expected'] = cash_expected
    
    await update.message.reply_text(
        f"📊 ИТОГО:\n"
        f"Общая сумма: {total_sales:,.0f} сум\n"
        f"Безнал: {total_cashless:,.0f} сум\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 Наличных по отчёту: {cash_expected:,.0f} сум\n\n"
        f"Введите фактическую сумму наличных в кассе:"
    )

async def count_cash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подсчёт наличных"""
    try:
        cash_actual = float(update.message.text.replace(',', '').replace(' ', ''))
        user_id = update.effective_user.id
        
        cash_expected = user_data[user_id]['cash_expected']
        cash_difference = cash_actual - cash_expected
        
        # Сохраняем
        db.update_report_cash(
            user_data[user_id]['report_id'],
            cash_expected,
            cash_actual,
            {}
        )
        
        if cash_difference > 0:
            diff_text = f"✅ ИЗЛИШЕК: +{cash_difference:,.0f} сум"
        elif cash_difference < 0:
            diff_text = f"⚠️ НЕДОСТАЧА: {cash_difference:,.0f} сум"
        else:
            diff_text = f"✅ БЕЗ РАСХОЖДЕНИЙ"
        
        await update.message.reply_text(
            f"💵 СВЕРКА:\n"
            f"По отчёту: {cash_expected:,.0f} сум\n"
            f"Фактически: {cash_actual:,.0f} сум\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{diff_text}\n\n"
            f"Добавить расходы?",
            reply_markup=yes_no_keyboard()
        )
        
        user_data[user_id]['cash_difference'] = cash_difference
        return ENTERING_EXPENSES
    
    except ValueError:
        await update.message.reply_text("❌ Введите число")
        return COUNTING_CASH

async def ask_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Спросить про расходы"""
    if update.message.text == "❌ Нет":
        return await finish_report(update, context)
    
    await update.message.reply_text(
        "💸 Отправьте расход в формате:\n"
        "<b>Сумма | Описание</b>\n\n"
        "Например: 150000 | Закупка овощей\n\n"
        "Или /done когда закончите",
        parse_mode='HTML'
    )
    return ENTERING_EXPENSES

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить расход"""
    if update.message.text == '/done':
        return await finish_report(update, context)
    
    user_id = update.effective_user.id
    
    try:
        parts = update.message.text.split('|')
        if len(parts) != 2:
            await update.message.reply_text("❌ Формат: Сумма | Описание")
            return ENTERING_EXPENSES
        
        amount = float(parts[0].strip().replace(',', '').replace(' ', ''))
        description = parts[1].strip()
        
        cash_accounts = db.get_accounts('cash')
        if cash_accounts:
            db.add_report_expense(
                user_data[user_id]['report_id'],
                cash_accounts[0]['id'],
                amount,
                None,
                description
            )
            
            await update.message.reply_text(f"✅ Расход {amount:,.0f} сум добавлен\n\nЕщё расход? Или /done")
        
        return ENTERING_EXPENSES
    
    except ValueError:
        await update.message.reply_text("❌ Проверьте формат")
        return ENTERING_EXPENSES

async def finish_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершить отчёт"""
    user_id = update.effective_user.id
    
    db.close_report(user_data[user_id]['report_id'])
    
    await update.message.reply_text(
        f"✅ <b>ОТЧЁТ СОХРАНЁН!</b>\n\n"
        f"📅 Дата: {user_data[user_id]['date'].strftime('%d.%m.%Y')}\n"
        f"📍 Точка: {user_data[user_id]['location_name']}\n"
        f"💰 Продажи: {user_data[user_id]['total_sales']:,.0f} сум\n"
        f"💵 Разница: {user_data[user_id]['cash_difference']:+,.0f} сум\n\n"
        f"ID отчёта: {user_data[user_id]['report_id']}",
        parse_mode='HTML',
        reply_markup=main_keyboard()
    )
    
    del user_data[user_id]
    return ConversationHandler.END

async def show_balances(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать балансы"""
    balances = db.get_account_balance()
    
    text = "💰 <b>БАЛАНСЫ СЧЕТОВ</b>\n\n"
    total = 0
    
    for acc_id, data in balances.items():
        emoji = "💵" if data['type'] == 'cash' else "🏦"
        text += f"{emoji} <b>{data['name']}</b>\n"
        text += f"   {data['balance']:,.0f} сум\n\n"
        total += data['balance']
    
    text += f"━━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"<b>ИТОГО: {total:,.0f} сум</b>"
    
    await update.message.reply_text(text, parse_mode='HTML')

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    await update.message.reply_text(
        "ℹ️ <b>ПОМОЩЬ</b>\n\n"
        "<b>Новый отчёт:</b>\n"
        "1. Нажмите '📊 Новый отчёт'\n"
        "2. Выберите точку\n"
        "3. Введите сумму продаж\n"
        "4. Введите суммы по методам оплаты\n"
        "5. Введите фактические наличные\n"
        "6. Добавьте расходы (опционально)\n\n"
        "<b>Балансы:</b>\n"
        "Нажмите '💰 Балансы'",
        parse_mode='HTML'
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена"""
    await update.message.reply_text("Отменено", reply_markup=main_keyboard())
    return ConversationHandler.END

def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler для отчёта
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^📊 Новый отчёт$'), new_report)],
        states={
            SELECTING_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_location)],
            ENTERING_TOTAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_total)],
            ENTERING_PAYMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_payment)],
            COUNTING_CASH: [MessageHandler(filters.TEXT & ~filters.COMMAND, count_cash)],
            ENTERING_EXPENSES: [
                MessageHandler(filters.Regex('^(✅ Да|❌ Нет)$'), ask_expenses),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense),
                CommandHandler('done', finish_report)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.Regex('^💰 Балансы$'), show_balances))
    application.add_handler(MessageHandler(filters.Regex('^📋 Помощь$'), show_help))
    
    print("🤖 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
