#!/usr/bin/env python3
"""
Форма кассира - Дневной отчёт V5
С валидацией ввода
"""

from database_v5 import FinanceSystemV5
from validation import safe_float, safe_int, safe_date, confirm
from datetime import date

def show_header():
    print("\n" + "=" * 70)
    print("  📊 ДНЕВНОЙ ОТЧЁТ КАССИРА")
    print("=" * 70)

def select_date():
    """Выбор даты"""
    print("\nДата:")
    print("1. Сегодня")
    print("2. Другая дата")
    
    choice = safe_int("Выбор: ", valid_values=[1, 2])
    
    if choice == 2:
        return safe_date()
    else:
        return date.today()

def select_location(db):
    """Выбор точки"""
    locations = db.get_locations()
    print("\n📍 Выберите точку:")
    for loc in locations:
        print(f"  {loc['id']}. {loc['name']}")
    
    valid_ids = [loc['id'] for loc in locations]
    loc_id = safe_int("\nТочка: ", valid_values=valid_ids)
    return loc_id

def input_sales(db, report_id, report_date, location_id):
    """Ввод продаж"""
    print("\n" + "=" * 70)
    print("  💰 ПРОДАЖИ")
    print("=" * 70)
    
    # Общая сумма продаж
    total_sales = safe_float("\nОбщая сумма продаж с учётом скидок: ", min_value=0, allow_zero=False)
    
    # Обновляем отчёт
    cursor = db.conn.cursor()
    cursor.execute('UPDATE daily_reports SET total_sales=? WHERE id=?', (total_sales, report_id))
    db.conn.commit()
    
    total_cashless = 0
    
    # ========== ТЕРМИНАЛЫ ==========
    print("\n📟 ТЕРМИНАЛЫ:")
    terminals = db.get_payment_methods('terminal')
    
    for term in terminals:
        amount = safe_float(f"  {term['name']} (комиссия {term['commission_percent']}%): ", min_value=0)
        if amount:
            db.add_report_payment(report_id, term['id'], term['default_account_id'], amount)
            net = amount * (1 - term['commission_percent']/100)
            total_cashless += amount
            print(f"    → На РС зачислится: {net:,.2f} сум")
    
    # ========== ОНЛАЙН ==========
    print("\n🌐 ОНЛАЙН ПЛАТЕЖИ:")
    online = db.get_payment_methods('online')
    
    for ol in online:
        amount = safe_float(f"  {ol['name']} (комиссия {ol['commission_percent']}%): ", min_value=0)
        if amount:
            db.add_report_payment(report_id, ol['id'], ol['default_account_id'], amount)
            net = amount * (1 - ol['commission_percent']/100)
            total_cashless += amount
            print(f"    → На РС зачислится: {net:,.2f} сум")
    
    # ========== ДОСТАВКИ ==========
    print("\n🚚 ДОСТАВКИ:")
    delivery = db.get_payment_methods('delivery')
    
    for deliv in delivery:
        amount = safe_float(f"  {deliv['name']} (комиссия {deliv['commission_percent']}%): ", min_value=0)
        if amount:
            db.add_report_payment(report_id, deliv['id'], deliv['default_account_id'], amount)
            net = amount * (1 - deliv['commission_percent']/100)
            total_cashless += amount
            print(f"    → На РС зачислится: {net:,.2f} сум")
    
    # Наличные по отчёту
    cash_expected = total_sales - total_cashless
    
    print("\n" + "=" * 70)
    print(f"  Общая сумма продаж: {total_sales:,.2f} сум")
    print(f"  Всего безнал:       {total_cashless:,.2f} сум")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Наличных по отчёту: {cash_expected:,.2f} сум")
    print("=" * 70)
    
    return cash_expected

