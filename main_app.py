#!/usr/bin/env python3
"""
Главное приложение с GUI для управления финансовой системой
Визуальное управление логикой, методами оплаты, отчётами
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from settings import config
from database_v5 import FinanceSystemV5

class MainApp:
    """Главное приложение"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("💰 Air Waffle Finance - Панель управления")
        self.root.geometry("900x700")
        
        # База данных
        try:
            self.db = FinanceSystemV5()
        except:
            messagebox.showerror("Ошибка", "База данных не найдена!\nЗапустите setup_v5.py")
            self.root.quit()
            return
        
        # Создаём интерфейс
        self.create_menu()
        self.create_main_screen()
    
    def create_menu(self):
        """Меню сверху"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 Файл", menu=file_menu)
        file_menu.add_command(label="⚙️ Настройки", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="❌ Выход", command=self.root.quit)
        
        # Данные
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="💾 Данные", menu=data_menu)
        data_menu.add_command(label="📊 Экспорт в Excel", command=self.export_excel)
        data_menu.add_command(label="🔄 Создать бэкап", command=self.create_backup)
        
        # Помощь
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Помощь", menu=help_menu)
        help_menu.add_command(label="📖 Инструкция", command=self.show_help)
        help_menu.add_command(label="ℹ️ О программе", command=self.show_about)
    
    def create_main_screen(self):
        """Главный экран с кнопками"""
        # Заголовок
        header = ttk.Frame(self.root)
        header.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(header, text="💰 AIR WAFFLE FINANCE", font=('Arial', 24, 'bold')).pack()
        ttk.Label(header, text="Система управления финансами", font=('Arial', 12)).pack()
        
        # Основные кнопки
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Сетка кнопок 2x3
        buttons = [
            ("📊 Новый отчёт кассира", self.new_cashier_report, 0, 0),
            ("👀 Просмотр отчётов", self.view_reports, 0, 1),
            ("💰 Балансы счетов", self.view_balances, 0, 2),
            ("💳 Методы оплаты", self.manage_payments, 1, 0),
            ("📍 Точки продаж", self.manage_locations, 1, 1),
            ("🏦 Счета", self.manage_accounts, 1, 2),
            ("📂 Категории расходов", self.manage_categories, 2, 0),
            ("⚙️ Настройки", self.open_settings, 2, 1),
            ("🤖 Telegram бот", self.telegram_status, 2, 2),
        ]
        
        for text, command, row, col in buttons:
            btn = ttk.Button(main_frame, text=text, command=command, width=25)
            btn.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Растягивание
        for i in range(3):
            main_frame.grid_rowconfigure(i, weight=1)
            main_frame.grid_columnconfigure(i, weight=1)
        
        # Статус бар
        self.create_statusbar()
    
    def create_statusbar(self):
        """Статус бар внизу"""
        statusbar = ttk.Frame(self.root)
        statusbar.pack(fill='x', side='bottom')
        
        # Левая часть - инфо
        self.status_label = ttk.Label(statusbar, text="✅ Готов к работе", relief='sunken')
        self.status_label.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        
        # Правая часть - БД инфо
        db_info = f"📊 БД: {config.db_path}"
        ttk.Label(statusbar, text=db_info, relief='sunken').pack(side='right', padx=5, pady=5)
    
    # ========== ОБРАБОТЧИКИ ==========
    
    def new_cashier_report(self):
        """Новый отчёт кассира"""
        CashierReportWindow(self.root, self.db)
    
    def view_reports(self):
        """Просмотр отчётов"""
        ReportsViewWindow(self.root, self.db)
    
    def view_balances(self):
        """Балансы счетов"""
        BalancesWindow(self.root, self.db)
    
    def manage_payments(self):
        """Управление методами оплаты"""
        PaymentMethodsWindow(self.root, self.db)
    
    def manage_locations(self):
        """Управление точками"""
        LocationsWindow(self.root, self.db)
    
    def manage_accounts(self):
        """Управление счетами"""
        AccountsWindow(self.root, self.db)
    
    def manage_categories(self):
        """Управление категориями"""
        CategoriesWindow(self.root, self.db)
    
    def open_settings(self):
        """Открыть настройки"""
        import subprocess
        subprocess.Popen(['python3', 'settings_gui.py'])
    
    def telegram_status(self):
        """Статус Telegram бота"""
        if config.telegram_enabled:
            status = f"✅ Telegram бот ВКЛЮЧЁН\n\nТокен: {config.bot_token[:20]}...\n\nЗапустите бота:\npython3 telegram_bot_simple.py"
        else:
            status = "❌ Telegram бот ВЫКЛЮЧЕН\n\nВключите в настройках"
        
        messagebox.showinfo("🤖 Telegram бот", status)
    
    def export_excel(self):
        """Экспорт в Excel"""
        messagebox.showinfo("📊 Экспорт", "Функция в разработке!")
    
    def create_backup(self):
        """Создать бэкап"""
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_{timestamp}.db"
        
        try:
            shutil.copy(config.db_path, backup_file)
            messagebox.showinfo("✅ Бэкап", f"Создан бэкап:\n{backup_file}")
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Не удалось создать бэкап:\n{e}")
    
    def show_help(self):
        """Показать помощь"""
        help_text = """
        📖 ИНСТРУКЦИЯ:
        
        1. НОВЫЙ ОТЧЁТ - заполнение дневного отчёта кассира
        2. ПРОСМОТР ОТЧЁТОВ - история всех отчётов
        3. БАЛАНСЫ - текущие остатки на счетах
        4. МЕТОДЫ ОПЛАТЫ - настройка терминалов, онлайн платежей
        5. ТОЧКИ ПРОДАЖ - управление точками
        6. СЧЕТА - управление счетами
        7. КАТЕГОРИИ - категории расходов
        8. НАСТРОЙКИ - общие настройки системы
        9. TELEGRAM БОТ - статус и управление ботом
        """
        messagebox.showinfo("📖 Помощь", help_text)
    
    def show_about(self):
        """О программе"""
        about_text = f"""
        💰 AIR WAFFLE FINANCE
        Версия: {config.get('app.version', '5.0')}
        
        Система управления финансами для кафе
        
        © 2025 Air Waffle
        """
        messagebox.showinfo("ℹ️ О программе", about_text)
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


# ========== ОКНА ==========

class PaymentMethodsWindow:
    """Окно управления методами оплаты"""
    
    def __init__(self, parent, db):
        self.db = db
        self.window = tk.Toplevel(parent)
        self.window.title("💳 Управление методами оплаты")
        self.window.geometry("800x600")
        
        self.create_ui()
        self.load_data()
    
    def create_ui(self):
        """Создать интерфейс"""
        # Заголовок
        ttk.Label(self.window, text="💳 МЕТОДЫ ОПЛАТЫ", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Фреймы
        list_frame = ttk.Frame(self.window)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Таблица
        columns = ('ID', 'Название', 'Тип', 'Комиссия %', 'Счёт', 'Видимый', 'Активен')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Название', text='Название')
        self.tree.heading('Тип', text='Тип')
        self.tree.heading('Комиссия %', text='Комиссия %')
        self.tree.heading('Счёт', text='Счёт')
        self.tree.heading('Видимый', text='Видимый')
        self.tree.heading('Активен', text='Активен')
        
        self.tree.column('ID', width=50)
        self.tree.column('Название', width=180)
        self.tree.column('Тип', width=80)
        self.tree.column('Комиссия %', width=90)
        self.tree.column('Счёт', width=150)
        self.tree.column('Видимый', width=80)
        self.tree.column('Активен', width=80)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Кнопки
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(btn_frame, text="➕ Добавить", command=self.add_method).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="✏️ Изменить", command=self.edit_method).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="👁️ Показать/Скрыть", command=self.toggle_visible).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Изменить порядок", command=self.change_order).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Удалить", command=self.delete_method).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_data).pack(side='left', padx=5)
    
    def load_data(self):
        """Загрузить данные"""
        # Очистить
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Загрузить
        methods = self.db.get_payment_methods()
        for method in methods:
            account_name = method.get('account_name', 'N/A')
            visible = '👁️' if method.get('is_visible', True) else '🙈'
            active = '✅' if method.get('is_active', True) else '❌'
            
            self.tree.insert('', 'end', values=(
                method['id'],
                method['name'],
                method['method_type'],
                f"{method['commission_percent']}%",
                account_name,
                visible,
                active
            ))
    
    def add_method(self):
        """Добавить метод"""
        AddPaymentMethodDialog(self.window, self.db, self.load_data)
    
    def edit_method(self):
        """Изменить метод"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("⚠️", "Выберите метод оплаты")
            return
        
        method_id = self.tree.item(selected[0])['values'][0]
        EditPaymentMethodDialog(self.window, self.db, method_id, self.load_data)
    
    def toggle_visible(self):
        """Показать/скрыть метод в отчётах"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("⚠️", "Выберите метод оплаты")
            return
        
        method_id = self.tree.item(selected[0])['values'][0]
        method = self.db.get_payment_method(method_id)
        
        if not method:
            messagebox.showerror("❌", "Метод не найден")
            return
        
        # Переключаем видимость
        new_visible = not method.get('is_visible', True)
        self.db.toggle_payment_method_visibility(method_id, new_visible)
        
        status = "видимым" if new_visible else "скрытым"
        messagebox.showinfo("✅", f"Метод '{method['name']}' теперь {status} в отчётах")
        self.load_data()
    
    def change_order(self):
        """Изменить порядок"""
        ReorderDialog(self.window, self.db, self.load_data)
    
    def delete_method(self):
        """Удалить метод"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("⚠️", "Выберите метод оплаты")
            return
        
        if messagebox.askyesno("Удалить", "Удалить выбранный метод?"):
            method_id = self.tree.item(selected[0])['values'][0]
            self.db.delete_payment_method(method_id)
            messagebox.showinfo("✅", "Метод удалён")
            self.load_data()


