#!/usr/bin/env python3
"""
Telegram бот для системы учёта Air Waffle
(Версия v4.0: Система прав, Быстрое добавление)
"""

import asyncio
import logging
from datetime import date, datetime
from typing import Optional # <-- Добавлен импорт
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import re

from database_v5 import FinanceSystemV5
import bot_db # <-- НАШ НОВЫЙ "МОЗГ"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# ВАШ ТОКЕН ВСТАВЛЕН
BOT_TOKEN = "8188072633:AAE6TavFNHlbyAcfR8Z5Tnsp4jpQsXj1jHw"

# Инициализация
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db = FinanceSystemV5()

# Состояния для заполнения отчёта
class DailyReport(StatesGroup):
    waiting_for_date = State() # <-- Добавлено
    selecting_location = State()
    entering_total_sales = State()
    entering_payments = State()
    counting_cash = State()
    entering_non_sales = State()
    entering_expenses = State()
    confirming = State()

# Новый FSM для пошагового ввода расхода
class ExpenseInput(StatesGroup):
    waiting_for_amount = State()
    waiting_for_description = State()
    waiting_for_category = State()
    waiting_for_account = State() # <-- Добавлено

class IncomeInput(StatesGroup):
    waiting_for_amount = State()
    waiting_for_description = State()
    waiting_for_category = State()
    waiting_for_account = State()

# Временное хранилище данных отчёта
user_reports = {}

# ========== КЛАВИАТУРЫ ПО ПРАВАМ ==========