def input_cash_count():
    """Подсчёт фактических наличных"""
    print("\n" + "=" * 70)
    print("  💵 ПОДСЧЁТ НАЛИЧНЫХ В КАССЕ")
    print("=" * 70)
    print("\nВведите количество купюр и монет (Enter - пропустить):")
    
    denominations = {
        200000: "200,000 сум",
        100000: "100,000 сум",
        50000: "50,000 сум",
        20000: "20,000 сум",
        10000: "10,000 сум",
        5000: "5,000 сум",
        1000: "1,000 сум",
        500: "500 сум",
        200: "200 сум",
        100: "100 сум",
        50: "50 сум"
    }
    
    breakdown = {}
    total_actual = 0
    
    for value, label in denominations.items():
        count = safe_int(f"  {label}: ", min_value=0)
        if count:
            breakdown[value] = count
            total_actual += value * count
        else:
            breakdown[value] = 0
    
    print("\n" + "=" * 70)
    print(f"  ИТОГО НАЛИЧНЫХ В КАССЕ: {total_actual:,.2f} сум")
    print("=" * 70)
    
    return total_actual, breakdown

def input_non_sales_income(db, report_id):
    """Приходы не от продаж"""
    print("\n" + "=" * 70)
    print("  📥 ПРИХОДЫ НЕ ОТ ПРОДАЖ")
    print("=" * 70)
    
    while True:
        add = input("\nДобавить приход? (да/нет): ").strip().lower()
        if add not in ['да', 'yes', 'y', 'д']:
            break
        
        # Выбор категории
        print("\nВыберите категорию:")
        income_cats = db.get_categories('income')
        for cat in income_cats:
            print(f"  {cat['id']}. {cat['name']}")
        print("  0. Добавить новую категорию")
        
        cat_choice = input("Категория: ").strip()
        
        if cat_choice == '0':
            new_cat_name = input("Название новой категории: ")
            category_id = db.add_category(new_cat_name, 'income')
            print(f"✅ Категория '{new_cat_name}' добавлена")
        else:
            category_id = int(cat_choice)
        
        # Сумма
        amount = float(input("Сумма: "))
        
        # Куда поступили (касса или РС)
        accounts = db.get_accounts()
        print("\nКуда поступили деньги:")
        for acc in accounts:
            print(f"  {acc['id']}. {acc['name']}")
        
        account_id = int(input("Счёт: "))
        
        description = input("Описание (необязательно): ").strip()
        
        db.add_non_sales_income(report_id, account_id, amount, category_id, description)
        print("✅ Приход добавлен")

def input_expenses(db, report_id):
    """Расходы за день"""
    print("\n" + "=" * 70)
    print("  💸 РАСХОДЫ ЗА ДЕНЬ")
    print("=" * 70)
    
    while True:
        add = input("\nДобавить расход? (да/нет): ").strip().lower()
        if add not in ['да', 'yes', 'y', 'д']:
            break
        
        # Выбор категории
        print("\nВыберите категорию:")
        expense_cats = db.get_categories('expense')
        for cat in expense_cats:
            print(f"  {cat['id']}. {cat['name']}")
            subcats = db.get_subcategories(cat['id'])
            for sub in subcats:
                print(f"      {sub['id']}. {sub['name']}")
        print("  0. Добавить новую категорию")
        
        cat_choice = input("Категория: ").strip()
        
        if cat_choice == '0':
            # Добавление новой категории
            print("\n1. Главная категория")
            print("2. Подкатегория")
            type_choice = input("Выбор: ").strip()
            
            if type_choice == '2':
                parent_id = int(input("ID главной категории: "))
                new_cat_name = input("Название подкатегории: ")
                category_id = db.add_category(new_cat_name, 'expense', parent_id)
            else:
                new_cat_name = input("Название категории: ")
                category_id = db.add_category(new_cat_name, 'expense')
            
            print(f"✅ Категория '{new_cat_name}' добавлена")
        else:
            category_id = int(cat_choice)
        
        # Сумма
        amount = float(input("Сумма: "))
        
        # Откуда списать
        accounts = db.get_accounts()
        print("\nОткуда списать:")
        for acc in accounts:
            print(f"  {acc['id']}. {acc['name']}")
        
        account_id = int(input("Счёт: "))
        
        description = input("Описание (необязательно): ").strip()
        
        db.add_report_expense(report_id, account_id, amount, category_id, description)
        print("✅ Расход добавлен")