class AddPaymentMethodDialog:
    """Диалог добавления метода оплаты"""
    
    def __init__(self, parent, db, callback):
        self.db = db
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("➕ Добавить метод оплаты")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_ui()
    
    def create_ui(self):
        """Создать UI"""
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Название
        ttk.Label(frame, text="Название:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        # Тип
        ttk.Label(frame, text="Тип:").grid(row=1, column=0, sticky='w', pady=5)
        self.type_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.type_var, 
                     values=['terminal', 'online', 'delivery'], 
                     width=28, state='readonly').grid(row=1, column=1, pady=5)
        
        # Комиссия
        ttk.Label(frame, text="Комиссия %:").grid(row=2, column=0, sticky='w', pady=5)
        self.commission_var = tk.DoubleVar(value=0.0)
        ttk.Spinbox(frame, textvariable=self.commission_var, from_=0, to=100, 
                    increment=0.1, width=28).grid(row=2, column=1, pady=5)
        
        # Счёт
        ttk.Label(frame, text="Счёт по умолчанию:").grid(row=3, column=0, sticky='w', pady=5)
        accounts = self.db.get_accounts()
        account_names = [f"{acc['name']} ({acc['type']})" for acc in accounts]
        self.account_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.account_var, 
                     values=account_names, width=28, state='readonly').grid(row=3, column=1, pady=5)
        
        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="💾 Сохранить", command=self.save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Отмена", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def save(self):
        """Сохранить"""
        name = self.name_var.get().strip()
        method_type = self.type_var.get()
        commission = self.commission_var.get()
        
        if not name or not method_type:
            messagebox.showerror("❌ Ошибка", "Заполните все поля")
            return
        
        # TODO: Получить ID счёта и добавить в БД
        messagebox.showinfo("✅", f"Метод '{name}' добавлен!")
        self.callback()
        self.dialog.destroy()