def get_main_keyboard_by_permissions(user_id_db: int):
    """Главное меню по правам пользователя"""
    from permissions_manager import permissions

    buttons = []

    if permissions.has_permission(user_id_db, 'create_cashier_report'):
        buttons.append([KeyboardButton(text="📊 Новый отчёт")])

    row = []
    if permissions.has_permission(user_id_db, 'view_balances'):
        row.append(KeyboardButton(text="💰 Балансы"))
    if permissions.has_permission(user_id_db, 'view_own_reports'):
        row.append(KeyboardButton(text="📋 Мои отчёты"))
    if row:
        buttons.append(row)

    row = []
    if permissions.has_permission(user_id_db, 'quick_add_expense'):
        row.append(KeyboardButton(text="📉 Расход"))
    if permissions.has_permission(user_id_db, 'quick_add_income'):
        row.append(KeyboardButton(text="📈 Приход"))
    if row:
        buttons.append(row)

    buttons.append([KeyboardButton(text="ℹ️ Помощь")])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

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
async def cmd_start(message: types.Message, state: FSMContext):
    """Команда /start: авторизация пользователя и главное меню"""
    await state.clear()

    tg_user = message.from_user
    telegram_id = tg_user.id
    username = tg_user.username or ''
    full_name = tg_user.full_name
    
    print(f"Попытка входа: {full_name} (ID: {telegram_id})")
    
    user_id_db = bot_db.get_or_create_user(telegram_id, username, full_name)

    if not user_id_db:
        await message.answer(
            f"❌ Ошибка регистрации. Попробуйте позже.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    user_perms = bot_db.get_user_permissions(telegram_id)

    if not user_perms:
        await message.answer(
            f"👋 Привет, {full_name}!\n\n"
            f"❌ У вас пока нет прав доступа.\n"
            f"Обратитесь к администратору для получения прав.\n\n"
            f"Ваш Telegram ID: `{telegram_id}`",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    print(f"✅ Вход: {full_name}, Прав: {len(user_perms)}")

    await state.update_data(user_id_db=user_id_db)

    keyboard = get_main_keyboard_by_permissions(user_id_db)
    perms_summary = bot_db.get_permissions_summary(telegram_id)

    await message.answer(
        f"👋 Привет, {full_name}!\n\n{perms_summary}\n"
        f"Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.message(F.text == "📊 Новый отчёт")
async def start_new_report(message: types.Message, state: FSMContext):
    """Начать новый отчёт (Система прав)"""
    telegram_id = message.from_user.id

    if not bot_db.has_permission(telegram_id, 'create_cashier_report'):
        await message.answer("❌ У вас нет права создавать отчёты кассира!")
        return

    data = await state.get_data()
    user_id_db = data.get('user_id_db')
    if not user_id_db:
        await cmd_start(message, state)
        return

    user_reports[telegram_id] = {
        'payments': {},
        'cash_breakdown': {},
        'non_sales_income': [],
        'expenses': []
    }

    await message.answer(
        "📅 Введите дату отчёта (ДД.ММ):\n\n"
        "Например: `05.11`\n"
        "Или просто напишите `Сегодня`",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Сегодня"), KeyboardButton(text="❌ Отмена")]],
            resize_keyboard=True
        ),
        parse_mode="Markdown"
    )
    await state.set_state(DailyReport.waiting_for_date)

@dp.message(DailyReport.waiting_for_date)
async def enter_date(message: types.Message, state: FSMContext):
    """Шаг 1: Получаем дату отчёта"""
    telegram_id = message.from_user.id
    text = message.text.strip()
    
    if text == "❌ Отмена":
        data = await state.get_data()
        user_id_db = data.get('user_id_db')
        await state.clear()
        if user_id_db:
            await state.update_data(user_id_db=user_id_db)
        keyboard = get_main_keyboard_by_permissions(user_id_db) if user_id_db else ReplyKeyboardRemove()
        await message.answer("Отменено", reply_markup=keyboard)
        return
    
    report_date = None
    if text.lower() == 'сегодня':
        report_date = date.today()
    else:
        match = re.match(r"(\d{1,2})[.,/](\d{1,2})", text)
        if match:
            day, month = int(match.group(1)), int(match.group(2))
            try:
                report_date = date(datetime.now().year, month, day)
            except ValueError:
                await message.answer("❌ Некорректная дата. Попробуйте ДД.ММ (например, `05.11`)")
                return
    
    if not report_date:
        await message.answer("❌ Непонятный формат. Введите `ДД.ММ` или `Сегодня`")
        return

    if telegram_id not in user_reports:
        await message.answer("❌ Ошибка: данные отчёта не найдены. Нажмите /start.")
        await state.clear()
        return

    user_reports[telegram_id]['date'] = report_date
    
    await message.answer(
        f"📍 Выберите точку продаж (для даты: {report_date.strftime('%d.%m.%Y')})",
        reply_markup=get_locations_keyboard()
    )
    await state.set_state(DailyReport.selecting_location)

@dp.message(DailyReport.selecting_location)
async def select_location(message: types.Message, state: FSMContext):
    """Шаг 2: Выбор точки"""
    if message.text == "❌ Отмена":
        data = await state.get_data()
        user_id_db = data.get('user_id_db')
        await state.clear()
        if user_id_db:
            await state.update_data(user_id_db=user_id_db)
        keyboard = get_main_keyboard_by_permissions(user_id_db) if user_id_db else ReplyKeyboardRemove()
        await message.answer("Отменено", reply_markup=keyboard)
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
        f"📅 Дата: {user_reports[user_id]['date'].strftime('%d.%m.%Y')}\n"
        f"📍 Точка: {location['name']}\n\n"
        "💰 Введите общую сумму продаж с учётом скидок:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(DailyReport.entering_total_sales)

@dp.message(DailyReport.entering_total_sales)
async def enter_total_sales(message: types.Message, state: FSMContext):
    """Шаг 3: Ввод общей суммы"""
    try:
        total_sales = float(message.text.replace(',', '').replace(' ', ''))
        if total_sales <= 0:
            await message.answer("❌ Сумма должна быть больше 0")
            return
        
        user_id = message.from_user.id
        user_reports[user_id]['total_sales'] = total_sales
        
        report_id = db.create_daily_report(
            user_reports[user_id]['date'], # <-- Исправлено
            user_reports[user_id]['location_id'],
            total_sales,
            message.from_user.username
        )
        user_reports[user_id]['report_id'] = report_id
        
        user_reports[user_id]['current_payment_index'] = 0
        payment_methods = db.get_payment_methods()
        user_reports[user_id]['payment_methods'] = [m for m in payment_methods if m.get('is_visible', True)]
        
        await ask_next_payment(message, user_id, state) # <-- ИСПРАВЛЕНО
        await state.set_state(DailyReport.entering_payments)
    
    except ValueError:
        await message.answer("❌ Введите корректное число")
    except Exception as e:
        print(f"!!! КРИТИЧЕСКАЯ ОШИБКА в enter_total_sales: {e}")
        await message.answer(f"⛔️ Произошла ошибка. Бот не смог обработать сумму.\n\n"
                           f"Тех. инфо: `{e}`\n\n"
                           f"Попробуйте нажать /start и начать заново.")
        await state.clear()

async def ask_next_payment(message: types.Message, user_id: int, state: FSMContext): # <-- ИСПРАВЛЕНО
    """Запросить следующий метод оплаты"""
    idx = user_reports[user_id]['current_payment_index']
    methods = user_reports[user_id]['payment_methods']
    
    if idx >= len(methods):
        await finalize_payments(message, user_id, state) # <-- ИСПРАВЛЕНО
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
        await ask_next_payment(message, user_id, state) # <-- ИСПРАВЛЕНО
        return
    
    if message.text == "❌ Отмена":
        data = await state.get_data()
        user_id_db = data.get('user_id_db')
        await state.clear()
        if user_id_db:
            await state.update_data(user_id_db=user_id_db)
        keyboard = get_main_keyboard_by_permissions(user_id_db) if user_id_db else ReplyKeyboardRemove()
        await message.answer("Отменено", reply_markup=keyboard)
        return
    
    try:
        amount = float(message.text.replace(',', '').replace(' ', ''))
        
        if amount > 0:
            idx = user_reports[user_id]['current_payment_index']
            method = user_reports[user_id]['payment_methods'][idx]
            
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
        await ask_next_payment(message, user_id, state) # <-- ИСПРАВЛЕНО
    
    except ValueError:
        await message.answer("❌ Введите корректное число")

async def finalize_payments(message: types.Message, user_id: int, state: FSMContext): # <-- ИСПРАВЛЕНО
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
    await state.set_state(DailyReport.counting_cash) # <-- ИСПРАВЛЕНО

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
        
        db.update_report_cash(
            user_reports[user_id]['report_id'],
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

# --- Обработчики для "Да" / "Нет" / "/done" ---

@dp.message(DailyReport.entering_expenses, F.text == "❌ Нет")
async def skip_expenses(message: types.Message, state: FSMContext):
    """Пропустить расходы"""
    await finalize_report(message, state) 

@dp.message(DailyReport.entering_expenses, Command("done"))
async def finalize_report_from_done(message: types.Message, state: FSMContext):
    """Завершить отчёт по /done"""
    await finalize_report(message, state)

@dp.message(DailyReport.entering_expenses, F.text == "✅ Да")
async def start_expense_input(message: types.Message, state: FSMContext):
    """Начать новый пошаговый ввод расхода"""
    report_data = await state.get_data()
    await state.set_state(ExpenseInput.waiting_for_amount)
    await state.update_data(report_id=user_reports[message.from_user.id]['report_id'],
                             user_id_db=report_data.get('user_id_db'),
                             quick_mode=None)
    
    await message.answer("💸 Введите сумму расхода:", reply_markup=ReplyKeyboardRemove())

@dp.message(F.text == "📉 Расход", StateFilter(None))
async def quick_expense_button(message: types.Message, state: FSMContext):
    """Быстрое добавление расхода"""
    telegram_id = message.from_user.id

    if not bot_db.has_permission(telegram_id, 'quick_add_expense'):
        await message.answer("❌ У вас нет права добавлять расходы.")
        return

    user_id_db = bot_db.get_user_id_by_telegram(telegram_id)
    if not user_id_db:
        await message.answer("❌ Пользователь не найден. Нажмите /start.")
        return

    await state.set_state(ExpenseInput.waiting_for_amount)
    await state.update_data(quick_mode='expense', user_id_db=user_id_db)

    await message.answer(
        "💸 Введите сумму расхода:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отмена")]],
            resize_keyboard=True
        )
    )

