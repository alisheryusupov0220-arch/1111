#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание и проверка таблиц категорий
Исправляет ошибку: no such table: income_categories
"""

import sqlite3
import sys

def create_categories_tables(db_path="finance_v5.db"):
    """Создание таблиц категорий"""
    
    print("🔧 Создание таблиц категорий...")
    print("="*50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # ========================================
        # 1. EXPENSE_CATEGORIES
        # ========================================
        print("\n📉 Создание expense_categories...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expense_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER,
                level INTEGER DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (parent_id) REFERENCES expense_categories(id)
            )
        """)
        
        # Проверка: есть ли данные?
        cursor.execute("SELECT COUNT(*) FROM expense_categories")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("   ➕ Таблица пустая, добавляем базовые категории...")
            
            base_categories = [
                (1, "Food Cost", None, 1),
                (2, "Продукты", 1, 2),
                (3, "Овощи", 2, 3),
                (4, "Мясо", 2, 3),
                (5, "Молочные", 2, 3),
                (6, "Напитки", 1, 2),
                (7, "Хозяйственные", None, 1),
                (8, "Зарплаты", None, 1),
                (9, "Аренда", None, 1),
                (10, "Коммунальные", None, 1)
            ]
            
            cursor.executemany("""
                INSERT OR IGNORE INTO expense_categories (id, name, parent_id, level)
                VALUES (?, ?, ?, ?)
            """, base_categories)
            
            print(f"   ✅ Добавлено {len(base_categories)} категорий расходов")
        else:
            print(f"   ✅ Таблица уже содержит {count} категорий")
        
        # ========================================
        # 2. INCOME_CATEGORIES
        # ========================================
        print("\n📈 Создание income_categories...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS income_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER,
                level INTEGER DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (parent_id) REFERENCES income_categories(id)
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM income_categories")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("   ➕ Таблица пустая, добавляем базовые категории...")
            
            income_cats = [
                (1, "Выручка", None, 1),
                (2, "Инвестиции", None, 1),
                (3, "Займы", None, 1),
                (4, "Прочие доходы", None, 1)
            ]
            
            cursor.executemany("""
                INSERT OR IGNORE INTO income_categories (id, name, parent_id, level)
                VALUES (?, ?, ?, ?)
            """, income_cats)
            
            print(f"   ✅ Добавлено {len(income_cats)} категорий приходов")
        else:
            print(f"   ✅ Таблица уже содержит {count} категорий")
        
        # ========================================
        # СОХРАНЕНИЕ
        # ========================================
        conn.commit()
        
        print("\n" + "="*50)
        print("✅ УСПЕХ! Таблицы категорий созданы")
        print("="*50)
        
        # ========================================
        # ПРОВЕРКА
        # ========================================
        print("\n🔍 Проверка...")
        
        cursor.execute("SELECT COUNT(*) FROM expense_categories WHERE is_active = 1")
        exp_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM income_categories WHERE is_active = 1")
        inc_count = cursor.fetchone()[0]
        
        print(f"   📉 Категорий расходов: {exp_count}")
        print(f"   📈 Категорий приходов: {inc_count}")
        
        # Примеры
        print("\n📝 Примеры категорий расходов:")
        cursor.execute("SELECT name FROM expense_categories WHERE is_active = 1 LIMIT 5")
        for row in cursor.fetchall():
            print(f"   - {row[0]}")
        
        print("\n📝 Примеры категорий приходов:")
        cursor.execute("SELECT name FROM income_categories WHERE is_active = 1 LIMIT 5")
        for row in cursor.fetchall():
            print(f"   - {row[0]}")
        
        conn.close()
        
        print("\n✅ Теперь Timeline должен работать!")
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        conn.close()
        return False

def check_tables(db_path="finance_v5.db"):
    """Проверка существования таблиц"""
    
    print("\n🔍 Проверка таблиц в БД...")
    print("="*50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Список всех таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📊 Найдено таблиц: {len(tables)}")
    
    required_tables = [
        "expense_categories",
        "income_categories",
        "timeline",
        "expenses",
        "income",
        "sales",
        "salaries"
    ]
    
    print("\n✅ Обязательные таблицы:")
    for table in required_tables:
        exists = "✅" if table in tables else "❌"
        print(f"   {exists} {table}")
    
    conn.close()
    print("="*50)

if __name__ == "__main__":
    DB_PATH = "finance_v5.db"
    
    print("="*50)
    print("ИСПРАВЛЕНИЕ ТАБЛИЦ КАТЕГОРИЙ")
    print("="*50)
    
    # Проверка таблиц
    check_tables(DB_PATH)
    
    # Создание категорий
    success = create_categories_tables(DB_PATH)
    
    if success:
        print("\n🎉 Готово! Запускай приложение:")
        print("   python3 main_app.py")
    else:
        print("\n❌ Что-то пошло не так. Проверь ошибки выше.")
        sys.exit(1)
