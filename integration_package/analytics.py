#!/usr/bin/env python3
"""
Модуль аналитики - дашборд с анализом финансов
Показывает структуру расходов, прибыльность, динамику
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import calendar
from database_v5 import FinanceSystemV5

class AnalyticsWindow:
    """Окно аналитики"""
    
    def __init__(self, parent_db):
        self.db = parent_db
        
        # Создаём окно
        self.window = tk.Toplevel()
        self.window.title("📊 Аналитика и отчёты")
        self.window.geometry("1400x900")
        
        # Текущий месяц
        now = datetime.now()
        self.current_month = now.month
        self.current_year = now.year
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Создать интерфейс"""
        
        # Верхняя панель - выбор периода
        top_frame = ttk.Frame(self.window)
        top_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(top_frame, text="📊 АНАЛИТИКА", font=('Arial', 20, 'bold')).pack(side='left')
        
        # Выбор месяца
        period_frame = ttk.Frame(top_frame)
        period_frame.pack(side='right')
        
        ttk.Button(period_frame, text="◀", width=3, command=self.prev_month).pack(side='left', padx=2)
        
        self.period_label = ttk.Label(period_frame, text="", font=('Arial', 14, 'bold'))
        self.period_label.pack(side='left', padx=10)
        
        ttk.Button(period_frame, text="▶", width=3, command=self.next_month).pack(side='left', padx=2)
        ttk.Button(period_frame, text="Сегодня", command=self.today).pack(side='left', padx=10)
        
        # Основной контейнер с прокруткой
        main_canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        # Контейнер для данных
        self.content_frame = scrollable_frame
        
        self.update_period_label()
    
    def update_period_label(self):
        """Обновить надпись периода"""
        month_name = calendar.month_name[self.current_month]
        self.period_label.config(text=f"{month_name} {self.current_year}")
    
    def prev_month(self):
        """Предыдущий месяц"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_period_label()
        self.load_data()
    
    def next_month(self):
        """Следующий месяц"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_period_label()
        self.load_data()
    
    def today(self):
        """Вернуться к текущему месяцу"""
        now = datetime.now()
        self.current_month = now.month
        self.current_year = now.year
        self.update_period_label()
        self.load_data()
    
    def load_data(self):
        """Загрузить данные за месяц"""
        
        # Очистить содержимое
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Период
        start_date = f"{self.current_year}-{self.current_month:02d}-01"
        last_day = calendar.monthrange(self.current_year, self.current_month)[1]
        end_date = f"{self.current_year}-{self.current_month:02d}-{last_day}"
        
        # Получаем данные
        reports = self.get_reports_for_period(start_date, end_date)
        
        if not reports:
            ttk.Label(self.content_frame, 
                     text="📭 Нет данных за выбранный период",
                     font=('Arial', 16)).pack(pady=50)
            return
        
        # Анализируем данные
        analytics = self.analyze_data(reports)
        
        # Показываем аналитику
        self.show_summary(analytics)
        self.show_structure(analytics)
        self.show_profitability(analytics)
        self.show_balances(analytics)
        self.show_categories(analytics)
        self.show_daily_table(reports)
    
    def get_reports_for_period(self, start_date, end_date):
        """Получить отчёты за период"""
        query = """
        SELECT 
            dr.id,
            dr.report_date,
            dr.location_id,
            l.name as location_name,
            dr.total_sales,
            dr.cash_actual,
            dr.created_by
        FROM daily_reports dr
        LEFT JOIN locations l ON dr.location_id = l.id
        WHERE dr.report_date BETWEEN ? AND ?
        ORDER BY dr.report_date DESC
        """
        
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, (start_date, end_date))
        reports = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Для каждого отчёта получаем детали
        for report in reports:
            report['payments'] = self.get_report_payments(report['id'])
            report['expenses'] = self.get_report_expenses(report['id'])
            report['incomes'] = self.get_report_incomes(report['id'])
        
        return reports
    
    def get_report_payments(self, report_id):
        """Получить платежи отчёта"""
        query = """
        SELECT pm.name, rp.amount, rp.fee_amount
        FROM report_payments rp
        LEFT JOIN payment_methods pm ON rp.method_id = pm.id
        WHERE rp.report_id = ?
        """
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(query, (report_id,))
        payments = cursor.fetchall()
        conn.close()
        return [{'name': p[0], 'amount': p[1], 'fee': p[2]} for p in payments]
    
    def get_report_expenses(self, report_id):
        """Получить расходы отчёта"""
        query = """
        SELECT ec.name, e.amount, e.description
        FROM expenses e
        LEFT JOIN expense_categories ec ON e.category_id = ec.id
        WHERE e.report_id = ?
        """
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(query, (report_id,))
        expenses = cursor.fetchall()
        conn.close()
        return [{'category': e[0] or 'Без категории', 'amount': e[1], 'desc': e[2]} for e in expenses]
    
    def get_report_incomes(self, report_id):
        """Получить приходы отчёта"""
        query = """
        SELECT ic.name, i.amount, i.description
        FROM incomes i
        LEFT JOIN income_categories ic ON i.category_id = ic.id
        WHERE i.report_id = ?
        """
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(query, (report_id,))
        incomes = cursor.fetchall()
        conn.close()
        return [{'category': i[0] or 'Без категории', 'amount': i[1], 'desc': i[2]} for i in incomes]
    
    def analyze_data(self, reports):
        """Анализировать данные"""
        
        total_sales = 0
        total_cash = 0
        total_card = 0
        total_expenses = 0
        total_incomes = 0
        total_fees = 0
        
        # Расходы по категориям
        expense_categories = {}
        
        # Продажи по дням
        daily_sales = []
        
        for report in reports:
            total_sales += report['total_sales']
            total_cash += report['cash_actual']
            
            # Безнал
            card_amount = sum(p['amount'] for p in report['payments'])
            total_card += card_amount
            
            # Комиссии
            fees = sum(p['fee'] for p in report['payments'])
            total_fees += fees
            
            # Расходы
            for exp in report['expenses']:
                amount = exp['amount']
                total_expenses += amount
                category = exp['category']
                expense_categories[category] = expense_categories.get(category, 0) + amount
            
            # Приходы
            for inc in report['incomes']:
                total_incomes += inc['amount']
            
            # По дням
            daily_sales.append({
                'date': report['report_date'],
                'sales': report['total_sales']
            })
        
        # Группировка расходов по типам (food cost, labor, etc.)
        expense_groups = self.group_expenses(expense_categories)
        
        # Прибыльность
        gross_profit = total_sales - total_expenses
        net_profit = gross_profit - total_fees
        
        if total_sales > 0:
            gross_margin = (gross_profit / total_sales) * 100
            net_margin = (net_profit / total_sales) * 100
        else:
            gross_margin = 0
            net_margin = 0
        
        return {
            'total_sales': total_sales,
            'total_cash': total_cash,
            'total_card': total_card,
            'total_expenses': total_expenses,
            'total_incomes': total_incomes,
            'total_fees': total_fees,
            'expense_categories': expense_categories,
            'expense_groups': expense_groups,
            'gross_profit': gross_profit,
            'net_profit': net_profit,
            'gross_margin': gross_margin,
            'net_margin': net_margin,
            'daily_sales': daily_sales,
            'reports_count': len(reports)
        }
    
    def group_expenses(self, expense_categories):
        """Группировать расходы по типам"""
        
        groups = {
            'Food Cost': 0,
            'Labor Cost': 0,
            'Rent': 0,
            'Marketing': 0,
            'Other': 0
        }
        
        # Маппинг категорий к группам
        food_keywords = ['закуп', 'фирма', 'базар', 'пепси', 'сыр', 'хлеб', 'корзинка', 'хавас', 'продукт', 'бар']
        labor_keywords = ['зарплата', 'аванс', 'обед']
        rent_keywords = ['аренда']
        marketing_keywords = ['ивент', 'маркетинг']
        
        for category, amount in expense_categories.items():
            cat_lower = category.lower()
            
            if any(kw in cat_lower for kw in food_keywords):
                groups['Food Cost'] += amount
            elif any(kw in cat_lower for kw in labor_keywords):
                groups['Labor Cost'] += amount
            elif any(kw in cat_lower for kw in rent_keywords):
                groups['Rent'] += amount
            elif any(kw in cat_lower for kw in marketing_keywords):
                groups['Marketing'] += amount
            else:
                groups['Other'] += amount
        
        return groups
    
    def show_summary(self, analytics):
        """Показать общую сводку"""
        frame = ttk.LabelFrame(self.content_frame, text="📊 ОБЩИЕ ПОКАЗАТЕЛИ", padding=20)
        frame.pack(fill='x', pady=10)
        
        # Сетка 2x3
        data = [
            ("💰 Продажи:", self.format_sum(analytics['total_sales'])),
            ("💵 Наличные:", self.format_sum(analytics['total_cash'])),
            ("💳 Безнал:", self.format_sum(analytics['total_card'])),
            ("💸 Расходы:", self.format_sum(analytics['total_expenses'])),
            ("💰 Приходы:", self.format_sum(analytics['total_incomes'])),
            ("📊 Отчётов:", str(analytics['reports_count'])),
        ]
        
        for i, (label, value) in enumerate(data):
            row = i // 3
            col = (i % 3) * 2
            
            ttk.Label(frame, text=label, font=('Arial', 11, 'bold')).grid(row=row, column=col, sticky='w', padx=5, pady=5)
            ttk.Label(frame, text=value, font=('Arial', 11)).grid(row=row, column=col+1, sticky='w', padx=5, pady=5)
    
    def show_structure(self, analytics):
        """Показать структуру расходов"""
        frame = ttk.LabelFrame(self.content_frame, text="📈 СТРУКТУРА РАСХОДОВ", padding=20)
        frame.pack(fill='x', pady=10)
        
        total = analytics['total_expenses']
        if total == 0:
            ttk.Label(frame, text="Нет расходов за период").pack()
            return
        
        groups = analytics['expense_groups']
        
        # Сортируем по сумме
        sorted_groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)
        
        for i, (group, amount) in enumerate(sorted_groups):
            if amount == 0:
                continue
            
            percent = (amount / total) * 100
            
            row_frame = ttk.Frame(frame)
            row_frame.pack(fill='x', pady=5)
            
            # Название
            ttk.Label(row_frame, text=f"{group}:", font=('Arial', 10, 'bold'), width=15).pack(side='left')
            
            # Прогресс бар
            progress = ttk.Progressbar(row_frame, length=300, mode='determinate')
            progress['value'] = percent
            progress.pack(side='left', padx=10)
            
            # Сумма и процент
            ttk.Label(row_frame, text=f"{self.format_sum(amount)} ({percent:.1f}%)").pack(side='left')
    
    def show_profitability(self, analytics):
        """Показать прибыльность"""
        frame = ttk.LabelFrame(self.content_frame, text="💹 ПРИБЫЛЬНОСТЬ", padding=20)
        frame.pack(fill='x', pady=10)
        
        data = [
            ("Валовая прибыль:", analytics['gross_profit'], analytics['gross_margin']),
            ("Комиссии:", -analytics['total_fees'], 0),
            ("Чистая прибыль:", analytics['net_profit'], analytics['net_margin']),
        ]
        
        for i, (label, amount, percent) in enumerate(data):
            row_frame = ttk.Frame(frame)
            row_frame.pack(fill='x', pady=5)
            
            ttk.Label(row_frame, text=label, font=('Arial', 11, 'bold'), width=20).pack(side='left')
            
            color = 'green' if amount >= 0 else 'red'
            amount_text = self.format_sum(amount)
            
            amount_label = ttk.Label(row_frame, text=amount_text, font=('Arial', 11))
            amount_label.pack(side='left', padx=10)
            
            if percent > 0:
                ttk.Label(row_frame, text=f"({percent:.1f}%)", font=('Arial', 10)).pack(side='left')
    
    def show_balances(self, analytics):
        """Показать остатки"""
        frame = ttk.LabelFrame(self.content_frame, text="💰 ОСТАТКИ", padding=20)
        frame.pack(fill='x', pady=10)
        
        # TODO: Получить реальные остатки из account_balance_history
        ttk.Label(frame, text="🚧 В разработке - будет показывать динамику остатков по дням").pack()
    
    def show_categories(self, analytics):
        """Показать топ категорий"""
        frame = ttk.LabelFrame(self.content_frame, text="📂 ТОП КАТЕГОРИЙ РАСХОДОВ", padding=20)
        frame.pack(fill='x', pady=10)
        
        categories = analytics['expense_categories']
        if not categories:
            ttk.Label(frame, text="Нет данных").pack()
            return
        
        # Топ-10
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Таблица
        cols = ('Категория', 'Сумма', '%')
        tree = ttk.Treeview(frame, columns=cols, show='headings', height=10)
        
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        total = analytics['total_expenses']
        
        for category, amount in sorted_cats:
            percent = (amount / total * 100) if total > 0 else 0
            tree.insert('', 'end', values=(
                category,
                self.format_sum(amount),
                f"{percent:.1f}%"
            ))
        
        tree.pack(fill='x')
    
    def show_daily_table(self, reports):
        """Показать таблицу по дням"""
        frame = ttk.LabelFrame(self.content_frame, text="📅 ОТЧЁТЫ ПО ДНЯМ", padding=20)
        frame.pack(fill='both', expand=True, pady=10)
        
        # Таблица
        cols = ('Дата', 'Точка', 'Продажи', 'Наличные', 'Безнал', 'Расходы')
        tree = ttk.Treeview(frame, columns=cols, show='headings', height=15)
        
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        for report in reports:
            card_amount = sum(p['amount'] for p in report['payments'])
            expenses_total = sum(e['amount'] for e in report['expenses'])
            
            tree.insert('', 'end', values=(
                report['report_date'],
                report['location_name'],
                self.format_sum(report['total_sales']),
                self.format_sum(report['cash_actual']),
                self.format_sum(card_amount),
                self.format_sum(expenses_total)
            ))
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        tree.pack(fill='both', expand=True)
    
    def format_sum(self, amount):
        """Форматировать сумму"""
        return f"{amount:,.0f}".replace(',', ' ')

import sqlite3

if __name__ == "__main__":
    # Тест
    db = FinanceSystemV5()
    root = tk.Tk()
    root.withdraw()
    app = AnalyticsWindow(db)
    root.mainloop()