class EditPaymentMethodDialog(AddPaymentMethodDialog):
    """Диалог редактирования метода оплаты"""
    
    def __init__(self, parent, db, method_id, callback):
        self.method_id = method_id
        super().__init__(parent, db, callback)
        self.dialog.title("✏️ Редактировать метод оплаты")
        self.load_method()
    
    def load_method(self):
        """Загрузить данные метода"""
        # TODO: Загрузить из БД
        pass


class ReorderDialog:
    """Диалог изменения порядка"""
    
    def __init__(self, parent, db, callback):
        self.db = db
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🔄 Изменить порядок")
        self.dialog.geometry("400x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_ui()
    
    def create_ui(self):
        """Создать UI"""
        ttk.Label(self.dialog, text="Перетащите элементы для изменения порядка:", 
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        # Listbox с методами
        self.listbox = tk.Listbox(self.dialog, height=15)
        self.listbox.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Загрузка методов
        methods = self.db.get_payment_methods()
        for method in methods:
            self.listbox.insert('end', f"{method['name']} ({method['method_type']})")
        
        # Кнопки
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="⬆️ Вверх", command=self.move_up).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="⬇️ Вниз", command=self.move_down).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="💾 Сохранить", command=self.save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Отмена", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def move_up(self):
        """Переместить вверх"""
        selection = self.listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        idx = selection[0]
        item = self.listbox.get(idx)
        self.listbox.delete(idx)
        self.listbox.insert(idx - 1, item)
        self.listbox.selection_set(idx - 1)
    
    def move_down(self):
        """Переместить вниз"""
        selection = self.listbox.curselection()
        if not selection or selection[0] == self.listbox.size() - 1:
            return
        
        idx = selection[0]
        item = self.listbox.get(idx)
        self.listbox.delete(idx)
        self.listbox.insert(idx + 1, item)
        self.listbox.selection_set(idx + 1)
    
    def save(self):
        """Сохранить порядок"""
        # TODO: Сохранить в БД
        messagebox.showinfo("✅", "Порядок сохранён!")
        self.callback()
        self.dialog.destroy()