@dp.message(F.text == "📈 Приход", StateFilter(None))
async def quick_income_button(message: types.Message, state: FSMContext):
    """Быстрое добавление прихода"""
    telegram_id = message.from_user.id

    if not bot_db.has_permission(telegram_id, 'quick_add_income'):
        await message.answer("❌ У вас нет права добавлять приходы.")
        return

    user_id_db = bot_db.get_user_id_by_telegram(telegram_id)
    if not user_id_db:
        await message.answer("❌ Пользователь не найден. Нажмите /start.")
        return

    await state.set_state(IncomeInput.waiting_for_amount)
    await state.update_data(quick_mode='income', user_id_db=user_id_db)

    await message.answer(
        "💰 Введите сумму прихода:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отмена")]],
            resize_keyboard=True
        )
    )

# --- Новая цепочка FSM для ExpenseInput ---

@dp.message(ExpenseInput.waiting_for_amount)
async def expense_enter_amount(message: types.Message, state: FSMContext):
    """Шаг 1: Получаем Сумму"""
    if message.text == "❌ Отмена":
        data = await state.get_data()
        user_id_db = data.get('user_id_db')
        quick_mode = data.get('quick_mode')
        await state.clear()
        if user_id_db:
            await state.update_data(user_id_db=user_id_db)
        keyboard = get_main_keyboard_by_permissions(user_id_db) if user_id_db else ReplyKeyboardRemove()
        if quick_mode == 'expense':
            await message.answer("Отменено.", reply_markup=keyboard)
        else:
            await message.answer("Расход отменён. Добавить еще расход?", reply_markup=get_yes_no_keyboard())
        return

    try:
        amount = float(message.text.replace(',', '').replace(' ', ''))
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0")
            return
        
        await state.update_data(amount=amount)
        await state.set_state(ExpenseInput.waiting_for_description)
        await message.answer("📝 Введите описание расхода:")
        
    except ValueError:
        await message.answer("❌ Введите корректное число")

