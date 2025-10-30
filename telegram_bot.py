#!/usr/bin/env python3
"""
Telegram бот для системы учёта Air Waffle
Кассир может заполнять отчёты прямо из телефона
"""

import asyncio
import logging
from datetime import date
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from database_v5 import FinanceSystemV5

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# ВАЖНО: Замените на ваш токен от @BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Инициализация
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db = FinanceSystemV5()

# Состояния для заполнения отчёта
class DailyReport(StatesGroup):
    selecting_location = State()
    entering_total_sales = State()
    entering_payments = State()
    counting_cash = State()
    entering_non_sales = State()
    entering_expenses = State()
    confirming = State()

# Временное хранилище данных отчёта
user_reports = {}

# ========== КЛАВИАТУРЫ ==========

def get_main_keyboard():
    """Главное меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Новый отчёт")],
            [KeyboardButton(text="💰 Балансы"), KeyboardButton(text="📋 Мои отчёты")],
            [KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_locations_keyboard():
    """Клавиатура точек"""
    locations = db.get_locations()
    buttons = [[KeyboardButton(text=loc['name'])] for loc in locations]
    buttons.append([KeyboardButton(text="❌ Отмена")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_skip_keyboard():
    """Кнопка пропустить"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⏭️ Пропустить")], [KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )

def get_yes_no_keyboard():
    """Да/Нет"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")]],
        resize_keyboard=True
    )

# ========== ОБРАБОТЧИКИ ==========

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Команда /start"""
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я бот для учёта финансов Air Waffle.\n\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "📊 Новый отчёт")
async def start_new_report(message: types.Message, state: FSMContext):
    """Начать новый отчёт"""
    user_id = message.from_user.id
    user_reports[user_id] = {
        'date': date.today(),
        'payments': {},
        'cash_breakdown': {},
        'non_sales_income': [],
        'expenses': []
    }
    
    await message.answer(
        "📍 Выберите точку продаж:",
        reply_markup=get_locations_keyboard()
    )
    await state.set_state(DailyReport.selecting_location)