def cashier_daily_report(db):
    """Основная функция - дневной отчёт"""
    show_header()
    
    # 1. Дата и точка
    report_date = select_date()
    location_id = select_location(db)
    
    print(f"\n📅 Дата: {report_date.strftime('%d.%m.%Y')}")
    
    # Проверяем, есть ли уже отчёт за эту дату
    existing = db.get_daily_report(report_date, location_id)
    if existing:
        print(f"\n⚠️  ВНИМАНИЕ: Отчёт за эту дату уже существует (ID: {existing['id']})")
        reopen = input("Открыть и редактировать? (да/нет): ").strip().lower()
        if reopen not in ['да', 'yes', 'y', 'д']:
            print("❌ Отменено")
            return
        report_id = existing['id']
    else:
        # Создаём новый отчёт
        report_id = db.create_daily_report(report_date, location_id, 0, "Кассир")
    
    # 2. Ввод продаж
    cash_expected = input_sales(db, report_id, report_date, location_id)
    
    # 3. Подсчёт наличных
    cash_actual, cash_breakdown = input_cash_count()
    
    # Разница
    cash_difference = cash_actual - cash_expected
    
    print("\n" + "=" * 70)
    print("  💵 СВЕРКА НАЛИЧНЫХ")
    print("=" * 70)
    print(f"  Должно быть по отчёту: {cash_expected:,.2f} сум")
    print(f"  Фактически в кассе:    {cash_actual:,.2f} сум")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    if cash_difference > 0:
        print(f"  ИЗЛИШЕК:               +{cash_difference:,.2f} сум ✅")
    elif cash_difference < 0:
        print(f"  НЕДОСТАЧА:             {cash_difference:,.2f} сум ⚠️")
    else:
        print(f"  БЕЗ РАСХОЖДЕНИЙ        {cash_difference:,.2f} сум ✅")
    
    print("=" * 70)
    
    # Сохраняем данные по наличным
    db.update_report_cash(report_id, cash_expected, cash_actual, cash_breakdown)
    
    # 4. Приходы не от продаж
    input_non_sales_income(db, report_id)
    
    # 5. Расходы
    input_expenses(db, report_id)
    
    # 6. Закрываем отчёт
    db.close_report(report_id)
    
    # 7. Итоговая информация
    print("\n" + "=" * 70)
    print("  ✅ ОТЧЁТ СОХРАНЁН И ЗАКРЫТ!")
    print("=" * 70)
    
    # Показываем итоги
    report_details = db.get_report_details(report_id)
    
    print(f"\n📊 ИТОГИ:")
    print(f"  ID отчёта: {report_id}")
    print(f"  Дата: {report_date.strftime('%d.%m.%Y')}")
    print(f"  Общая сумма продаж: {report_details['total_sales']:,.2f} сум")
    
    if report_details['payments']:
        print(f"\n  Безналичные платежи:")
        for payment in report_details['payments']:
            if payment['payment_method_id']:
                print(f"    {payment['payment_method_name']}: {payment['amount']:,.2f} сум → {payment['net_amount']:,.2f} сум")
    
    print(f"\n  Наличные:")
    print(f"    По отчёту: {report_details['cash_expected']:,.2f} сум")
    print(f"    Фактически: {report_details['cash_actual']:,.2f} сум")
    print(f"    Разница: {report_details['cash_difference']:,.2f} сум")
    
    if report_details['non_sales_income']:
        print(f"\n  Приходы не от продаж:")
        for income in report_details['non_sales_income']:
            print(f"    {income['category_name']}: {income['amount']:,.2f} сум")
    
    if report_details['expenses']:
        print(f"\n  Расходы:")
        for expense in report_details['expenses']:
            print(f"    {expense['category_name']}: {expense['amount']:,.2f} сум")
    
    print("\n" + "=" * 70)

def main():
    db = FinanceSystemV5()
    
    while True:
        try:
            cashier_daily_report(db)
            
            again = input("\nЗаполнить ещё один отчёт? (да/нет): ").strip().lower()
            if again not in ['да', 'yes', 'y', 'д']:
                break
        
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
        
        input("\nНажмите Enter...")
    
    db.close()
    print("\nДо свидания!")

if __name__ == '__main__':
    main()