@dp.message(ExpenseInput.waiting_for_description)
async def expense_enter_description(message: types.Message, state: FSMContext):
    """Шаг 2: Получаем Описание"""
    if message.text == "❌ Отмена":
        data = await state.get_data()
        user_id_db = data.get('user_id_db')
        quick_mode = data.get('quick_mode')
        await state.clear()
        if user_id_db:
            await state.update_data(user_id_db=user_id_db)
        keyboard = get_main_keyboard_by_permissions(user_id_db) if user_id_db else ReplyKeyboardRemove()
        if quick_mode == 'expense':
            await message.answer("Отменено.", reply_markup=keyboard)
        else:
            await message.answer("Расход отменён. Добавить еще расход?", reply_markup=get_yes_no_keyboard())
        return

    description = message.text.strip()
    if not description:
        await message.answer("❌ Описание не может быть пустым")
        return
    
    await state.update_data(description=description, category_type='expense')
    await state.set_state(ExpenseInput.waiting_for_category)
    
    keyboard = await build_category_keyboard(parent_id=None, category_type='expense')
    await message.answer("🌳 Выберите категорию:", reply_markup=keyboard)

async def build_category_keyboard(parent_id: Optional[int] = None, current_path: str = "Root", category_type: str = 'expense'):
    """Рекурсивно строит Inline-клавиатуру для категорий"""
    categories = bot_db.get_categories(parent_id, category_type=category_type)
    
    buttons = []
    row = []
    for cat in categories:
        row.append(types.InlineKeyboardButton(text=cat['name'], callback_data=f"cat_{cat['id']}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    if parent_id is not None:
        back_id = f"cat_back_{current_path}"
        buttons.append([types.InlineKeyboardButton(text="⬅️ Назад", callback_data=back_id)])
    
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

def build_account_keyboard() -> ReplyKeyboardMarkup:
    """Строит Reply-клавиатуру для выбора счета"""
    accounts = bot_db.get_accounts()
    buttons = []
    row = []
    for acc in accounts:
        emoji = "💵" if acc['account_type'] == 'cash' else "🏦"
        row.append(KeyboardButton(text=f"{emoji} {acc['name']}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([KeyboardButton(text="❌ Отмена")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.callback_query(StateFilter(ExpenseInput.waiting_for_category), F.data.startswith("cat_"))
async def process_expense_category(callback: types.CallbackQuery, state: FSMContext):
    """Обработка нажатий на Inline-кнопки категорий"""
    
    query = callback.data
    data = await state.get_data()
    category_type = data.get('category_type', 'expense')
    
    if query.startswith("cat_back_"):
        path_parts = query.split('_')
        if len(path_parts) > 2 and path_parts[2] != 'root':
            parent_id = int(path_parts[2])
            details = bot_db.get_category_details(parent_id, category_type=category_type)
            grandparent_id = details.get('parent_id')
            
            keyboard = await build_category_keyboard(grandparent_id, category_type=category_type)
            await callback.message.edit_text(f"🌳 Выберите категорию:", reply_markup=keyboard)
        else:
            keyboard = await build_category_keyboard(parent_id=None, category_type=category_type)
            await callback.message.edit_text("🌳 Выберите категорию (Корень):", reply_markup=keyboard)
        await callback.answer()
        return

    category_id = int(query.split('_')[1])
    details = bot_db.get_category_details(category_id, category_type=category_type)
    
    if not details:
        await callback.answer("❌ Ошибка: Категория не найдена", show_alert=True)
        return

    if details['has_children']:
        await callback.answer(f"Загрузка {details['name']}...")
        parent_id_for_back_button = details.get('parent_id') or 'root'
        keyboard = await build_category_keyboard(
            parent_id=category_id,
            current_path=str(parent_id_for_back_button),
            category_type=category_type
        )
        await callback.message.edit_text(f"🌳 {details['name']} / Выберите подкатегорию:", reply_markup=keyboard)
    else:
        await state.update_data(category_id=category_id, category_name=details['name'])
        
        await state.set_state(ExpenseInput.waiting_for_account)
        
        keyboard = build_account_keyboard()
        await callback.message.delete() 
        await callback.message.answer(f"✅ Категория: {details['name']}\n\n"
                                     f"💳 Теперь выберите счет списания:",
                                     reply_markup=keyboard)
        await callback.answer()

@dp.message(ExpenseInput.waiting_for_account)
async def expense_enter_account(message: types.Message, state: FSMContext):
    """Шаг 4: Получаем Счет, Сохраняем и Завершаем"""
    
    if message.text == "❌ Отмена":
        data = await state.get_data()
        quick_mode = data.get('quick_mode')
        user_id_db = data.get('user_id_db')
        if quick_mode == 'expense':
            await state.clear()
            if user_id_db:
                await state.update_data(user_id_db=user_id_db)
            keyboard = get_main_keyboard_by_permissions(user_id_db) if user_id_db else ReplyKeyboardRemove()
            await message.answer("Отменено.", reply_markup=keyboard)
        else:
            await state.set_state(DailyReport.entering_expenses)
            await message.answer("Отменено. Добавить еще расход?", reply_markup=get_yes_no_keyboard())
        return

    account_name = message.text.split(' ', 1)[-1]
    accounts = bot_db.get_accounts()
    account = next((acc for acc in accounts if acc['name'] == account_name), None)
    
    if not account:
        await message.answer("❌ Пожалуйста, выберите счет с помощью кнопок.")
        return

    data = await state.get_data()
    amount = data['amount']
    description = data['description']
    category_id = data['category_id']
    category_name = data['category_name']
    account_id = account['id']
    quick_mode = data.get('quick_mode') == 'expense'
    user_id_db = data.get('user_id_db')

    if quick_mode:
        success = bot_db.log_to_timeline(
            telegram_id=message.from_user.id,
            operation_type='expense',
            amount=-abs(amount),
            category_id=category_id,
            account_id=account_id,
            description=description,
            source='telegram'
        )
        keyboard = get_main_keyboard_by_permissions(user_id_db) if user_id_db else ReplyKeyboardRemove()
        if success:
            await message.answer(
                f"✅ Расход добавлен!\n"
                f"Сумма: {amount:,.0f} сум\n"
                f"Категория: {category_name}\n"
                f"Счёт: {account_name}",
                reply_markup=keyboard
            )
        else:
            await message.answer("❌ Ошибка сохранения расхода.", reply_markup=keyboard)
        await state.clear()
        if user_id_db:
            await state.update_data(user_id_db=user_id_db)
        return

    db.add_report_expense(
        data['report_id'],
        account_id,
        amount,
        category_id,
        description
    )
    
    bot_db.log_to_timeline(
        telegram_id=message.from_user.id,
        operation_type='expense',
        amount=-abs(amount),
        category_id=category_id,
        account_id=account_id,
        description=description,
        source='telegram_report'
    )
    
    await state.set_state(DailyReport.entering_expenses)
    await message.answer(
        f"✅ Расход добавлен:\n"
        f"Сумма: {amount:,.0f} сум\n"
        f"Категория: {category_name}\n"
        f"Счёт: {account_name}\n\n"
        "Добавить еще один расход?",
        reply_markup=get_yes_no_keyboard()
    )

@dp.message(IncomeInput.waiting_for_amount)
async def income_enter_amount(message: types.Message, state: FSMContext):
    """Шаг 1: Получаем сумму прихода"""
    if message.text == "❌ Отмена":
        data = await state.get_data()
        user_id_db = data.get('user_id_db')
        await state.clear()
        if user_id_db:
            await state.update_data(user_id_db=user_id_db)
        keyboard = get_main_keyboard_by_permissions(user_id_db) if user_id_db else ReplyKeyboardRemove()
        await message.answer("Отменено.", reply_markup=keyboard)
        return

    try:
        amount = float(message.text.replace(',', '').replace(' ', ''))
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0")
            return

        await state.update_data(amount=amount)
        await state.set_state(IncomeInput.waiting_for_description)
        await message.answer("📝 Введите описание прихода:")

    except ValueError:
        await message.answer("❌ Введите корректное число")

@dp.message(IncomeInput.waiting_for_description)
async def income_enter_description(message: types.Message, state: FSMContext):
    """Шаг 2: Получаем описание прихода"""
    if message.text == "❌ Отмена":
        data = await state.get_data()
        user_id_db = data.get('user_id_db')
        await state.clear()
        if user_id_db:
            await state.update_data(user_id_db=user_id_db)
        keyboard = get_main_keyboard_by_permissions(user_id_db) if user_id_db else ReplyKeyboardRemove()
        await message.answer("Отменено.", reply_markup=keyboard)
        return

    description = message.text.strip()
    if not description:
        await message.answer("❌ Описание не может быть пустым")
        return

    await state.update_data(description=description, category_type='income')
    await state.set_state(IncomeInput.waiting_for_category)

    keyboard = await build_category_keyboard(parent_id=None, category_type='income')
    await message.answer("🌳 Выберите категорию прихода:", reply_markup=keyboard)

@dp.callback_query(StateFilter(IncomeInput.waiting_for_category), F.data.startswith("cat_"))
async def process_income_category(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора категории прихода"""
    query = callback.data
    data = await state.get_data()
    category_type = data.get('category_type', 'income')

    if query.startswith("cat_back_"):
        path_parts = query.split('_')
        if len(path_parts) > 2 and path_parts[2] != 'root':
            parent_id = int(path_parts[2])
            details = bot_db.get_category_details(parent_id, category_type=category_type)
            grandparent_id = details.get('parent_id')
            keyboard = await build_category_keyboard(grandparent_id, category_type=category_type)
            await callback.message.edit_text("🌳 Выберите категорию:", reply_markup=keyboard)
        else:
            keyboard = await build_category_keyboard(parent_id=None, category_type=category_type)
            await callback.message.edit_text("🌳 Выберите категорию (Корень):", reply_markup=keyboard)
        await callback.answer()
        return

    category_id = int(query.split('_')[1])
    details = bot_db.get_category_details(category_id, category_type=category_type)

    if not details:
        await callback.answer("❌ Ошибка: Категория не найдена", show_alert=True)
        return

    if details['has_children']:
        await callback.answer(f"Загрузка {details['name']}...")
        parent_id_for_back_button = details.get('parent_id') or 'root'
        keyboard = await build_category_keyboard(
            parent_id=category_id,
            current_path=str(parent_id_for_back_button),
            category_type=category_type
        )
        await callback.message.edit_text(f"🌳 {details['name']} / Выберите подкатегорию:", reply_markup=keyboard)
    else:
        await state.update_data(category_id=category_id, category_name=details['name'])
        await state.set_state(IncomeInput.waiting_for_account)
        keyboard = build_account_keyboard()
        await callback.message.delete()
        await callback.message.answer(
            f"✅ Категория: {details['name']}\n\n"
            f"💳 Теперь выберите счёт зачисления:",
            reply_markup=keyboard
        )
        await callback.answer()

@dp.message(IncomeInput.waiting_for_account)
async def income_enter_account(message: types.Message, state: FSMContext):
    """Шаг 4: Выбор счёта для прихода"""
    if message.text == "❌ Отмена":
        data = await state.get_data()
        user_id_db = data.get('user_id_db')
        await state.clear()
        if user_id_db:
            await state.update_data(user_id_db=user_id_db)
        keyboard = get_main_keyboard_by_permissions(user_id_db) if user_id_db else ReplyKeyboardRemove()
        await message.answer("Отменено.", reply_markup=keyboard)
        return

    account_name = message.text.split(' ', 1)[-1]
    accounts = bot_db.get_accounts()
    account = next((acc for acc in accounts if acc['name'] == account_name), None)

    if not account:
        await message.answer("❌ Пожалуйста, выберите счет с помощью кнопок.")
        return

    data = await state.get_data()
    amount = data['amount']
    description = data['description']
    category_id = data['category_id']
    category_name = data['category_name']
    account_id = account['id']
    user_id_db = data.get('user_id_db')

    success = bot_db.log_to_timeline(
        telegram_id=message.from_user.id,
        operation_type='income',
        amount=abs(amount),
        category_id=category_id,
        account_id=account_id,
        description=description,
        source='telegram'
    )

    keyboard = get_main_keyboard_by_permissions(user_id_db) if user_id_db else ReplyKeyboardRemove()
    if success:
        await message.answer(
            f"✅ Приход добавлен!\n"
            f"Сумма: {amount:,.0f} сум\n"
            f"Категория: {category_name}\n"
            f"Счёт: {account_name}",
            reply_markup=keyboard
        )
    else:
        await message.answer("❌ Ошибка сохранения прихода.", reply_markup=keyboard)

    await state.clear()
    if user_id_db:
        await state.update_data(user_id_db=user_id_db)

@dp.message(DailyReport.entering_expenses, Command("done"))
async def finalize_report_from_done_dummy(message: types.Message, state: FSMContext):
    await finalize_report(message, state)

async def finalize_report(message: types.Message, state: FSMContext):
    """Завершить отчёт"""
    user_id_tg = message.from_user.id
    data = await state.get_data()
    user_id_db = data.get('user_id_db')
    
    if user_id_tg not in user_reports:
        keyboard = get_main_keyboard_by_permissions(user_id_db) if user_id_db else ReplyKeyboardRemove()
        await message.answer("Ошибка: не найдены данные отчета. Начните с /start", reply_markup=keyboard)
        await state.clear()
        return

    report_id = user_reports[user_id_tg]['report_id']
    db.close_report(report_id)
    
    report = user_reports[user_id_tg]
    
    if user_id_db:
        bot_db.log_to_timeline(
            telegram_id=user_id_tg,
            operation_type='income',
            amount=report['total_sales'],
            description=f"Продажи, отчёт #{report_id}",
            source='telegram_report'
        )
        if report['cash_difference'] != 0:
            op_type = 'expense' if report['cash_difference'] < 0 else 'income'
            bot_db.log_to_timeline(
                telegram_id=user_id_tg,
                operation_type=op_type,
                amount=report['cash_difference'],
                description=f"Разница в кассе, отчёт #{report_id}",
                source='telegram_report'
            )
    
    keyboard = get_main_keyboard_by_permissions(user_id_db) if user_id_db else ReplyKeyboardRemove()
    await message.answer(
        f"✅ <b>ОТЧЁТ СОХРАНЁН!</b>\n\n"
        f"📅 Дата: {report['date'].strftime('%d.%m.%Y')}\n"
        f"📍 Точка: {report['location_name']}\n"
        f"💰 Продажи: {report['total_sales']:,.0f} сум\n"
        f"💵 Наличные: {report['cash_difference']:+,.0f} сум\n\n"
        f"ID отчёта: {report['report_id']}",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
    await state.clear()
    if user_id_db:
        await state.update_data(user_id_db=user_id_db)
    del user_reports[user_id_tg]

# ========== ДРУГИЕ ОБРАБОТЧИКИ ==========

@dp.message(F.text == "💰 Балансы", StateFilter(None))
async def show_balances(message: types.Message, state: FSMContext):
    """Показать балансы"""
    telegram_id = message.from_user.id
    if not bot_db.has_permission(telegram_id, 'view_balances'):
        await message.answer("❌ У вас нет права просматривать балансы.")
        return

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

@dp.message(F.text == "📋 Мои отчёты", StateFilter(None))
async def show_my_reports(message: types.Message, state: FSMContext):
    """Показать 'Мои отчёты' (Таймлайн)"""
    telegram_id = message.from_user.id
    if not bot_db.has_permission(telegram_id, 'view_own_reports'):
        await message.answer("❌ У вас нет права просматривать отчёты.")
        return

    await message.answer("Заглушка: Здесь будет 'Таймлайн' (Шаг 5)")


@dp.message(F.text == "ℹ️ Помощь", StateFilter(None))
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
        "7. Отчёт сохранён!",
        parse_mode="HTML"
    )

# ========== ЗАПУСК ==========

async def main():
    """Запуск бота"""
    print("🤖 Бот запущен! (v4.0 - Система прав, Быстрое добавление)")
    # Убедимся, что FSM сбрасывается при перезапуске
    try:
        await dp.storage.close() 
    except Exception as e:
        print(f"Ошибка при закрытии storage (это нормально): {e}")
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
EOF
