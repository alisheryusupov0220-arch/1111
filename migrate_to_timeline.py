#!/usr/bin/env python3
"""
Скрипт переноса данных в Timeline
Переносит все операции из существующих таблиц в единую таблицу timeline
"""

import sqlite3
from datetime import datetime

DB_PATH = 'finance_v5.db'

def migrate_data():
    """Перенос данных в timeline"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("🚀 Начинаем миграцию данных в Timeline...\n")
    
    total_migrated = 0
    
    # 1. Миграция расходов из report_expenses
    print("📉 Миграция расходов...")
    cursor.execute("""
        SELECT re.id, dr.report_date, re.category_id, re.account_id, 
               re.amount, re.description, dr.id as report_id
        FROM report_expenses re
        JOIN daily_reports dr ON re.report_id = dr.id
        WHERE dr.status = 'closed'
    """)
    expenses = cursor.fetchall()
    
    expenses_count = 0
    for exp in expenses:
        cursor.execute("""
            INSERT INTO timeline (date, type, category_id, account_id, amount, description, report_id, source)
            VALUES (?, 'expense', ?, ?, ?, ?, ?, 'desktop')
        """, (exp['report_date'], exp['category_id'], exp['account_id'], 
              exp['amount'], exp['description'], exp['report_id']))
        expenses_count += 1
    
    print(f"   ✅ Перенесено расходов: {expenses_count}")
    total_migrated += expenses_count
    
    # 2. Миграция приходов из non_sales_income
    print("\n📈 Миграция приходов...")
    cursor.execute("""
        SELECT nsi.id, dr.report_date, nsi.category_id, nsi.account_id,
               nsi.amount, nsi.description, dr.id as report_id
        FROM non_sales_income nsi
        JOIN daily_reports dr ON nsi.report_id = dr.id
        WHERE dr.status = 'closed'
    """)
    income = cursor.fetchall()
    
    income_count = 0
    for inc in income:
        cursor.execute("""
            INSERT INTO timeline (date, type, category_id, account_id, amount, description, report_id, source)
            VALUES (?, 'income', ?, ?, ?, ?, ?, 'desktop')
        """, (inc['report_date'], inc['category_id'], inc['account_id'],
              inc['amount'], inc['description'], inc['report_id']))
        income_count += 1
    
    print(f"   ✅ Перенесено приходов: {income_count}")
    total_migrated += income_count
    
    # 3. Миграция продаж из daily_report_payments
    print("\n💰 Миграция продаж...")
    cursor.execute("""
        SELECT drp.id, dr.report_date, drp.payment_method_id,
               drp.amount, dr.id as report_id, pm.name as payment_name,
               pm.default_account_id, pm.method_type
        FROM daily_report_payments drp
        JOIN daily_reports dr ON drp.report_id = dr.id
        LEFT JOIN payment_methods pm ON drp.payment_method_id = pm.id
        WHERE dr.status = 'closed'
    """)
    payments = cursor.fetchall()
    
    sales_cash_count = 0
    sales_cashless_count = 0
    for pay in payments:
        # Определяем тип продажи по типу метода оплаты
        method_type = pay['method_type'] if pay['method_type'] else 'terminal'
        account_id = pay['default_account_id'] if pay['default_account_id'] else None
        
        # Продажи наличными и безналом
        sale_type = 'sale'
        description = f"Продажа ({pay['payment_name'] or 'Неизвестный метод'})"
        
        cursor.execute("""
            INSERT INTO timeline (date, type, account_id, amount, description, 
                                 report_id, payment_method_id, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'desktop')
        """, (pay['report_date'], sale_type, account_id, pay['amount'],
              description, pay['report_id'], pay['payment_method_id']))
        
        if method_type == 'terminal' or method_type == 'online':
            sales_cashless_count += 1
        else:
            sales_cash_count += 1
    
    print(f"   ✅ Перенесено продаж наличными: {sales_cash_count}")
    print(f"   ✅ Перенесено продаж безналом: {sales_cashless_count}")
    total_migrated += sales_cash_count + sales_cashless_count
    
    # 4. Миграция зарплат (если есть таблица salaries)
    print("\n👔 Миграция зарплат...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='salaries'")
    if cursor.fetchone():
        cursor.execute("""
            SELECT date, employee_id, amount, description
            FROM salaries
        """)
        salaries = cursor.fetchall()
        
        salary_count = 0
        for sal in salaries:
            cursor.execute("""
                INSERT INTO timeline (date, type, amount, description, source)
                VALUES (?, 'salary', ?, ?, 'desktop')
            """, (sal['date'], sal['amount'], sal['description']))
            salary_count += 1
        
        print(f"   ✅ Перенесено зарплат: {salary_count}")
        total_migrated += salary_count
    else:
        print("   ⚠️ Таблица salaries не найдена, пропускаем")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ МИГРАЦИЯ ЗАВЕРШЕНА!")
    print(f"📊 Всего перенесено операций: {total_migrated}")
    
    # Проверка
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM timeline")
    count = cursor.fetchone()[0]
    print(f"📈 Всего записей в timeline: {count}")
    conn.close()

if __name__ == '__main__':
    try:
        migrate_data()
    except Exception as e:
        print(f"❌ Ошибка при миграции: {e}")
        import traceback
        traceback.print_exc()

