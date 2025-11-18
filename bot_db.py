#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bot_db.py - Модуль работы с БД для Telegram бота
Версия 2.0 - Интеграция с системой прав (permissions)
"""

import sqlite3
from typing import Optional, Tuple, List, Dict
from datetime import datetime
import sys
import os

# Добавляем путь к permissions_manager
sys.path.append(os.path.dirname(__file__))
from permissions_manager import permissions

DB_PATH = 'finance_v5.db'

def get_db_connection():
    """Подключение к БД"""
    return sqlite3.connect(DB_PATH)

# ========================================
# РАБОТА С ПОЛЬЗОВАТЕЛЯМИ (НОВАЯ СИСТЕМА)
# ========================================

def get_user_id_by_telegram(telegram_id: int) -> Optional[int]:
    """
    Получить user_id из таблицы users по telegram_id
    
    Args:
        telegram_id: Telegram ID пользователя
    
    Returns:
        user_id если найден, None если нет
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM users 
            WHERE telegram_id = ? AND is_active = 1
        """, (str(telegram_id),))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
        
    except Exception as e:
        print(f"Ошибка get_user_id_by_telegram: {e}")
        return None

def get_or_create_user(telegram_id: int, username: str, full_name: str) -> Optional[int]:
    """
    Найти пользователя или создать нового (БЕЗ ПРАВ)
    
    Args:
        telegram_id: Telegram ID
        username: username из Telegram
        full_name: Полное имя из Telegram
    
    Returns:
        user_id если успешно, None если ошибка
    """
    try:
        # Проверяем существует ли
        user_id = get_user_id_by_telegram(telegram_id)
        
        if user_id:
            print(f"✅ Пользователь найден: {full_name} (ID: {user_id})")
            return user_id
        
        # Создаём нового без прав
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (telegram_id, username, is_active)
            VALUES (?, ?, 1)
        """, (str(telegram_id), username or full_name))
        
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        print(f"⚠️ НОВЫЙ пользователь БЕЗ ПРАВ: {full_name} (TG: {telegram_id}, DB_ID: {new_id})")
        print(f"   Админ должен дать права через Desktop приложение!")
        
        return new_id
        
    except Exception as e:
        print(f"Ошибка get_or_create_user: {e}")
        return None

def get_username_by_telegram(telegram_id: int) -> Optional[str]:
    """Получить username пользователя"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT username FROM users 
            WHERE telegram_id = ? AND is_active = 1
        """, (str(telegram_id),))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
        
    except Exception as e:
        print(f"Ошибка get_username_by_telegram: {e}")
        return None

# ========================================
# ПРОВЕРКА ПРАВ
# ========================================

def has_permission(telegram_id: int, permission_name: str) -> bool:
    """
    Проверить есть ли у пользователя право
    
    Args:
        telegram_id: Telegram ID пользователя
        permission_name: Системное имя права (например: 'quick_add_expense')
    
    Returns:
        True если право есть, False если нет
    
    Example:
        if has_permission(message.from_user.id, 'quick_add_expense'):
            # Разрешить действие
    """
    try:
        user_id = get_user_id_by_telegram(telegram_id)
        
        if not user_id:
            print(f"❌ Пользователь TG:{telegram_id} не найден")
            return False
        
        has_perm = permissions.has_permission(user_id, permission_name)
        
        if not has_perm:
            print(f"❌ TG:{telegram_id} (DB:{user_id}) НЕТ права '{permission_name}'")
        
        return has_perm
        
    except Exception as e:
        print(f"Ошибка has_permission: {e}")
        return False

def get_user_permissions(telegram_id: int) -> List[str]:
    """
    Получить список всех прав пользователя
    
    Returns:
        Список системных имён прав ['quick_add_expense', 'view_balances', ...]
    """
    try:
        user_id = get_user_id_by_telegram(telegram_id)
        
        if not user_id:
            return []
        
        user_perms = permissions.get_user_permissions(user_id)
        return [p['name'] for p in user_perms]
        
    except Exception as e:
        print(f"Ошибка get_user_permissions: {e}")
        return []

# ========================================
# ЗАПИСЬ В TIMELINE (с user_id)
# ========================================

def log_to_timeline(telegram_id: int, operation_type: str, amount: float,
                    category_id: Optional[int] = None,
                    account_id: Optional[int] = None,
                    description: str = "",
                    source: str = 'telegram') -> bool:
    """
    Записать операцию в timeline
    
    Args:
        telegram_id: Telegram ID пользователя (будет преобразован в user_id)
        operation_type: 'expense' или 'income'
        amount: Сумма
        category_id: ID категории
        account_id: ID счёта
        description: Описание
        source: Источник (по умолчанию 'telegram')
    
    Returns:
        True если успешно, False если ошибка
    """
    try:
        user_id = get_user_id_by_telegram(telegram_id)
        
        if not user_id:
            print(f"❌ Не могу записать в timeline: пользователь TG:{telegram_id} не найден")
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO timeline 
            (date, type, category_id, account_id, amount, description, source, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime('%Y-%m-%d'),
            operation_type,
            category_id,
            account_id,
            amount,
            description,
            source,
            user_id
        ))
        
        conn.commit()
        timeline_id = cursor.lastrowid
        conn.close()
        
        print(f"✅ Timeline #{timeline_id}: {operation_type} {amount} от user_id={user_id} (TG:{telegram_id})")
        return True
        
    except Exception as e:
        print(f"Ошибка log_to_timeline: {e}")
        return False