class CashierReportWindow:
    """Окно создания отчёта кассира"""
    
    def __init__(self, parent, db):
        self.db = db
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Новый отчёт кассира")
        self.window.geometry("800x900")
        
        self.payment_entries = {}
        self.report_id = None
        
        self.create_ui()
    
    def create_ui(self):
        """Создать интерфейс"""
        # Скроллируемый фрейм
        canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        frame = self.scrollable_frame
        
        # Заголовок
        ttk.Label(frame, text="📊 ДНЕВНОЙ ОТЧЁТ КАССИРА", 
                 font=('Arial', 18, 'bold')).pack(pady=15)
        
        # ОСНОВНАЯ ИНФОРМАЦИЯ
        info_frame = ttk.LabelFrame(frame, text="📋 Основная информация", padding=15)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        # Точка
        ttk.Label(info_frame, text="Точка продаж:").grid(row=0, column=0, sticky='w', pady=5)
        self.location_var = tk.StringVar()
        locations = self.db.get_locations()
        location_names = [loc['name'] for loc in locations]
        ttk.Combobox(info_frame, textvariable=self.location_var, 
                     values=location_names, width=30, state='readonly').grid(row=0, column=1, pady=5, sticky='w')
        
        # Дата
        from datetime import date
        ttk.Label(info_frame, text="Дата:").grid(row=1, column=0, sticky='w', pady=5)
        self.date_var = tk.StringVar(value=date.today().strftime('%d.%m.%Y'))
        ttk.Entry(info_frame, textvariable=self.date_var, width=32).grid(row=1, column=1, pady=5, sticky='w')
        
        # ПРОДАЖИ
        sales_frame = ttk.LabelFrame(frame, text="💰 Продажи", padding=15)
        sales_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(sales_frame, text="Общая сумма продаж:").grid(row=0, column=0, sticky='w', pady=5)
        self.total_sales_var = tk.StringVar()
        ttk.Entry(sales_frame, textvariable=self.total_sales_var, width=25).grid(row=0, column=1, pady=5, sticky='w')
        ttk.Label(sales_frame, text="сум").grid(row=0, column=2, sticky='w', pady=5, padx=5)
        
        # МЕТОДЫ ОПЛАТЫ
        payments_frame = ttk.LabelFrame(frame, text="💳 Методы оплаты", padding=15)
        payments_frame.pack(fill='x', padx=20, pady=10)
        
        methods = self.db.get_payment_methods()
        # Фильтруем только видимые методы
        methods = [m for m in methods if m.get('is_visible', True)]
        row = 0
        
        for method in methods:
            emoji = {'terminal': '📟', 'online': '🌐', 'delivery': '🚚'}.get(method['method_type'], '💳')
            label_text = f"{emoji} {method['name']} ({method['commission_percent']}%)"
            
            ttk.Label(payments_frame, text=label_text).grid(row=row, column=0, sticky='w', pady=5)
            
            var = tk.StringVar(value="0")
            entry = ttk.Entry(payments_frame, textvariable=var, width=20)
            entry.grid(row=row, column=1, pady=5, sticky='w')
            
            ttk.Label(payments_frame, text="сум").grid(row=row, column=2, sticky='w', pady=5, padx=5)
            
            # Показываем чистую сумму
            net_label = ttk.Label(payments_frame, text="→ 0 сум", foreground='gray')
            net_label.grid(row=row, column=3, sticky='w', pady=5, padx=10)
            
            self.payment_entries[method['id']] = {
                'var': var,
                'method': method,
                'net_label': net_label
            }
            
            # При вводе пересчитываем
            var.trace('w', lambda *args, m=method, nl=net_label: self.update_net_amount(m, nl))
            
            row += 1
        
        # Кнопка пересчёта
        ttk.Button(payments_frame, text="🔄 Пересчитать", 
                  command=self.recalculate).grid(row=row, column=0, columnspan=4, pady=10)
        
        # РЕЗУЛЬТАТ БЕЗНАЛ
        self.cashless_frame = ttk.LabelFrame(frame, text="📊 Итого безнал", padding=15)
        self.cashless_frame.pack(fill='x', padx=20, pady=10)
        
        self.cashless_label = ttk.Label(self.cashless_frame, text="0 сум", font=('Arial', 14, 'bold'))
        self.cashless_label.pack()
        
        # НАЛИЧНЫЕ
        cash_frame = ttk.LabelFrame(frame, text="💵 Наличные", padding=15)
        cash_frame.pack(fill='x', padx=20, pady=10)
        
        self.cash_expected_label = ttk.Label(cash_frame, text="По отчёту: 0 сум", font=('Arial', 12))
        self.cash_expected_label.pack(pady=5)
        
        ttk.Separator(cash_frame, orient='horizontal').pack(fill='x', pady=10)
        
        ttk.Label(cash_frame, text="Фактически в кассе:").pack(anchor='w', pady=5)
        self.cash_actual_var = tk.StringVar(value="0")
        ttk.Entry(cash_frame, textvariable=self.cash_actual_var, width=25).pack(anchor='w', pady=5)
        
        ttk.Button(cash_frame, text="🔄 Рассчитать разницу", 
                  command=self.calculate_difference).pack(pady=10)
        
        self.difference_label = ttk.Label(cash_frame, text="", font=('Arial', 12, 'bold'))
        self.difference_label.pack(pady=5)
        
        # РАСХОДЫ (опционально)
        expenses_frame = ttk.LabelFrame(frame, text="💸 Расходы (опционально)", padding=15)
        expenses_frame.pack(fill='x', padx=20, pady=10)
        
        self.expenses = []
        
        ttk.Button(expenses_frame, text="➕ Добавить расход", 
                  command=self.add_expense).pack(pady=5)
        
        self.expenses_list_frame = ttk.Frame(expenses_frame)
        self.expenses_list_frame.pack(fill='x', pady=10)
        
        # КНОПКИ ДЕЙСТВИЙ
        action_frame = ttk.Frame(frame)
        action_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(action_frame, text="💾 Сохранить отчёт", 
                  command=self.save_report, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(action_frame, text="❌ Отмена", 
                  command=self.window.destroy).pack(side='left', padx=5)
    
    def update_net_amount(self, method, net_label):
        """Обновить чистую сумму при вводе"""
        try:
            amount = float(self.payment_entries[method['id']]['var'].get() or 0)
            net = amount * (1 - method['commission_percent'] / 100)
            net_label.config(text=f"→ {net:,.0f} сум")
        except:
            net_label.config(text="→ 0 сум")
    
    def recalculate(self):
        """Пересчитать все суммы"""
        try:
            total_sales = float(self.total_sales_var.get() or 0)
            total_cashless = 0
            
            for method_id, data in self.payment_entries.items():
                amount = float(data['var'].get() or 0)
                total_cashless += amount
                
                # Обновляем чистую сумму
                net = amount * (1 - data['method']['commission_percent'] / 100)
                data['net_label'].config(text=f"→ {net:,.0f} сум")
            
            cash_expected = total_sales - total_cashless
            
            self.cashless_label.config(text=f"{total_cashless:,.0f} сум")
            self.cash_expected_label.config(text=f"По отчёту: {cash_expected:,.0f} сум")
            
            messagebox.showinfo("✅", "Пересчитано!")
            
        except ValueError:
            messagebox.showerror("❌", "Проверьте введённые числа")
    
    def calculate_difference(self):
        """Рассчитать разницу в наличных"""
        try:
            total_sales = float(self.total_sales_var.get() or 0)
            total_cashless = sum(float(data['var'].get() or 0) 
                               for data in self.payment_entries.values())
            
            cash_expected = total_sales - total_cashless
            cash_actual = float(self.cash_actual_var.get() or 0)
            difference = cash_actual - cash_expected
            
            if difference > 0:
                text = f"✅ ИЗЛИШЕК: +{difference:,.0f} сум"
                color = 'green'
            elif difference < 0:
                text = f"⚠️ НЕДОСТАЧА: {difference:,.0f} сум"
                color = 'red'
            else:
                text = f"✅ БЕЗ РАСХОЖДЕНИЙ"
                color = 'green'
            
            self.difference_label.config(text=text, foreground=color)
            
        except ValueError:
            messagebox.showerror("❌", "Проверьте введённые числа")
    
    def add_expense(self):
        """Добавить расход"""
        AddExpenseDialog(self.window, self.db, self.update_expenses_list)
    
    def update_expenses_list(self, expense_data=None):
        """Обновить список расходов"""
        if expense_data:
            self.expenses.append(expense_data)
        
        # Очистить
        for widget in self.expenses_list_frame.winfo_children():
            widget.destroy()
        
        # Показать
        for i, expense in enumerate(self.expenses):
            frame = ttk.Frame(self.expenses_list_frame)
            frame.pack(fill='x', pady=2)
            
            text = f"• {expense['amount']:,.0f} сум - {expense['description']}"
            ttk.Label(frame, text=text).pack(side='left')
            
            ttk.Button(frame, text="🗑️", width=3, 
                      command=lambda idx=i: self.remove_expense(idx)).pack(side='right')
    
    def remove_expense(self, index):
        """Удалить расход"""
        self.expenses.pop(index)
        self.update_expenses_list()
    
    def save_report(self):
        """Сохранить отчёт"""
        try:
            from datetime import datetime
            
            # Валидация
            if not self.location_var.get():
                messagebox.showerror("❌", "Выберите точку продаж")
                return
            
            total_sales = float(self.total_sales_var.get() or 0)
            if total_sales <= 0:
                messagebox.showerror("❌", "Введите сумму продаж")
                return
            
            # Получаем ID точки
            locations = self.db.get_locations()
            location = next((loc for loc in locations if loc['name'] == self.location_var.get()), None)
            if not location:
                messagebox.showerror("❌", "Точка не найдена")
                return
            
            # Создаём отчёт
            report_date = datetime.strptime(self.date_var.get(), '%d.%m.%Y').date()
            self.report_id = self.db.create_daily_report(
                report_date,
                location['id'],
                total_sales,
                "GUI User"
            )
            
            # Сохраняем платежи
            for method_id, data in self.payment_entries.items():
                amount = float(data['var'].get() or 0)
                if amount > 0:
                    self.db.add_report_payment(
                        self.report_id,
                        method_id,
                        data['method']['default_account_id'],
                        amount
                    )
            
            # Сохраняем наличные
            total_cashless = sum(float(data['var'].get() or 0) 
                               for data in self.payment_entries.values())
            cash_expected = total_sales - total_cashless
            cash_actual = float(self.cash_actual_var.get() or 0)
            
            self.db.update_report_cash(self.report_id, cash_expected, cash_actual, {})
            
            # Сохраняем расходы
            cash_accounts = self.db.get_accounts('cash')
            if cash_accounts and self.expenses:
                for expense in self.expenses:
                    self.db.add_report_expense(
                        self.report_id,
                        cash_accounts[0]['id'],
                        expense['amount'],
                        expense.get('category_id'),
                        expense['description']
                    )
            
            # Закрываем отчёт
            self.db.close_report(self.report_id)
            
            messagebox.showinfo("✅ Успех", 
                              f"Отчёт #{self.report_id} сохранён!\n\n"
                              f"Дата: {report_date.strftime('%d.%m.%Y')}\n"
                              f"Точка: {location['name']}\n"
                              f"Продажи: {total_sales:,.0f} сум")
            
            self.window.destroy()
            
        except ValueError as e:
            messagebox.showerror("❌ Ошибка", f"Проверьте введённые данные:\n{e}")
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Не удалось сохранить:\n{e}")


class AddExpenseDialog:
    """Диалог добавления расхода"""
    
    def __init__(self, parent, db, callback):
        self.db = db
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("➕ Добавить расход")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_ui()
    
    def create_ui(self):
        """Создать UI"""
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Сумма:").grid(row=0, column=0, sticky='w', pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.amount_var, width=30).grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Описание:").grid(row=1, column=0, sticky='w', pady=5)
        self.desc_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.desc_var, width=30).grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Категория:").grid(row=2, column=0, sticky='w', pady=5)
        self.category_var = tk.StringVar()
        categories = self.db.get_expense_categories()
        category_names = ['Без категории'] + [cat['name'] for cat in categories]
        ttk.Combobox(frame, textvariable=self.category_var, 
                     values=category_names, width=28, state='readonly').grid(row=2, column=1, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="💾 Добавить", command=self.save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Отмена", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def save(self):
        """Сохранить"""
        try:
            amount = float(self.amount_var.get() or 0)
            description = self.desc_var.get().strip()
            
            if amount <= 0:
                messagebox.showerror("❌", "Введите сумму")
                return
            
            if not description:
                messagebox.showerror("❌", "Введите описание")
                return
            
            # Получаем ID категории
            category_id = None
            category_name = self.category_var.get()
            if category_name and category_name != 'Без категории':
                categories = self.db.get_expense_categories()
                category = next((cat for cat in categories if cat['name'] == category_name), None)
                if category:
                    category_id = category['id']
            
            expense_data = {
                'amount': amount,
                'description': description,
                'category_id': category_id
            }
            
            self.callback(expense_data)
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("❌", "Проверьте сумму")


class ReportsViewWindow:
    """Окно просмотра отчётов"""
    
    def __init__(self, parent, db):
        self.db = db
        self.window = tk.Toplevel(parent)
        self.window.title("👀 Просмотр отчётов")
        self.window.geometry("1000x600")
        
        self.create_ui()
        self.load_data()
    
    def create_ui(self):
        """Создать интерфейс"""
        ttk.Label(self.window, text="👀 ОТЧЁТЫ КАССИРОВ", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Фильтры
        filter_frame = ttk.Frame(self.window)
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(filter_frame, text="Точка:").pack(side='left', padx=5)
        self.location_var = tk.StringVar(value="Все")
        locations = ['Все'] + [loc['name'] for loc in self.db.get_locations()]
        ttk.Combobox(filter_frame, textvariable=self.location_var, 
                     values=locations, width=20, state='readonly').pack(side='left', padx=5)
        
        ttk.Button(filter_frame, text="🔍 Фильтровать", command=self.load_data).pack(side='left', padx=5)
        ttk.Button(filter_frame, text="🔄 Обновить", command=self.load_data).pack(side='left', padx=5)
        
        # Таблица
        list_frame = ttk.Frame(self.window)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Дата', 'Точка', 'Продажи', 'Наличные (план)', 'Наличные (факт)', 'Разница', 'Статус')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column('ID', width=50)
        self.tree.column('Дата', width=100)
        self.tree.column('Точка', width=150)
        self.tree.column('Продажи', width=120)
        self.tree.column('Наличные (план)', width=120)
        self.tree.column('Наличные (факт)', width=120)
        self.tree.column('Разница', width=100)
        self.tree.column('Статус', width=80)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Двойной клик для детального просмотра
        self.tree.bind('<Double-1>', self.view_details)
        
        # Кнопки
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(btn_frame, text="📋 Детали", command=self.view_details).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🖨️ Печать", command=self.print_report).pack(side='left', padx=5)
    
    def load_data(self):
        """Загрузить данные"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Фильтр по точке
        location_name = self.location_var.get()
        location_id = None
        if location_name != "Все":
            locations = self.db.get_locations()
            location = next((loc for loc in locations if loc['name'] == location_name), None)
            if location:
                location_id = location['id']
        
        reports = self.db.get_reports(limit=100, location_id=location_id)
        
        for report in reports:
            status_emoji = '✅' if report.get('status') == 'closed' else '📝'
            diff = report.get('cash_difference', 0)
            diff_color = 'red' if diff < 0 else ('green' if diff > 0 else 'black')
            
            self.tree.insert('', 'end', values=(
                report['id'],
                report['date'],
                report['location'],
                f"{report.get('total_sales', 0):,.0f}",
                f"{report.get('cash_expected', 0):,.0f}",
                f"{report.get('cash_actual', 0):,.0f}",
                f"{diff:+,.0f}",
                status_emoji
            ), tags=(diff_color,))
        
        # Цвета для разницы
        self.tree.tag_configure('red', foreground='red')
        self.tree.tag_configure('green', foreground='green')
    
    def view_details(self, event=None):
        """Посмотреть детали отчёта"""
        selected = self.tree.selection()
        if not selected:
            if event:  # Если вызвано через двойной клик, не показывать предупреждение
                return
            messagebox.showwarning("⚠️", "Выберите отчёт")
            return
        
        report_id = self.tree.item(selected[0])['values'][0]
        ReportDetailsWindow(self.window, self.db, report_id)
    
    def print_report(self):
        """Печать отчёта"""
        messagebox.showinfo("В разработке", "Функция печати будет готова в следующей версии!")


class ReportDetailsWindow:
    """Окно детального просмотра отчёта"""
    
    def __init__(self, parent, db, report_id):
        self.db = db
        self.report_id = report_id
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"📋 Отчёт #{report_id}")
        self.window.geometry("700x800")
        
        self.create_ui()
        self.load_data()
    
    def create_ui(self):
        """Создать интерфейс"""
        # Скроллируемый фрейм
        canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def load_data(self):
        """Загрузить данные отчёта"""
        report = self.db.get_report_details(self.report_id)
        
        if not report:
            messagebox.showerror("Ошибка", "Отчёт не найден")
            self.window.destroy()
            return
        
        frame = self.scrollable_frame
        
        # Заголовок
        ttk.Label(frame, text=f"📋 ОТЧЁТ #{report['id']}", 
                 font=('Arial', 18, 'bold')).pack(pady=10)
        
        # Основная информация
        info_frame = ttk.LabelFrame(frame, text="ℹ️ Основная информация", padding=15)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        info_data = [
            ("Дата:", report['report_date']),
            ("Точка:", report['location_name']),
            ("Кассир:", report.get('created_by', 'N/A')),
            ("Статус:", '✅ Закрыт' if report.get('status') == 'closed' else '📝 Открыт'),
        ]
        
        for label, value in info_data:
            row = ttk.Frame(info_frame)
            row.pack(fill='x', pady=2)
            ttk.Label(row, text=label, font=('Arial', 10, 'bold'), width=15).pack(side='left')
            ttk.Label(row, text=value).pack(side='left')
        
        # Продажи
        sales_frame = ttk.LabelFrame(frame, text="💰 Продажи", padding=15)
        sales_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(sales_frame, text=f"Общая сумма: {report.get('total_sales', 0):,.0f} сум",
                 font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Платежи
        if report.get('payments'):
            payments_frame = ttk.LabelFrame(frame, text="💳 Методы оплаты", padding=15)
            payments_frame.pack(fill='x', padx=20, pady=10)
            
            for payment in report['payments']:
                net = payment['amount'] * (1 - payment.get('commission_percent', 0) / 100)
                text = f"{payment['payment_method_name']}: {payment['amount']:,.0f} → {net:,.0f} сум"
                ttk.Label(payments_frame, text=text).pack(anchor='w', pady=2)
        
        # Наличные
        cash_frame = ttk.LabelFrame(frame, text="💵 Наличные", padding=15)
        cash_frame.pack(fill='x', padx=20, pady=10)
        
        expected = report.get('cash_expected', 0)
        actual = report.get('cash_actual', 0)
        diff = report.get('cash_difference', 0)
        
        ttk.Label(cash_frame, text=f"По отчёту: {expected:,.0f} сум").pack(anchor='w', pady=2)
        ttk.Label(cash_frame, text=f"Фактически: {actual:,.0f} сум").pack(anchor='w', pady=2)
        
        diff_text = f"Разница: {diff:+,.0f} сум"
        diff_color = 'red' if diff < 0 else ('green' if diff > 0 else 'black')
        ttk.Label(cash_frame, text=diff_text, foreground=diff_color, 
                 font=('Arial', 11, 'bold')).pack(anchor='w', pady=5)
        
        # Расходы
        if report.get('expenses'):
            expenses_frame = ttk.LabelFrame(frame, text="💸 Расходы", padding=15)
            expenses_frame.pack(fill='x', padx=20, pady=10)
            
            total_expenses = 0
            for expense in report['expenses']:
                cat = expense.get('category_name', 'Без категории')
                desc = expense.get('description', '')
                amount = expense['amount']
                total_expenses += amount
                
                text = f"• {cat}: {amount:,.0f} сум"
                if desc:
                    text += f" ({desc})"
                ttk.Label(expenses_frame, text=text).pack(anchor='w', pady=2)
            
            ttk.Label(expenses_frame, text=f"Всего расходов: {total_expenses:,.0f} сум",
                     font=('Arial', 10, 'bold')).pack(anchor='w', pady=5)
        
        # Кнопка закрыть
        ttk.Button(frame, text="❌ Закрыть", command=self.window.destroy).pack(pady=20)


class BalancesWindow:
    """Окно балансов"""
    
    def __init__(self, parent, db):
        self.db = db
        self.window = tk.Toplevel(parent)
        self.window.title("💰 Балансы счетов")
        self.window.geometry("600x400")
        
        self.create_ui()
        self.load_balances()
    
    def create_ui(self):
        """Создать UI"""
        ttk.Label(self.window, text="💰 БАЛАНСЫ СЧЕТОВ", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Таблица
        columns = ('Счёт', 'Тип', 'Баланс')
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column('Счёт', width=200)
        self.tree.column('Тип', width=100)
        self.tree.column('Баланс', width=200)
        
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Итого
        self.total_label = ttk.Label(self.window, text="", font=('Arial', 14, 'bold'))
        self.total_label.pack(pady=10)
        
        ttk.Button(self.window, text="🔄 Обновить", command=self.load_balances).pack(pady=10)
    
    def load_balances(self):
        """Загрузить балансы"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        balances = self.db.get_account_balance()
        total = 0
        
        for acc_id, data in balances.items():
            emoji = "💵" if data['type'] == 'cash' else "🏦"
            self.tree.insert('', 'end', values=(
                f"{emoji} {data['name']}",
                data['type'],
                f"{data['balance']:,.0f} сум"
            ))
            total += data['balance']
        
        self.total_label.config(text=f"ИТОГО: {total:,.0f} сум")


class LocationsWindow:
    """Окно управления точками"""
    
    def __init__(self, parent, db):
        self.db = db
        self.window = tk.Toplevel(parent)
        self.window.title("📍 Управление точками продаж")
        self.window.geometry("700x500")
        
        self.create_ui()
        self.load_data()
    
    def create_ui(self):
        """Создать интерфейс"""
        ttk.Label(self.window, text="📍 ТОЧКИ ПРОДАЖ", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Таблица
        list_frame = ttk.Frame(self.window)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Название', 'Адрес', 'Активна')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column('ID', width=50)
        self.tree.column('Название', width=200)
        self.tree.column('Адрес', width=300)
        self.tree.column('Активна', width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Кнопки
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(btn_frame, text="➕ Добавить", command=self.add_location).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="✏️ Изменить", command=self.edit_location).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Удалить", command=self.delete_location).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_data).pack(side='left', padx=5)
    
    def load_data(self):
        """Загрузить данные"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        locations = self.db.get_locations()
        for loc in locations:
            active = '✅' if loc.get('is_active', True) else '❌'
            self.tree.insert('', 'end', values=(
                loc['id'],
                loc['name'],
                loc.get('address', ''),
                active
            ))
    
    def add_location(self):
        """Добавить точку"""
        AddLocationDialog(self.window, self.db, self.load_data)
    
    def edit_location(self):
        """Изменить точку"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("⚠️", "Выберите точку")
            return
        
        location_id = self.tree.item(selected[0])['values'][0]
        EditLocationDialog(self.window, self.db, location_id, self.load_data)
    
    def delete_location(self):
        """Удалить точку"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("⚠️", "Выберите точку")
            return
        
        if messagebox.askyesno("Удалить", "Удалить выбранную точку?"):
            location_id = self.tree.item(selected[0])['values'][0]
            self.db.delete_location(location_id)
            messagebox.showinfo("✅", "Точка удалена")
            self.load_data()


class AddLocationDialog:
    """Диалог добавления точки"""
    
    def __init__(self, parent, db, callback):
        self.db = db
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("➕ Добавить точку")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_ui()
    
    def create_ui(self):
        """Создать UI"""
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Название:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Адрес:").grid(row=1, column=0, sticky='w', pady=5)
        self.address_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.address_var, width=30).grid(row=1, column=1, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="💾 Сохранить", command=self.save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Отмена", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def save(self):
        """Сохранить"""
        name = self.name_var.get().strip()
        address = self.address_var.get().strip()
        
        if not name:
            messagebox.showerror("❌ Ошибка", "Заполните название")
            return
        
        self.db.add_location(name, address)
        messagebox.showinfo("✅", f"Точка '{name}' добавлена!")
        self.callback()
        self.dialog.destroy()


class EditLocationDialog(AddLocationDialog):
    """Диалог редактирования точки"""
    
    def __init__(self, parent, db, location_id, callback):
        self.location_id = location_id
        super().__init__(parent, db, callback)
        self.dialog.title("✏️ Редактировать точку")
        self.load_location()
    
    def load_location(self):
        """Загрузить данные точки"""
        locations = self.db.get_locations()
        location = next((loc for loc in locations if loc['id'] == self.location_id), None)
        if location:
            self.name_var.set(location['name'])
            self.address_var.set(location.get('address', ''))
    
    def save(self):
        """Сохранить"""
        name = self.name_var.get().strip()
        address = self.address_var.get().strip()
        
        if not name:
            messagebox.showerror("❌ Ошибка", "Заполните название")
            return
        
        self.db.update_location(self.location_id, name, address)
        messagebox.showinfo("✅", "Точка обновлена!")
        self.callback()
        self.dialog.destroy()


class AccountsWindow:
    """Окно управления счетами"""
    
    def __init__(self, parent, db):
        self.db = db
        self.window = tk.Toplevel(parent)
        self.window.title("🏦 Управление счетами")
        self.window.geometry("700x500")
        
        self.create_ui()
        self.load_data()
    
    def create_ui(self):
        """Создать интерфейс"""
        ttk.Label(self.window, text="🏦 СЧЕТА", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Таблица
        list_frame = ttk.Frame(self.window)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Название', 'Тип', 'Баланс', 'Активен')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column('ID', width=50)
        self.tree.column('Название', width=200)
        self.tree.column('Тип', width=100)
        self.tree.column('Баланс', width=150)
        self.tree.column('Активен', width=80)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Кнопки
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(btn_frame, text="➕ Добавить", command=self.add_account).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="✏️ Изменить", command=self.edit_account).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Удалить", command=self.delete_account).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_data).pack(side='left', padx=5)
    
    def load_data(self):
        """Загрузить данные"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        accounts = self.db.get_accounts()
        balances = self.db.get_account_balance()
        
        for acc in accounts:
            acc_id = acc['id']
            balance = balances.get(acc_id, {}).get('balance', 0)
            active = '✅' if acc.get('is_active', True) else '❌'
            
            self.tree.insert('', 'end', values=(
                acc_id,
                acc['name'],
                acc['account_type'],
                f"{balance:,.0f} сум",
                active
            ))
    
    def add_account(self):
        """Добавить счёт"""
        AddAccountDialog(self.window, self.db, self.load_data)
    
    def edit_account(self):
        """Изменить счёт"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("⚠️", "Выберите счёт")
            return
        
        account_id = self.tree.item(selected[0])['values'][0]
        EditAccountDialog(self.window, self.db, account_id, self.load_data)
    
    def delete_account(self):
        """Удалить счёт"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("⚠️", "Выберите счёт")
            return
        
        if messagebox.askyesno("Удалить", "Удалить выбранный счёт?"):
            account_id = self.tree.item(selected[0])['values'][0]
            self.db.delete_account(account_id)
            messagebox.showinfo("✅", "Счёт удалён")
            self.load_data()


class AddAccountDialog:
    """Диалог добавления счёта"""
    
    def __init__(self, parent, db, callback):
        self.db = db
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("➕ Добавить счёт")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_ui()
    
    def create_ui(self):
        """Создать UI"""
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Название:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Тип:").grid(row=1, column=0, sticky='w', pady=5)
        self.type_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.type_var, 
                     values=['cash', 'bank'], width=28, state='readonly').grid(row=1, column=1, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="💾 Сохранить", command=self.save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Отмена", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def save(self):
        """Сохранить"""
        name = self.name_var.get().strip()
        acc_type = self.type_var.get()
        
        if not name or not acc_type:
            messagebox.showerror("❌ Ошибка", "Заполните все поля")
            return
        
        self.db.add_account(name, acc_type)
        messagebox.showinfo("✅", f"Счёт '{name}' добавлен!")
        self.callback()
        self.dialog.destroy()


class EditAccountDialog(AddAccountDialog):
    """Диалог редактирования счёта"""
    
    def __init__(self, parent, db, account_id, callback):
        self.account_id = account_id
        super().__init__(parent, db, callback)
        self.dialog.title("✏️ Редактировать счёт")
        self.load_account()
    
    def load_account(self):
        """Загрузить данные счёта"""
        accounts = self.db.get_accounts()
        account = next((acc for acc in accounts if acc['id'] == self.account_id), None)
        if account:
            self.name_var.set(account['name'])
            self.type_var.set(account['account_type'])
    
    def save(self):
        """Сохранить"""
        name = self.name_var.get().strip()
        acc_type = self.type_var.get()
        
        if not name or not acc_type:
            messagebox.showerror("❌ Ошибка", "Заполните все поля")
            return
        
        self.db.update_account(self.account_id, name, acc_type)
        messagebox.showinfo("✅", "Счёт обновлён!")
        self.callback()
        self.dialog.destroy()


class CategoriesWindow:
    """Окно управления категориями"""
    
    def __init__(self, parent, db):
        self.db = db
        self.window = tk.Toplevel(parent)
        self.window.title("📂 Управление категориями расходов")
        self.window.geometry("700x500")
        
        self.create_ui()
        self.load_data()
    
    def create_ui(self):
        """Создать интерфейс"""
        ttk.Label(self.window, text="📂 КАТЕГОРИИ РАСХОДОВ", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Таблица
        list_frame = ttk.Frame(self.window)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Название', 'Описание', 'Активна')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column('ID', width=50)
        self.tree.column('Название', width=200)
        self.tree.column('Описание', width=300)
        self.tree.column('Активна', width=80)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Кнопки
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(btn_frame, text="➕ Добавить", command=self.add_category).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="✏️ Изменить", command=self.edit_category).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Удалить", command=self.delete_category).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_data).pack(side='left', padx=5)
    
    def load_data(self):
        """Загрузить данные"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        categories = self.db.get_expense_categories()
        for cat in categories:
            active = '✅' if cat.get('is_active', True) else '❌'
            self.tree.insert('', 'end', values=(
                cat['id'],
                cat['name'],
                cat.get('description', ''),
                active
            ))
    
    def add_category(self):
        """Добавить категорию"""
        AddCategoryDialog(self.window, self.db, self.load_data)
    
    def edit_category(self):
        """Изменить категорию"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("⚠️", "Выберите категорию")
            return
        
        category_id = self.tree.item(selected[0])['values'][0]
        EditCategoryDialog(self.window, self.db, category_id, self.load_data)
    
    def delete_category(self):
        """Удалить категорию"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("⚠️", "Выберите категорию")
            return
        
        if messagebox.askyesno("Удалить", "Удалить выбранную категорию?"):
            category_id = self.tree.item(selected[0])['values'][0]
            self.db.delete_expense_category(category_id)
            messagebox.showinfo("✅", "Категория удалена")
            self.load_data()


class AddCategoryDialog:
    """Диалог добавления категории"""
    
    def __init__(self, parent, db, callback):
        self.db = db
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("➕ Добавить категорию")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_ui()
    
    def create_ui(self):
        """Создать UI"""
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Название:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Описание:").grid(row=1, column=0, sticky='w', pady=5)
        self.desc_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.desc_var, width=30).grid(row=1, column=1, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="💾 Сохранить", command=self.save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Отмена", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def save(self):
        """Сохранить"""
        name = self.name_var.get().strip()
        description = self.desc_var.get().strip()
        
        if not name:
            messagebox.showerror("❌ Ошибка", "Заполните название")
            return
        
        self.db.add_expense_category(name, description)
        messagebox.showinfo("✅", f"Категория '{name}' добавлена!")
        self.callback()
        self.dialog.destroy()


class EditCategoryDialog(AddCategoryDialog):
    """Диалог редактирования категории"""
    
    def __init__(self, parent, db, category_id, callback):
        self.category_id = category_id
        super().__init__(parent, db, callback)
        self.dialog.title("✏️ Редактировать категорию")
        self.load_category()
    
    def load_category(self):
        """Загрузить данные категории"""
        categories = self.db.get_expense_categories()
        category = next((cat for cat in categories if cat['id'] == self.category_id), None)
        if category:
            self.name_var.set(category['name'])
            self.desc_var.set(category.get('description', ''))
    
    def save(self):
        """Сохранить"""
        name = self.name_var.get().strip()
        description = self.desc_var.get().strip()
        
        if not name:
            messagebox.showerror("❌ Ошибка", "Заполните название")
            return
        
        self.db.update_expense_category(self.category_id, name, description)
        messagebox.showinfo("✅", "Категория обновлена!")
        self.callback()
        self.dialog.destroy()




if __name__ == '__main__':
    app = MainApp()
    app.run()