@dp.message(DailyReport.selecting_location)
async def select_location(message: types.Message, state: FSMContext):
    """Выбор точки"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено", reply_markup=get_main_keyboard())
        return
    
    user_id = message.from_user.id
    locations = db.get_locations()
    location = next((loc for loc in locations if loc['name'] == message.text), None)
    
    if not location:
        await message.answer("❌ Выберите точку из списка")
        return
    
    user_reports[user_id]['location_id'] = location['id']
    user_reports[user_id]['location_name'] = location['name']
    
    await message.answer(
        f"📅 Дата: {date.today().strftime('%d.%m.%Y')}\n"
        f"📍 Точка: {location['name']}\n\n"
        "💰 Введите общую сумму продаж с учётом скидок:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(DailyReport.entering_total_sales)

@dp.message(DailyReport.entering_total_sales)
async def enter_total_sales(message: types.Message, state: FSMContext):
    """Ввод общей суммы"""
    try:
        total_sales = float(message.text.replace(',', '').replace(' ', ''))
        if total_sales <= 0:
            await message.answer("❌ Сумма должна быть больше 0")
            return
        
        user_id = message.from_user.id
        user_reports[user_id]['total_sales'] = total_sales
        
        # Создаём отчёт в БД
        report_id = db.create_daily_report(
            date.today(),
            user_reports[user_id]['location_id'],
            total_sales,
            message.from_user.username
        )
        user_reports[user_id]['report_id'] = report_id
        
        # Начинаем сбор платежей
        user_reports[user_id]['current_payment_index'] = 0
        user_reports[user_id]['payment_methods'] = db.get_payment_methods()
        
        await ask_next_payment(message, user_id)
        await state.set_state(DailyReport.entering_payments)
    
    except ValueError:
        await message.answer("❌ Введите корректное число")

async def ask_next_payment(message: types.Message, user_id: int):
    """Запросить следующий метод оплаты"""
    idx = user_reports[user_id]['current_payment_index']
    methods = user_reports[user_id]['payment_methods']
    
    if idx >= len(methods):
        # Все методы введены
        await finalize_payments(message, user_id)
        return
    
    method = methods[idx]
    type_emoji = {'terminal': '📟', 'online': '🌐', 'delivery': '🚚'}
    emoji = type_emoji.get(method['method_type'], '💳')
    
    await message.answer(
        f"{emoji} {method['name']}\n"
        f"Комиссия: {method['commission_percent']}%\n\n"
        f"Введите сумму (или 0 для пропуска):",
        reply_markup=get_skip_keyboard()
    )

@dp.message(DailyReport.entering_payments)
async def enter_payment(message: types.Message, state: FSMContext):
    """Ввод платежа"""
    user_id = message.from_user.id
    
    if message.text == "⏭️ Пропустить":
        user_reports[user_id]['current_payment_index'] += 1
        await ask_next_payment(message, user_id)
        return
    
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено", reply_markup=get_main_keyboard())
        return
    
    try:
        amount = float(message.text.replace(',', '').replace(' ', ''))
        
        if amount > 0:
            idx = user_reports[user_id]['current_payment_index']
            method = user_reports[user_id]['payment_methods'][idx]
            
            # Сохраняем в БД
            db.add_report_payment(
                user_reports[user_id]['report_id'],
                method['id'],
                method['default_account_id'],
                amount
            )
            
            net = amount * (1 - method['commission_percent']/100)
            user_reports[user_id]['payments'][method['name']] = {
                'amount': amount,
                'net': net
            }
            
            await message.answer(f"✅ {amount:,.0f} → {net:,.0f} сум")
        
        user_reports[user_id]['current_payment_index'] += 1
        await ask_next_payment(message, user_id)
    
    except ValueError:
        await message.answer("❌ Введите корректное число")

async def finalize_payments(message: types.Message, user_id: int):
    """Завершить ввод платежей"""
    total_sales = user_reports[user_id]['total_sales']
    total_cashless = sum(p['amount'] for p in user_reports[user_id]['payments'].values())
    cash_expected = total_sales - total_cashless
    
    user_reports[user_id]['cash_expected'] = cash_expected
    user_reports[user_id]['total_cashless'] = total_cashless
    
    await message.answer(
        f"📊 ИТОГО:\n"
        f"Общая сумма: {total_sales:,.0f} сум\n"
        f"Безнал: {total_cashless:,.0f} сум\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 Наличных по отчёту: {cash_expected:,.0f} сум\n\n"
        f"Теперь введите фактическую сумму наличных в кассе:",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.reply_to_message.bot.get_current().state.set_state(DailyReport.counting_cash)

@dp.message(DailyReport.counting_cash)
async def count_cash(message: types.Message, state: FSMContext):
    """Подсчёт наличных"""
    try:
        cash_actual = float(message.text.replace(',', '').replace(' ', ''))
        user_id = message.from_user.id
        
        cash_expected = user_reports[user_id]['cash_expected']
        cash_difference = cash_actual - cash_expected
        
        user_reports[user_id]['cash_actual'] = cash_actual
        user_reports[user_id]['cash_difference'] = cash_difference
        
        # Сохраняем в БД
        db.update_report_cash(
            user_reports[user_id]['report_id'],
            cash_expected,
            cash_actual,
            {}  # breakdown пока пустой
        )
        
        if cash_difference > 0:
            diff_text = f"✅ ИЗЛИШЕК: +{cash_difference:,.0f} сум"
        elif cash_difference < 0:
            diff_text = f"⚠️ НЕДОСТАЧА: {cash_difference:,.0f} сум"
        else:
            diff_text = f"✅ БЕЗ РАСХОЖДЕНИЙ"
        
        await message.answer(
            f"💵 СВЕРКА:\n"
            f"По отчёту: {cash_expected:,.0f} сум\n"
            f"Фактически: {cash_actual:,.0f} сум\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{diff_text}\n\n"
            f"Добавить расходы за день?",
            reply_markup=get_yes_no_keyboard()
        )
        await state.set_state(DailyReport.entering_expenses)
    
    except ValueError:
        await message.answer("❌ Введите корректное число")

@dp.message(DailyReport.entering_expenses, F.text == "❌ Нет")
async def skip_expenses(message: types.Message, state: FSMContext):
    """Пропустить расходы"""
    await finalize_report(message, state)

@dp.message(DailyReport.entering_expenses, F.text == "✅ Да")
async def add_expenses_prompt(message: types.Message):
    """Начать добавление расходов"""
    await message.answer(
        "💸 Отправьте расход в формате:\n"
        "<b>Сумма | Описание</b>\n\n"
        "Например:\n"
        "150000 | Закупка овощей\n\n"
        "Или отправьте /done когда закончите",
        parse_mode="HTML"
    )

@dp.message(DailyReport.entering_expenses, Command("done"))
async def finalize_report(message: types.Message, state: FSMContext):
    """Завершить отчёт"""
    user_id = message.from_user.id
    
    # Закрываем отчёт
    db.close_report(user_reports[user_id]['report_id'])
    
    report = user_reports[user_id]
    
    await message.answer(
        f"✅ <b>ОТЧЁТ СОХРАНЁН!</b>\n\n"
        f"📅 Дата: {report['date'].strftime('%d.%m.%Y')}\n"
        f"📍 Точка: {report['location_name']}\n"
        f"💰 Продажи: {report['total_sales']:,.0f} сум\n"
        f"💵 Наличные: {report['cash_difference']:+,.0f} сум\n\n"
        f"ID отчёта: {report['report_id']}",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )
    
    await state.clear()
    del user_reports[user_id]

@dp.message(DailyReport.entering_expenses)
async def add_expense(message: types.Message):
    """Добавить расход"""
    user_id = message.from_user.id
    
    try:
        parts = message.text.split('|')
        if len(parts) != 2:
            await message.answer("❌ Формат: Сумма | Описание")
            return
        
        amount = float(parts[0].strip().replace(',', '').replace(' ', ''))
        description = parts[1].strip()
        
        # Добавляем в БД (в кассу)
        cash_accounts = db.get_accounts('cash')
        if cash_accounts:
            db.add_report_expense(
                user_reports[user_id]['report_id'],
                cash_accounts[0]['id'],
                amount,
                None,
                description
            )
            
            await message.answer(f"✅ Расход {amount:,.0f} сум добавлен")
    
    except ValueError:
        await message.answer("❌ Проверьте формат")

@dp.message(F.text == "💰 Балансы")
async def show_balances(message: types.Message):
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
    
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "ℹ️ Помощь")
async def show_help(message: types.Message):
    """Помощь"""
    await message.answer(
        "ℹ️ <b>ПОМОЩЬ</b>\n\n"
        "<b>Дневной отчёт:</b>\n"
        "1. Нажмите '📊 Новый отчёт'\n"
        "2. Выберите точку\n"
        "3. Введите общую сумму продаж\n"
        "4. Введите суммы по каждому методу оплаты\n"
        "5. Введите фактическую сумму наличных\n"
        "6. Добавьте расходы (опционально)\n"
        "7. Отчёт сохранён!\n\n"
        "<b>Балансы:</b>\n"
        "Нажмите '💰 Балансы' чтобы увидеть остатки на всех счетах",
        parse_mode="HTML"
    )

# ========== ЗАПУСК ==========

async def main():
    """Запуск бота"""
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