# ========================================
# КАТЕГОРИИ (без изменений)
# ========================================

def get_categories(parent_id: Optional[int] = None, category_type: str = 'expense') -> List[Dict]:
    """
    Получить список категорий
    
    Args:
        parent_id: ID родительской категории (None для корневых)
        category_type: 'expense' или 'income'
    
    Returns:
        [{'id': 1, 'name': 'Название'}, ...]
    """
    table = 'expense_categories' if category_type == 'expense' else 'income_categories'
    
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if parent_id is None:
            query = f"SELECT id, name FROM {table} WHERE parent_id IS NULL AND is_active = 1 ORDER BY name"
            cursor.execute(query)
        else:
            query = f"SELECT id, name FROM {table} WHERE parent_id = ? AND is_active = 1 ORDER BY name"
            cursor.execute(query, (parent_id,))
        
        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return categories
        
    except Exception as e:
        print(f"Ошибка get_categories: {e}")
        return []

def get_category_details(category_id: int, category_type: str = 'expense') -> Optional[Dict]:
    """
    Получить детали категории
    
    Returns:
        {'id': 1, 'name': 'Название', 'parent_id': None, 'has_children': False}
    """
    table = 'expense_categories' if category_type == 'expense' else 'income_categories'
    
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT name, parent_id FROM {table} WHERE id = ?", (category_id,))
        cat = cursor.fetchone()
        
        if not cat:
            conn.close()
            return None
        
        cursor.execute(f"SELECT 1 FROM {table} WHERE parent_id = ? AND is_active = 1 LIMIT 1", 
                      (category_id,))
        has_children = cursor.fetchone() is not None
        
        conn.close()
        
        return {
            'id': category_id,
            'name': cat['name'],
            'parent_id': cat['parent_id'],
            'has_children': has_children
        }
        
    except Exception as e:
        print(f"Ошибка get_category_details: {e}")
        return None

# ========================================
# СЧЕТА (без изменений)
# ========================================

def get_accounts(account_type: Optional[str] = None) -> List[Dict]:
    """
    Получить список счетов
    
    Returns:
        [{'id': 1, 'name': 'Касса', 'account_type': 'cash'}, ...]
    """
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT id, name, account_type 
            FROM accounts 
            WHERE account_type IN ('cash', 'bank') AND is_active = 1
            ORDER BY name
        """
        
        cursor.execute(query)
        accounts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return accounts
        
    except Exception as e:
        print(f"Ошибка get_accounts: {e}")
        return []

# ========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ========================================

def get_permissions_summary(telegram_id: int) -> str:
    """
    Получить текстовое описание прав пользователя
    
    Returns:
        Строка с правами для отправки в Telegram
    """
    try:
        user_id = get_user_id_by_telegram(telegram_id)
        
        if not user_id:
            return "❌ Пользователь не найден"
        
        user_perms = permissions.get_user_permissions(user_id)
        
        if not user_perms:
            return "❌ У вас нет прав. Обратитесь к администратору."
        
        # Группируем по категориям
        by_category = {}
        for perm in user_perms:
            cat = perm['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(perm['display_name'])
        
        # Формируем текст
        text = "🔐 <b>ВАШИ ПРАВА:</b>\n\n"
        
        cat_emoji = {
            'finance': '💰',
            'view': '👁️',
            'settings': '⚙️',
            'admin': '🔐'
        }
        
        for cat, perms in by_category.items():
            emoji = cat_emoji.get(cat, '📋')
            text += f"{emoji} <b>{cat.upper()}:</b>\n"
            for p in perms:
                text += f"  ✓ {p}\n"
            text += "\n"
        
        return text
        
    except Exception as e:
        print(f"Ошибка get_permissions_summary: {e}")
        return "❌ Ошибка получения прав"

# ========================================
# ТЕСТИРОВАНИЕ
# ========================================

if __name__ == "__main__":
    print("=== ТЕСТ bot_db.py v2.0 ===\n")
    
    # Тест 1: Получить пользователя
    test_tg_id = 123456789
    print(f"1. Поиск TG:{test_tg_id}")
    user_id = get_user_id_by_telegram(test_tg_id)
    print(f"   Результат: {user_id}\n")
    
    # Тест 2: Проверка права
    print(f"2. Проверка права 'quick_add_expense'")
    has_perm = has_permission(test_tg_id, 'quick_add_expense')
    print(f"   Результат: {has_perm}\n")
    
    # Тест 3: Список прав
    print(f"3. Все права пользователя")
    perms = get_user_permissions(test_tg_id)
    print(f"   Права: {perms}\n")
    
    # Тест 4: Резюме прав
    print(f"4. Резюме прав")
    summary = get_permissions_summary(test_tg_id)
    print(summary)
