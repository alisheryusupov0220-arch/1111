#!/usr/bin/env python3
"""
Форма менеджера V5 - просмотр отчётов и балансов
"""

from database_v5 import FinanceSystemV5
from datetime import date, timedelta
import json

def show_menu():
    print("\n" + "=" * 70)
    print("  МЕНЮ МЕНЕДЖЕРА")
    print("=" * 70)
    print("\n1. Показать балансы счетов")
    print("2. Посмотреть отчёты за период")
    print("3. Изменить привязку метода оплаты к РС")
    print("4. Редактировать отчёт")
    print("0. Выход")
    print("=" * 70)

def show_balances(db):
    """Показать балансы всех счетов"""
    balances = db.get_account_balance()
    
    print("\n" + "=" * 70)
    print("  💰 БАЛАНСЫ СЧЕТОВ")
    print("=" * 70)
    
    total = 0
    cash_total = 0
    bank_total = 0
    
    for acc_id, data in balances.items():
        acc_emoji = "💵" if data['type'] == 'cash' else "🏦"
        print(f"\n{acc_emoji} {data['name']}:")
        print(f"  Продажи:        {data['sales_income']:,.2f} сум")
        print(f"  Прочие приходы: {data['non_sales_income']:,.2f} сум")
        print(f"  Расходы:        {data['expenses']:,.2f} сум")
        print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  БАЛАНС:         {data['balance']:,.2f} сум")
        
        total += data['balance']
        if data['type'] == 'cash':
            cash_total += data['balance']
        else:
            bank_total += data['balance']
    
    print("\n" + "=" * 70)
    print(f"  💵 Наличные:     {cash_total:,.2f} сум")
    print(f"  🏦 На РС:        {bank_total:,.2f} сум")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  📊 ИТОГО:        {total:,.2f} сум")
    print("=" * 70)

def show_reports(db):
    """Посмотреть отчёты"""
    print("\n" + "=" * 70)
    print("  📊 ОТЧЁТЫ ЗА ПЕРИОД")
    print("=" * 70)
    
    print("\nВыберите период:")
    print("1. Сегодня")
    print("2. Вчера")
    print("3. За 7 дней")
    print("4. За 30 дней")
    
    choice = input("\nВыбор: ").strip()
    
    end_date = date.today()
    
    if choice == '1':
        start_date = date.today()
    elif choice == '2':
        start_date = date.today() - timedelta(days=1)
        end_date = start_date
    elif choice == '3':
        start_date = date.today() - timedelta(days=7)
    elif choice == '4':
        start_date = date.today() - timedelta(days=30)
    else:
        print("❌ Неверный выбор")
        return
    
    # Получаем все отчёты за период
    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT dr.*, l.name as location_name
        FROM daily_reports dr
        JOIN locations l ON dr.location_id = l.id
        WHERE dr.report_date BETWEEN ? AND ?
        ORDER BY dr.report_date DESC
    ''', (start_date.isoformat(), end_date.isoformat()))
    
    reports = [dict(row) for row in cursor.fetchall()]
    
    if not reports:
        print("\n❌ Отчётов за этот период нет")
        return
    
    print(f"\n📋 Найдено отчётов: {len(reports)}")
    
    for report in reports:
        print(f"\n{'─' * 70}")
        print(f"📅 {report['report_date']} | {report['location_name']}")
        print(f"ID: {report['id']} | Статус: {report['status']}")
        print(f"  Продажи: {report['total_sales']:,.2f} сум")
        print(f"  Наличные: по отчёту {report['cash_expected']:,.2f}, факт {report['cash_actual']:,.2f}")
        
        if report['cash_difference'] != 0:
            diff_emoji = "⚠️" if report['cash_difference'] < 0 else "✅"
            print(f"  Разница: {report['cash_difference']:,.2f} сум {diff_emoji}")

def change_payment_method_account(db):
    """Изменить привязку метода оплаты к РС"""
    print("\n" + "=" * 70)
    print("  ⚙️ ИЗМЕНЕНИЕ ПРИВЯЗКИ МЕТОДА К РС")
    print("=" * 70)
    
    # Показываем все методы
    methods = db.get_payment_methods()
    print("\nТекущие методы оплаты:")
    for pm in methods:
        type_emoji = {'terminal': '📟', 'online': '🌐', 'delivery': '🚚'}
        emoji = type_emoji.get(pm['method_type'], '💳')
        print(f"  {pm['id']}. {emoji} {pm['name']}")
        print(f"      → {pm['default_account_name']}")
    
    method_id = int(input("\nID метода для изменения: "))
    
    # Показываем РС счета
    accounts = db.get_accounts('bank')
    print("\nДоступные РС счета:")
    for acc in accounts:
        print(f"  {acc['id']}. {acc['name']}")
    
    account_id = int(input("\nНовый РС счёт: "))
    
    db.update_payment_method_default_account(method_id, account_id)
    print("\n✅ Привязка изменена!")

def edit_report(db):
    """Редактировать закрытый отчёт"""
    print("\n" + "=" * 70)
    print("  ✏️ РЕДАКТИРОВАНИЕ ОТЧЁТА")
    print("=" * 70)
    
    report_id = int(input("\nID отчёта: "))
    
    report = db.get_report_details(report_id)
    
    if not report:
        print("❌ Отчёт не найден")
        return
    
    print(f"\n📋 Отчёт #{report_id} от {report['report_date']}")
    print(f"Точка: {report['location_name']}")
    print(f"Продажи: {report['total_sales']:,.2f} сум")
    print(f"Статус: {report['status']}")
    
    print("\nЧто изменить:")
    print("1. Изменить привязку платежа к РС")
    print("2. Открыть отчёт заново (сменить статус на 'open')")
    print("0. Назад")
    
    choice = input("\nВыбор: ").strip()
    
    if choice == '1':
        if report['payments']:
            print("\nПлатежи в отчёте:")
            for pay in report['payments']:
                if pay['payment_method_id']:
                    print(f"  {pay['id']}. {pay['payment_method_name']}: {pay['amount']:,.2f} → {pay['account_name']}")
            
            payment_id = int(input("\nID платежа для изменения: "))
            
            accounts = db.get_accounts('bank')
            print("\nНовый РС:")
            for acc in accounts:
                print(f"  {acc['id']}. {acc['name']}")
            
            new_account_id = int(input("Счёт: "))
            
            cursor = db.conn.cursor()
            cursor.execute('UPDATE report_payments SET account_id=? WHERE id=?', (new_account_id, payment_id))
            db.conn.commit()
            print("✅ Изменено!")
        else:
            print("❌ Нет платежей в отчёте")
    
    elif choice == '2':
        cursor = db.conn.cursor()
        cursor.execute("UPDATE daily_reports SET status='open' WHERE id=?", (report_id,))
        db.conn.commit()
        print("✅ Отчёт открыт для редактирования!")

def main():
    db = FinanceSystemV5()
    
    while True:
        show_menu()
        choice = input("\nВыбор: ").strip()
        
        try:
            if choice == '1':
                show_balances(db)
            elif choice == '2':
                show_reports(db)
            elif choice == '3':
                change_payment_method_account(db)
            elif choice == '4':
                edit_report(db)
            elif choice == '0':
                print("\nДо свидания!")
                break
            else:
                print("❌ Неверный выбор")
        
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
        
        input("\nНажмите Enter...")
    
    db.close()

if __name__ == '__main__':
    main()
