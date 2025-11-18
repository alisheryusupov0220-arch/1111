import sqlite3

db = sqlite3.connect('finance_v5.db')
db.row_factory = sqlite3.Row
cursor = db.cursor()

print("=" * 60)
print("ДИАГНОСТИКА БАЗЫ ДАННЫХ")
print("=" * 60)

# 1. Проверка отчётов
print("\n1. ВСЕ ОТЧЁТЫ В БД:")
cursor.execute("SELECT id, report_date, location_id, status FROM daily_reports")
reports = cursor.fetchall()
for r in reports:
    print(f"   ID: {r['id']}, Дата: {r['report_date']}, Точка: {r['location_id']}, Статус: {r['status']}")

# 2. Проверка закрытых отчётов
print("\n2. ТОЛЬКО ЗАКРЫТЫЕ (status='closed'):")
cursor.execute("SELECT id, report_date, status FROM daily_reports WHERE status='closed'")
closed = cursor.fetchall()
if closed:
    for r in closed:
        print(f"   ID: {r['id']}, Дата: {r['report_date']}, Статус: {r['status']}")
else:
    print("   НЕТ ЗАКРЫТЫХ ОТЧЁТОВ!")

# 3. Проверка таблицы daily_report_payments
print("\n3. ТАБЛИЦА daily_report_payments:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_report_payments'")
if cursor.fetchone():
    print("   ✅ Таблица существует")
    cursor.execute("SELECT COUNT(*) as cnt FROM daily_report_payments")
    count = cursor.fetchone()['cnt']
    print(f"   Записей: {count}")
else:
    print("   ❌ ТАБЛИЦА НЕ СУЩЕСТВУЕТ!")

# 4. Проверка колонок в daily_reports
print("\n4. КОЛОНКИ В daily_reports:")
cursor.execute("PRAGMA table_info(daily_reports)")
columns = [row['name'] for row in cursor.fetchall()]
print(f"   Всего колонок: {len(columns)}")
for col in ['expenses', 'other_income']:
    if col in columns:
        print(f"   ✅ {col} - есть")
    else:
        print(f"   ❌ {col} - НЕТ!")

# 5. Что вернёт get_reports()
print("\n5. ЧТО ВЕРНЁТ get_reports(status='closed'):")
from database_v5 import FinanceSystemV5
db_obj = FinanceSystemV5()
reports = db_obj.get_reports(limit=100, status='closed')
print(f"   Найдено отчётов: {len(reports)}")
if reports:
    for r in reports:
        print(f"   ID: {r['id']}, Дата: {r.get('report_date', 'НЕТ ДАТЫ')}")

print("\n" + "=" * 60)
print("ДИАГНОСТИКА ЗАВЕРШЕНА")
print("=" * 60)

db.close()



