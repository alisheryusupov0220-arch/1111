#!/usr/bin/env python3
"""
Главное приложение с GUI для управления финансовой системой
Визуальное управление логикой, методами оплаты, отчётами
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from settings import config
from database_v5 import FinanceSystemV5

class MainApp:
    """Главное приложение"""
    
    def __init__(self):
        from login_window import select_user

        self.current_user_id, self.current_username = select_user()

        if not self.current_user_id:
            sys.exit(0)

        from permissions_manager import permissions
        self.permissions = permissions

        self.root = tk.Tk()
        self.root.title(f"💰 Air Waffle Finance - {self.current_username}")
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
        
        # Запускаем Poster scheduler
        try:
            from poster_scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            print(f"Poster scheduler error: {e}")
    
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
        ttk.Label(header, text=f"Система управления финансами • Пользователь: {self.current_username}",
                  font=('Arial', 12)).pack()
        
        # Основные кнопки
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Сетка кнопок 2x3
        buttons = [
            ("📅 Timeline", self.show_timeline, 'view_timeline', 0, 0),
            ("📊 Новый отчёт кассира", self.new_cashier_report, 'create_cashier_report', 0, 1),
            ("👀 Просмотр отчётов", self.view_reports, 'view_all_reports', 0, 2),
            ("⚡ Быстрое добавление", self.show_quick_add, 'quick_add_expense', 1, 0),
            ("💰 Балансы счетов", self.view_balances, 'view_balances', 1, 1),
            ("💳 Методы оплаты", self.manage_payments, 'manage_payment_methods', 1, 2),
            ("📍 Точки продаж", self.manage_locations, 'manage_locations', 2, 0),
            ("🏦 Счета", self.manage_accounts, 'manage_accounts', 2, 1),
            ("📂 Категории (старые)", self.manage_categories, 'manage_categories', 2, 2),
            ("🌳 Категории (новые)", self.manage_categories_new, 'manage_categories', 3, 0),
            ("📊 Аналитика", self.show_analytics, 'view_analytics', 3, 1),
            ("💰 Категории приходов", self.manage_income_categories, 'manage_categories', 3, 2),
            ("⚙️ Настройки", self.open_settings, 'system_settings', 4, 0),
            ("📡 Poster API", self.open_poster_settings, 'manage_poster', 4, 1),
            ("🤖 Telegram бот", self.telegram_status, None, 4, 2),
            ("🔐 Права", self.manage_permissions, 'manage_permissions', 5, 0),
        ]
        
        for text, command, permission, row, col in buttons:
            if permission and not self.permissions.has_permission(self.current_user_id, permission):
                continue
            btn = ttk.Button(main_frame, text=text, command=command, width=25)
            btn.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Растягивание
        for i in range(6):
            main_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
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
    
    def show_timeline(self):
        """Показать Timeline"""
        TimelineWindow(self.root, self.db)
    
    def show_quick_add(self):
        """Быстрое добавление расходов/приходов"""
        if not self.permissions.has_any_permission(
            self.current_user_id, ['quick_add_expense', 'quick_add_income']
        ):
            messagebox.showerror("Доступ запрещён", "У вас нет прав для быстрого добавления.")
            return
        QuickAddWindow(self.root, self.db, self.current_user_id)

    def manage_permissions(self):
        """Управление правами пользователей"""
        if not self.permissions.has_permission(self.current_user_id, 'manage_permissions'):
            messagebox.showerror("Доступ запрещён", "У вас нет прав для управления доступом.")
            return
        PermissionsWindow(self.root, self.db, self.current_user_id)
    
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
    
    def manage_income_categories(self):
        """Управление категориями приходов"""
        IncomeCategoriesWindow(self.root, self.db)
    
    def manage_categories_new(self):
        """Управление категориями с иерархией"""
        from category_manager import CategoryManager
        manager = CategoryManager(self.db)
        manager.window.transient(self.root)
    
    def show_analytics(self):
        """Показать аналитику"""
        from analytics import AnalyticsWindow
        analytics = AnalyticsWindow(self.db)
        analytics.window.transient(self.root)
    
    def open_settings(self):
        """Открыть настройки"""
        import subprocess
        subprocess.Popen(['python3', 'settings_gui.py'])
    
    def open_poster_settings(self):
        """Открыть настройки Poster API"""
        from poster_settings_ui import PosterSettingsWindow
        PosterSettingsWindow(self.db.db_path)
    
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
        self.methods = []  # Сохраняем методы с их ID
        self.drag_start_index = None
        self.drag_end_index = None
        
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
        
        # Привязываем события для drag & drop
        self.listbox.bind('<Button-1>', self.on_click)
        self.listbox.bind('<B1-Motion>', self.on_drag)
        self.listbox.bind('<ButtonRelease-1>', self.on_release)
        self.listbox.bind('<KeyPress-Up>', self.on_key_up)
        self.listbox.bind('<KeyPress-Down>', self.on_key_down)
        
        # Загрузка методов
        self.methods = self.db.get_payment_methods()
        for method in self.methods:
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
        method = self.methods[idx]
        
        # Обновляем listbox
        self.listbox.delete(idx)
        self.listbox.insert(idx - 1, item)
        self.listbox.selection_set(idx - 1)
        
        # Обновляем список методов
        self.methods.insert(idx - 1, self.methods.pop(idx))
    
    def move_down(self):
        """Переместить вниз"""
        selection = self.listbox.curselection()
        if not selection or selection[0] == self.listbox.size() - 1:
            return
        
        idx = selection[0]
        item = self.listbox.get(idx)
        method = self.methods[idx]
        
        # Обновляем listbox
        self.listbox.delete(idx)
        self.listbox.insert(idx + 1, item)
        self.listbox.selection_set(idx + 1)
        
        # Обновляем список методов
        self.methods.insert(idx + 1, self.methods.pop(idx))
    
    def save(self):
        """Сохранить порядок"""
        try:
            # Получаем ID методов в текущем порядке
            ordered_ids = [method['id'] for method in self.methods]
            
            # Сохраняем порядок в БД
            self.db.update_payment_methods_order(ordered_ids)
            
        messagebox.showinfo("✅", "Порядок сохранён!")
        self.callback()
        self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("❌", f"Ошибка при сохранении: {str(e)}")
    
    def on_click(self, event):
        """Обработчик клика мыши"""
        self.drag_start_index = self.listbox.nearest(event.y)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.drag_start_index)
    
    def on_drag(self, event):
        """Обработчик перетаскивания"""
        if self.drag_start_index is not None:
            current_index = self.listbox.nearest(event.y)
            if current_index != self.drag_start_index:
                # Подсвечиваем элемент под курсором
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(current_index)
                self.drag_end_index = current_index
    
    def on_release(self, event):
        """Обработчик отпускания мыши"""
        if self.drag_start_index is not None and self.drag_end_index is not None:
            if self.drag_start_index != self.drag_end_index:
                self.move_item(self.drag_start_index, self.drag_end_index)
        
        self.drag_start_index = None
        self.drag_end_index = None
    
    def on_key_up(self, event):
        """Обработчик клавиши стрелка вверх"""
        self.move_up()
        return "break"  # Предотвращаем стандартное поведение
    
    def on_key_down(self, event):
        """Обработчик клавиши стрелка вниз"""
        self.move_down()
        return "break"  # Предотвращаем стандартное поведение
    
    def move_item(self, from_index, to_index):
        """Переместить элемент из одной позиции в другую"""
        if from_index == to_index:
            return
        
        # Получаем элемент
        item = self.listbox.get(from_index)
        method = self.methods[from_index]
        
        # Удаляем из старой позиции
        self.listbox.delete(from_index)
        self.methods.pop(from_index)
        
        # Вставляем в новую позицию
        self.listbox.insert(to_index, item)
        self.methods.insert(to_index, method)
        
        # Выделяем перемещенный элемент
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(to_index)


class CashierReportWindow:
    """Окно создания или редактирования отчёта кассира"""
    
    def __init__(self, parent, db, report_id=None, callback=None):
        self.db = db
        self.report_id = report_id  # Если есть - режим редактирования
        self.callback = callback
    
        self.window = tk.Toplevel(parent)
        if report_id:
            self.window.title("✏️ Редактирование отчёта кассира")
        else:
        self.window.title("📊 Новый отчёт кассира")
        self.window.geometry("900x1100")
        
        self.payment_entries = {}
        self.bill_vars = {}
        self.coin_vars = {}
        self.coins_visible = False
        self.expense_rows = []
        self.income_rows = []
        
        # Основные переменные формы
        self.total_sales_var = tk.StringVar(value="0")
        self.non_cash_total_var = tk.StringVar(value="0")
        self.cash_expected_var = tk.StringVar(value="0")
        self.cash_actual_var = tk.StringVar(value="0")
        self.cash_difference_var = tk.StringVar(value="0")
        self.total_expenses_var = tk.StringVar(value="0")
        self.total_income_var = tk.StringVar(value="0")
        self.total_sales_var.trace('w', lambda *args: self.auto_calculate())
        
        self.create_ui()
    
        # Если редактируем, подгружаем данные
        if self.report_id:
            self.load_report_data()
    
    def load_report_data(self):
        """Загрузка данных из отчёта для редактирования"""
        import json
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM daily_reports WHERE id=?", (self.report_id,))
        report = cursor.fetchone()
        if not report:
            messagebox.showerror("Ошибка", "Отчёт не найден!")
            self.window.destroy()
            return
        report = dict(report)
    
        # Заполняем локейшн/id точки
        locations = self.db.get_locations()
        location_id = report['location_id']
        location_name = next((loc['name'] for loc in locations if loc['id'] == location_id), "")
        self.location_var.set(location_name)
        self.date_var.set(report['report_date'])
    
        # Загрузка методов оплаты
        cursor.execute('''SELECT payment_method_id, amount FROM daily_report_payments WHERE report_id=?''', (self.report_id,))
        for row in cursor.fetchall():
            method_id = row['payment_method_id']
            amount = row['amount']
            if method_id in self.payment_entries:
                self.payment_entries[method_id]['var'].set(str(amount))
    
        # Загрузка купюр/монет
        if report.get('cash_breakdown'):
            cash_data = json.loads(report['cash_breakdown'])
            for denom, count in cash_data.get('bills', {}).items():
                denom = int(denom)
                if denom in self.bill_vars:
                    self.bill_vars[denom].set(str(count))
            for denom, count in cash_data.get('coins', {}).items():
                denom = int(denom)
                if denom in self.coin_vars:
                    self.coin_vars[denom].set(str(count))
    
        # Загрузка расходов
        if report.get('expenses'):
            try:
                loaded_expenses = json.loads(report['expenses'])
                for item in loaded_expenses:
                    self.add_expense_row()
                    row = self.expense_rows[-1]
                    row['category_var'].set(item.get('category', ''))
                    row['amount_var'].set(str(item.get('amount', 0)))
            except Exception:
                pass
    
        # Загрузка приходов
        if report.get('other_income'):
            try:
                loaded_income = json.loads(report['other_income'])
                for item in loaded_income:
                    self.add_income_row()
                    row = self.income_rows[-1]
                    row['category_var'].set(item.get('source', ''))
                    row['amount_var'].set(str(item.get('amount', 0)))
            except Exception:
                pass
    
        # Автопересчёт
        self.auto_calculate()
    
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
            
            # При вводе пересчитываем автоматически
            var.trace('w', lambda *args, m=method, nl=net_label: self.update_net_amount(m, nl))
            var.trace('w', lambda *args: self.auto_calculate())
            
            row += 1
        
        # РЕЗУЛЬТАТ БЕЗНАЛ
        self.cashless_frame = ttk.LabelFrame(frame, text="📊 Итого безнал", padding=15)
        self.cashless_frame.pack(fill='x', padx=20, pady=10)
        
        self.cashless_label = ttk.Label(self.cashless_frame, textvariable=self.non_cash_total_var, 
                                        font=('Arial', 14, 'bold'))
        self.cashless_label.pack()
        
        # НАЛИЧНЫЕ ПЛАН
        cash_plan_frame = ttk.LabelFrame(frame, text="💵 Наличные (по отчёту)", padding=15)
        cash_plan_frame.pack(fill='x', padx=20, pady=10)
        
        self.cash_expected_label = ttk.Label(cash_plan_frame, textvariable=self.cash_expected_var, 
                                             font=('Arial', 12))
        self.cash_expected_label.pack()
        
        # НАЛИЧНЫЕ ФАКТ - БЛОК КУПЮР
        self.create_cash_breakdown_ui(frame)
        
        # РАСХОДЫ
        self.create_expenses_ui(frame)
        
        # ПРИХОДЫ
        self.create_income_ui(frame)
        
        # ИТОГОВЫЕ РЕЗУЛЬТАТЫ
        results_frame = ttk.LabelFrame(frame, text="📊 Итоговые результаты", padding=15)
        results_frame.pack(fill='x', padx=20, pady=10)
        
        self.cash_actual_label = ttk.Label(results_frame, 
                                           textvariable=self.cash_actual_var, 
                                           font=('Arial', 14, 'bold'))
        self.cash_actual_label.pack(pady=5)
        
        self.difference_label = ttk.Label(results_frame, 
                                         textvariable=self.cash_difference_var, 
                                         font=('Arial', 14, 'bold'))
        self.difference_label.pack(pady=5)
        
        # КНОПКИ ДЕЙСТВИЙ
        action_frame = ttk.Frame(frame)
        action_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(action_frame, text="💾 Сохранить отчёт", 
                  command=self.save_report, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(action_frame, text="❌ Отмена", 
                  command=self.window.destroy).pack(side='left', padx=5)
    
    def create_cash_breakdown_ui(self, parent):
        """Создать блок купюр и монет"""
        self.cash_frame = ttk.LabelFrame(parent, text="💵 Наличные факт (по купюрам и монетам)", padding=15)
        self.cash_frame.pack(fill='x', padx=20, pady=10)
        
        # Купюры (всегда видны)
        bills_label = ttk.Label(self.cash_frame, text="💵 Купюры:", font=('Arial', 11, 'bold'))
        bills_label.grid(row=0, column=0, sticky='w', pady=5, columnspan=3)
        
        bill_denominations = [200000, 100000, 50000, 20000, 10000, 5000, 1000]
        row = 1
        
        for denom in bill_denominations:
            var = tk.StringVar(value="0")
            self.bill_vars[denom] = var
            
            ttk.Label(self.cash_frame, text=f"{denom:,} сум:").grid(row=row, column=0, sticky='w', pady=2, padx=5)
            entry = ttk.Entry(self.cash_frame, textvariable=var, width=10)
            entry.grid(row=row, column=1, sticky='w', pady=2)
            
            count_label = ttk.Label(self.cash_frame, text="× шт", foreground='gray')
            count_label.grid(row=row, column=2, sticky='w', pady=2, padx=5)
            
            # Привязываем авто-расчёт
            var.trace('w', lambda *args: self.auto_calculate())
            row += 1
        
        # Кнопка монет
        self.coins_btn = ttk.Button(self.cash_frame, text="💰 Добавить монеты", 
                                   command=self.toggle_coins)
        self.coins_btn.grid(row=row, column=0, columnspan=3, pady=10)
        self.coins_btn_row = row
        row += 1
        
        # Монеты (скрыты по умолчанию)
        self.coins_frame = ttk.Frame(self.cash_frame)
        
        coin_denominations = [1000, 500, 200, 100, 50]
        coin_row = 0
        
        for denom in coin_denominations:
            var = tk.StringVar(value="0")
            self.coin_vars[denom] = var
            
            ttk.Label(self.coins_frame, text=f"{denom} сум:").grid(row=coin_row, column=0, sticky='w', pady=2, padx=5)
            entry = ttk.Entry(self.coins_frame, textvariable=var, width=10)
            entry.grid(row=coin_row, column=1, sticky='w', pady=2)
            
            count_label = ttk.Label(self.coins_frame, text="× шт", foreground='gray')
            count_label.grid(row=coin_row, column=2, sticky='w', pady=2, padx=5)
            
            # Привязываем авто-расчёт
            var.trace('w', lambda *args: self.auto_calculate())
            coin_row += 1
        
        # Итого наличных
        ttk.Separator(self.cash_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, 
                                                           sticky='ew', pady=10)
        self.separator_row = row
        row += 1
        
        self.cash_total_label = ttk.Label(self.cash_frame, 
                                          textvariable=self.cash_actual_var,
                                          font=('Arial', 12, 'bold'))
        self.cash_total_label.grid(row=row, column=0, columnspan=3, pady=5)
    
    def toggle_coins(self):
        """Показать/скрыть блок монет"""
        if self.coins_visible:
            self.coins_frame.grid_remove()
            self.coins_btn.config(text="💰 Добавить монеты")
            self.coins_visible = False
        else:
            # Вставляем монеты между кнопкой и разделителем
            self.coins_frame.grid(row=self.coins_btn_row + 1, column=0, columnspan=3, 
                                sticky='w', pady=5, padx=5)
            self.coins_btn.config(text="💰 Скрыть монеты")
            self.coins_visible = True
    
    def create_expenses_ui(self, parent):
        """Создать блок расходов (динамические строки)"""
        self.expenses_frame = ttk.LabelFrame(parent, text="💸 РАСХОДЫ (из наличных)", padding=15)
        self.expenses_frame.pack(fill='x', padx=20, pady=10)

        self.expenses_rows_frame = ttk.Frame(self.expenses_frame)
        self.expenses_rows_frame.pack(fill='x')

        ttk.Button(self.expenses_frame, text="➕ Добавить расход", command=self.add_expense_row).pack(pady=8)

        self.total_expenses_var.set("ИТОГО РАСХОДОВ: 0 сум")
        ttk.Label(self.expenses_frame, textvariable=self.total_expenses_var, font=('Arial', 11, 'bold'), foreground='blue').pack(pady=4)

    def add_expense_row(self):
        if len(self.expense_rows) >= 20:
            return
        row_frame = ttk.Frame(self.expenses_rows_frame, padding=5)
        row_frame.pack(fill='x', pady=2)

        ttk.Label(row_frame, text="Категория:").pack(side='left', padx=5)
        category_var = tk.StringVar()
        categories = self.db.get_expense_categories()
        category_names = [cat['name'] for cat in categories] if categories else []
        category_combo = ttk.Combobox(row_frame, textvariable=category_var, values=category_names, width=25, state='readonly')
        category_combo.pack(side='left')

        ttk.Label(row_frame, text="Сумма:").pack(side='left', padx=10)
        amount_var = tk.StringVar(value="0")
        amount_entry = ttk.Entry(row_frame, textvariable=amount_var, width=15)
        amount_entry.pack(side='left')

        def on_change(*_):
            self.update_expenses_total()
        amount_var.trace('w', on_change)

        del_btn = ttk.Button(row_frame, text="🗑️", width=3, command=lambda rf=row_frame: self.remove_expense_row(rf))
        del_btn.pack(side='left', padx=6)

        self.expense_rows.append({
            'frame': row_frame,
            'category_var': category_var,
            'amount_var': amount_var,
            'category_combo': category_combo,
            'amount_entry': amount_entry,
        })
        self.update_expenses_total()

    def remove_expense_row(self, frame):
        self.expense_rows = [r for r in self.expense_rows if r['frame'] is not frame]
        frame.destroy()
        self.update_expenses_total()

    def update_expenses_total(self):
        total = 0.0
        for r in self.expense_rows:
            try:
                total += float(r['amount_var'].get() or 0)
            except ValueError:
                pass
        self.total_expenses_var.set(f"ИТОГО РАСХОДОВ: {total:,.0f} сум")
        self.auto_calculate()
    
    def create_income_ui(self, parent):
        """Создать блок приходов (динамические строки)"""
        self.income_frame = ttk.LabelFrame(parent, text="💰 ПРИХОДЫ (не от продаж)", padding=15)
        self.income_frame.pack(fill='x', padx=20, pady=10)

        self.income_rows_frame = ttk.Frame(self.income_frame)
        self.income_rows_frame.pack(fill='x')

        ttk.Button(self.income_frame, text="➕ Добавить приход", command=self.add_income_row).pack(pady=8)

        self.total_income_var.set("ИТОГО ПРИХОДОВ: 0 сум")
        ttk.Label(self.income_frame, textvariable=self.total_income_var, font=('Arial', 11, 'bold'), foreground='blue').pack(pady=4)

    def add_income_row(self):
        if len(self.income_rows) >= 20:
            return
        row_frame = ttk.Frame(self.income_rows_frame, padding=5)
        row_frame.pack(fill='x', pady=2)

        ttk.Label(row_frame, text="Источник:").pack(side='left', padx=5)
        source_var = tk.StringVar()
        # Получаем категории приходов из БД
        income_categories = self.db.get_categories(category_type='income')
        sources = [cat['name'] for cat in income_categories] if income_categories else []
        source_combo = ttk.Combobox(row_frame, textvariable=source_var, values=sources, width=25, state='readonly')
        source_combo.pack(side='left')

        ttk.Label(row_frame, text="Сумма:").pack(side='left', padx=10)
        amount_var = tk.StringVar(value="0")
        amount_entry = ttk.Entry(row_frame, textvariable=amount_var, width=15)
        amount_entry.pack(side='left')

        def on_change(*_):
            self.update_income_total()
        amount_var.trace('w', on_change)

        del_btn = ttk.Button(row_frame, text="🗑️", width=3, command=lambda rf=row_frame: self.remove_income_row(rf))
        del_btn.pack(side='left', padx=6)

        self.income_rows.append({
            'frame': row_frame,
            'category_var': source_var,
            'amount_var': amount_var,
            'category_combo': source_combo,
            'amount_entry': amount_entry,
        })
        self.update_income_total()

    def remove_income_row(self, frame):
        self.income_rows = [r for r in self.income_rows if r['frame'] is not frame]
        frame.destroy()
        self.update_income_total()

    def update_income_total(self):
        total = 0.0
        for r in self.income_rows:
            try:
                total += float(r['amount_var'].get() or 0)
            except ValueError:
                pass
        self.total_income_var.set(f"ИТОГО ПРИХОДОВ: {total:,.0f} сум")
        self.auto_calculate()
    
    def update_net_amount(self, method, net_label):
        """Обновить чистую сумму при вводе"""
        try:
            amount = float(self.payment_entries[method['id']]['var'].get() or 0)
            net = amount * (1 - method['commission_percent'] / 100)
            net_label.config(text=f"→ {net:,.0f} сум")
        except:
            net_label.config(text="→ 0 сум")
    
    def auto_calculate(self):
        """Автоматический пересчёт всех сумм"""
        try:
            # 1. Считаем безнал (терминалы + онлайн)
            non_cash_total = 0
            for method_id, data in self.payment_entries.items():
                method = data['method']
                # Учитываем ВСЕ безналичные методы, включая 'delivery'
                if method['method_type'] in ['terminal', 'online', 'delivery']:
                amount = float(data['var'].get() or 0)
                    non_cash_total += amount
            
            self.non_cash_total_var.set(f"ИТОГО БЕЗНАЛ: {non_cash_total:,.0f} сум")
            
            # 2. Продажи и наличные от продаж
            total_sales = float(self.total_sales_var.get() or 0)
            cash_from_sales = total_sales - non_cash_total
            
            # 3. Факт наличных (ТОЛЬКО купюры + монеты)
            cash_from_bills = 0
            for denom, var in self.bill_vars.items():
                count = float(var.get() or 0)
                cash_from_bills += denom * count
            
            cash_from_coins = 0
            for denom, var in self.coin_vars.items():
                count = float(var.get() or 0)
                cash_from_coins += denom * count
            
            # 4. Итого расходов и приходов из динамических строк
            total_expenses = 0.0
            for r in self.expense_rows:
                try:
                    total_expenses += float(r['amount_var'].get() or 0)
        except ValueError:
                    pass
            total_income = 0.0
            for r in self.income_rows:
                try:
                    total_income += float(r['amount_var'].get() or 0)
                except ValueError:
                    pass
            self.total_expenses_var.set(f"ИТОГО РАСХОДОВ: {total_expenses:,.0f} сум")
            self.total_income_var.set(f"ИТОГО ПРИХОДОВ: {total_income:,.0f} сум")
            
            # 5. ПЛАН наличных: от продаж минус расходы плюс приходы
            cash_expected = cash_from_sales - total_expenses + total_income
            self.cash_expected_var.set(f"ПО ОТЧЁТУ: {cash_expected:,.0f} сум")

            # 6. ФАКТ наличных: только подсчёт купюр/монет
            cash_actual = cash_from_bills + cash_from_coins
            self.cash_actual_var.set(f"ИТОГО НАЛИЧНЫХ: {cash_actual:,.0f} сум")
            
            # 7. Разница
            cash_difference = cash_actual - cash_expected
            if cash_difference > 0:
                text = f"✅ ИЗЛИШЕК: +{cash_difference:,.0f} сум"
                color = 'green'
            elif cash_difference < 0:
                text = f"⚠️ НЕДОСТАЧА: {cash_difference:,.0f} сум"
                color = 'red'
            else:
                text = f"✅ БЕЗ РАСХОЖДЕНИЙ"
                color = 'green'
            
            self.cash_difference_var.set(text)
            self.difference_label.config(foreground=color)
            
        except (ValueError, TypeError):
            # Игнорируем ошибки при вводе (пользователь ещё печатает)
            pass
    
    def add_expense(self):
        """Добавить расход"""
        try:
            amount = float(self.expense_amount_var.get() or 0)
            comment = self.expense_comment_var.get().strip()
            category = self.expense_category_var.get()
            
            if amount <= 0:
                messagebox.showerror("❌", "Введите сумму расхода")
                return
            
            if not comment:
                messagebox.showerror("❌", "Введите комментарий")
                return
            
            # Получаем ID категории
            category_id = None
            if category and category != 'Без категории':
                categories = self.db.get_expense_categories()
                cat = next((c for c in categories if c['name'] == category), None)
                if cat:
                    category_id = cat['id']
            
            expense_data = {
                'category': category or 'Без категории',
                'amount': amount,
                'comment': comment,
                'category_id': category_id
            }
            
            self.expenses.append(expense_data)
            self.update_expenses_tree()
            
            # Очищаем поля
            self.expense_amount_var.set("")
            self.expense_comment_var.set("")
            self.expense_category_var.set("Без категории")
            
            self.auto_calculate()
            
        except ValueError:
            messagebox.showerror("❌", "Проверьте сумму расхода")
    
    def update_expenses_tree(self):
        """Обновить Treeview расходов"""
        # Очищаем
        for item in self.expenses_tree.get_children():
            self.expenses_tree.delete(item)
        
        # Добавляем
        for i, expense in enumerate(self.expenses):
            item_id = self.expenses_tree.insert('', 'end', 
                                               values=(expense['category'], 
                                                      f"{expense['amount']:,.0f}",
                                                      expense['comment']),
                                               tags=(i,))
            self.expenses_tree.tag_bind(item_id, '<Double-1>', lambda e, idx=i: self.remove_expense(idx))
    
    def remove_expense(self, index):
        """Удалить расход"""
        if 0 <= index < len(self.expenses):
        self.expenses.pop(index)
            self.update_expenses_tree()
            self.auto_calculate()
    
    def add_income(self):
        """Добавить приход"""
        try:
            amount = float(self.income_amount_var.get() or 0)
            comment = self.income_comment_var.get().strip()
            source = self.income_source_var.get()
            
            if amount <= 0:
                messagebox.showerror("❌", "Введите сумму прихода")
                return
            
            if not source:
                messagebox.showerror("❌", "Выберите источник прихода")
                return
            
            income_data = {
                'source': source,
                'amount': amount,
                'comment': comment or ''
            }
            
            self.other_income.append(income_data)
            self.update_income_tree()
            
            # Очищаем поля
            self.income_amount_var.set("")
            self.income_comment_var.set("")
            self.income_source_var.set("")
            
            self.auto_calculate()
            
        except ValueError:
            messagebox.showerror("❌", "Проверьте сумму прихода")
    
    def update_income_tree(self):
        """Обновить Treeview приходов"""
        # Очищаем
        for item in self.income_tree.get_children():
            self.income_tree.delete(item)
        
        # Добавляем
        for i, income in enumerate(self.other_income):
            item_id = self.income_tree.insert('', 'end', 
                                             values=(income['source'],
                                                    f"{income['amount']:,.0f}",
                                                    income['comment']),
                                             tags=(i,))
            self.income_tree.tag_bind(item_id, '<Double-1>', lambda e, idx=i: self.remove_income(idx))
    
    def remove_income(self, index):
        """Удалить приход"""
        if 0 <= index < len(self.other_income):
            self.other_income.pop(index)
            self.update_income_tree()
            self.auto_calculate()
    
    def save_report(self):
        """Сохранить отчёт (create/edit)"""
        try:
            import json
            from datetime import datetime

            # Валидация обязательных полей уже выполнена выше в __init__/create_ui
            # Сбор общих данных для расчётов
            total_sales = float(self.total_sales_var.get() or 0)

            # Безнал (только terminal и online)
            total_cashless = 0.0
            for method_id, data in self.payment_entries.items():
                method = data['method']
                if method['method_type'] in ['terminal', 'online', 'delivery']:
                    total_cashless += float(data['var'].get() or 0)

            # План наличных (будет уточнён после расчёта расходов/приходов ниже)
            cash_expected = total_sales - total_cashless

            # Детализация наличных
            cash_breakdown = {
                'bills': {str(denom): int(self.bill_vars[denom].get() or 0) for denom in self.bill_vars},
                'coins': {str(denom): int(self.coin_vars[denom].get() or 0) for denom in self.coin_vars},
            }

            cash_from_bills = sum(denom * int(self.bill_vars[denom].get() or 0) for denom in self.bill_vars)
            cash_from_coins = sum(denom * int(self.coin_vars[denom].get() or 0) for denom in self.coin_vars)

            # данные для сохранения JSON из rows
            expenses_data = []
            for r in self.expense_rows:
                category = r['category_var'].get()
                try:
                    amount_val = float(r['amount_var'].get() or 0)
                except ValueError:
                    amount_val = 0
                if category and amount_val > 0:
                    expenses_data.append({'category': category, 'amount': amount_val})

            # Получаем категории приходов для поиска category_id
            income_categories = self.db.get_categories(category_type='income')
            
            income_data = []
            for r in self.income_rows:
                source = r['category_var'].get()
                try:
                    amount_val = float(r['amount_var'].get() or 0)
                except ValueError:
                    amount_val = 0
                if source and amount_val > 0:
                    # Находим category_id по названию
                    income_cat = next((c for c in income_categories if c['name'] == source), None)
                    category_id = income_cat['id'] if income_cat else None
                    income_data.append({'source': source, 'amount': amount_val, 'category_id': category_id})

            total_expenses = sum(item['amount'] for item in expenses_data)
            total_income = sum(item['amount'] for item in income_data)

            # Правильная логика: План = (продажи - безнал) - расходы + приходы
            cash_expected = (total_sales - total_cashless) - total_expenses + total_income
            # Факт = только купюры/монеты
            cash_actual = cash_from_bills + cash_from_coins

            expenses_json = json.dumps(expenses_data)
            income_json = json.dumps(income_data)

            cursor = self.db.conn.cursor()

            if self.report_id:
                # UPDATE существующего отчёта
                cursor.execute('''
                    UPDATE daily_reports 
                    SET total_sales=?, cash_expected=?, cash_actual=?, cash_difference=?, cash_breakdown=?, expenses=?, other_income=?, status=?
                    WHERE id=?
                ''', (
                    total_sales,
                    cash_expected,
                    cash_actual,
                    cash_actual - cash_expected,
                    json.dumps(cash_breakdown),
                    expenses_json,
                    income_json,
                    'closed',
                    self.report_id
                ))

                # Пересохранить платежи: удалить старые и вставить новые
                cursor.execute('DELETE FROM daily_report_payments WHERE report_id=?', (self.report_id,))
                for method_id, data in self.payment_entries.items():
                    amount = float(data['var'].get() or 0)
                    if amount > 0:
                        cursor.execute('''
                            INSERT INTO daily_report_payments (report_id, payment_method_id, amount)
                            VALUES (?, ?, ?)
                        ''', (self.report_id, method_id, amount))

                # Удалить старые приходы и вставить новые
                cursor.execute('DELETE FROM non_sales_income WHERE report_id=?', (self.report_id,))
                cash_accounts = self.db.get_accounts('cash')
                if cash_accounts and income_data:
                    for income in income_data:
                        cash_account_id = cash_accounts[0]['id']
                        self.db.add_non_sales_income(
                            self.report_id,
                            cash_account_id,
                            income['amount'],
                            category_id=income.get('category_id'),
                            description=income['source']
                        )

                self.db.conn.commit()
                messagebox.showinfo("✅", "Отчёт успешно обновлён!")
            else:
                # INSERT нового отчёта
            report_date = datetime.strptime(self.date_var.get(), '%d.%m.%Y').date()
                # Получаем ID точки по имени
                locations = self.db.get_locations()
                location = next((loc for loc in locations if loc['name'] == self.location_var.get()), None)
            self.report_id = self.db.create_daily_report(
                report_date,
                    location['id'] if location else None,
                total_sales,
                "GUI User"
            )
            
                # Сохранить методы оплаты в daily_report_payments
            for method_id, data in self.payment_entries.items():
                amount = float(data['var'].get() or 0)
                if amount > 0:
                        cursor.execute('''
                            INSERT INTO daily_report_payments (report_id, payment_method_id, amount)
                            VALUES (?, ?, ?)
                        ''', (self.report_id, method_id, amount))

                # Обновить денежные поля и JSON в daily_reports
                cursor.execute('''
                    UPDATE daily_reports 
                    SET cash_expected=?, cash_actual=?, cash_difference=?, cash_breakdown=?, expenses=?, other_income=?, status='closed'
                    WHERE id=?
                ''', (
                    cash_expected,
                    cash_actual,
                    cash_actual - cash_expected,
                    json.dumps(cash_breakdown),
                    expenses_json,
                    income_json,
                    self.report_id
                ))

                # Сохранить приходы в non_sales_income
            cash_accounts = self.db.get_accounts('cash')
                if cash_accounts and income_data:
                    for income in income_data:
                        cash_account_id = cash_accounts[0]['id']
                        self.db.add_non_sales_income(
                        self.report_id,
                            cash_account_id,
                            income['amount'],
                            category_id=income.get('category_id'),
                            description=income['source']
                        )

                self.db.conn.commit()
                messagebox.showinfo("✅", "Отчёт успешно создан!")

            if self.callback:
                self.callback()
            self.window.destroy()
        except ValueError as e:
            messagebox.showerror("❌ Ошибка", f"Проверьте введённые данные:\n{e}")
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Не удалось сохранить:\n{e}")
    
    def edit_report(self):
        """Открыть отчёт на редактирование"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("⚠️", "Выберите отчёт для редактирования")
            return
        item = self.tree.item(selection[0])
        report_id = item['values'][0]
        CashierReportWindow(self.window, self.db, report_id=report_id, callback=self.load_data)


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

        # Кнопки действий
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="✏️ Редактировать", command=self.edit_report).pack(side='left', padx=5)
        # Можно добавить и другие кнопки (например, Детали/Удалить и т.д.)
        
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
        
        # Двойной клик открывает редактирование
        self.tree.bind('<Double-1>', lambda e: self.edit_report())
    
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
        
        reports = self.db.get_reports(limit=100, location_id=location_id, status='closed')
        
        for report in reports:
            status_emoji = '✅' if report.get('status') == 'closed' else '📝'
            diff = report.get('cash_difference', 0)
            diff_color = 'red' if diff < 0 else ('green' if diff > 0 else 'black')
            
            self.tree.insert('', 'end', values=(
                report['id'],
                report['report_date'],
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
    
    def edit_report(self):
        """Открыть отчёт на редактирование"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("⚠️", "Выберите отчёт для редактирования")
                return
        item = self.tree.item(selection[0])
        report_id = item['values'][0]
        CashierReportWindow(self.window, self.db, report_id=report_id, callback=self.load_data)


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
        
        # Двойной клик для просмотра истории
        self.tree.bind('<Double-1>', self.show_account_history)
        
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
    
    def show_account_history(self, event=None):
        """Показать историю счёта"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        account_name = item['values'][0]  # Название счёта (с эмодзи)
        # Убираем эмодзи для поиска
        account_name_clean = account_name.replace('💵 ', '').replace('🏦 ', '')
        
        # Находим ID счёта по имени
        accounts = self.db.get_accounts()
        account = next((acc for acc in accounts if acc['name'] == account_name_clean), None)
        
        if account:
            AccountHistoryWindow(self.window, self.db, account['id'], account_name_clean)


class AccountHistoryWindow:
    """Окно истории операций по счёту"""
    
    def __init__(self, parent, db, account_id, account_name):
        self.db = db
        self.account_id = account_id
        self.account_name = account_name
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"📜 История: {account_name}")
        self.window.geometry("900x600")
        
        self.create_ui()
        self.load_data()
    
    def create_ui(self):
        """Создать интерфейс"""
        ttk.Label(self.window, 
                 text=f"📜 ИСТОРИЯ ОПЕРАЦИЙ: {self.account_name}", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Таблица
        list_frame = ttk.Frame(self.window)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('Дата', 'Тип', 'Сумма', 'Описание', 'Точка', 'Отчёт')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        self.tree.heading('Дата', text='Дата')
        self.tree.heading('Тип', text='Тип')
        self.tree.heading('Сумма', text='Сумма')
        self.tree.heading('Описание', text='Описание')
        self.tree.heading('Точка', text='Точка')
        self.tree.heading('Отчёт', text='Отчёт #')
        
        self.tree.column('Дата', width=100)
        self.tree.column('Тип', width=50)
        self.tree.column('Сумма', width=120)
        self.tree.column('Описание', width=250)
        self.tree.column('Точка', width=150)
        self.tree.column('Отчёт', width=80)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Итого
        total_frame = ttk.Frame(self.window)
        total_frame.pack(fill='x', padx=20, pady=10)
        
        self.total_label = ttk.Label(total_frame, text="", 
                                     font=('Arial', 12, 'bold'))
        self.total_label.pack()
        
        # Кнопки
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(btn_frame, text="🔄 Обновить", 
                  command=self.load_data).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📋 Открыть отчёт", 
                  command=self.open_report).pack(side='left', padx=5)
    
    def load_data(self):
        """Загрузить данные"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        history = self.db.get_account_history(self.account_id)
        
        total = 0
        for op in history:
            operation_type = op['operation_type']
            amount = op['amount']
            
            # Считаем итог
            if operation_type == '+':
                total += amount
                amount_str = f"+{amount:,.0f}"
                tag = 'plus'
            else:
                total -= amount
                amount_str = f"-{amount:,.0f}"
                tag = 'minus'
            
            emoji = '💰' if operation_type == '+' else '💸'
            
            self.tree.insert('', 'end', values=(
                op['date'],
                emoji,
                amount_str,
                op['description'],
                op.get('location', ''),
                f"#{op['report_id']}"
            ), tags=(tag,))
        
        # Цвета
        self.tree.tag_configure('plus', foreground='green')
        self.tree.tag_configure('minus', foreground='red')
        
        # Итого
        self.total_label.config(
            text=f"📊 ТЕКУЩИЙ БАЛАНС: {total:,.0f} сум",
            foreground='blue'
        )
    
    def open_report(self):
        """Открыть отчёт"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("⚠️", "Выберите операцию")
            return
        
        item = self.tree.item(selection[0])
        report_str = item['values'][5]  # "#123"
        report_id = int(report_str.replace('#', ''))
        
        # Открываем отчёт на редактирование
        CashierReportWindow(self.window, self.db, report_id=report_id, callback=self.load_data)


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


class IncomeCategoriesWindow:
    """Окно управления категориями приходов"""
    
    def __init__(self, parent, db):
        self.db = db
        self.window = tk.Toplevel(parent)
        self.window.title("💰 Управление категориями приходов")
        self.window.geometry("700x500")
        
        self.create_ui()
        self.load_data()
    
    def create_ui(self):
        """Создать интерфейс"""
        ttk.Label(self.window, text="💰 КАТЕГОРИИ ПРИХОДОВ", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Таблица
        list_frame = ttk.Frame(self.window)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Название', 'Активна')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column('ID', width=50)
        self.tree.column('Название', width=400)
        self.tree.column('Активна', width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Кнопки
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(btn_frame, text="➕ Добавить", 
                  command=self.add_category).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="✏️ Изменить", 
                  command=self.edit_category).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Удалить", 
                  command=self.delete_category).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", 
                  command=self.load_data).pack(side='left', padx=5)
    
    def load_data(self):
        """Загрузить данные"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получаем категории приходов из БД
        categories = self.db.get_categories(category_type='income')
        for cat in categories:
            active = '✅' if cat.get('is_active', True) else '❌'
            self.tree.insert('', 'end', values=(
                cat['id'],
                cat['name'],
                active
            ))
    
    def add_category(self):
        """Добавить категорию"""
        AddIncomeCategoryDialog(self.window, self.db, self.load_data)
    
    def edit_category(self):
        """Изменить категорию"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("⚠️", "Выберите категорию")
            return
        
        item = self.tree.item(selection[0])
        category_id = item['values'][0]
        category_name = item['values'][1]
        
        EditIncomeCategoryDialog(self.window, self.db, category_id, 
                                category_name, self.load_data)
    
    def delete_category(self):
        """Удалить категорию"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("⚠️", "Выберите категорию")
            return
        
        if messagebox.askyesno("❓", "Удалить категорию?"):
            item = self.tree.item(selection[0])
            category_id = item['values'][0]
            # Используем универсальную функцию удаления через SQL
            cursor = self.db.conn.cursor()
            cursor.execute('UPDATE categories SET is_active=0 WHERE id=?', (category_id,))
            self.db.conn.commit()
            self.load_data()
            messagebox.showinfo("✅", "Категория удалена")


class AddIncomeCategoryDialog:
    """Диалог добавления категории прихода"""
    
    def __init__(self, parent, db, callback):
        self.db = db
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("➕ Добавить категорию прихода")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_ui()
    
    def create_ui(self):
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Название:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="💾 Сохранить", 
                  command=self.save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Отмена", 
                  command=self.dialog.destroy).pack(side='left', padx=5)
    
    def save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("❌", "Введите название")
            return
        
        self.db.add_category(name, 'income')
        self.callback()
        self.dialog.destroy()
        messagebox.showinfo("✅", "Категория добавлена")


class EditIncomeCategoryDialog:
    """Диалог редактирования категории прихода"""
    
    def __init__(self, parent, db, category_id, current_name, callback):
        self.db = db
        self.category_id = category_id
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("✏️ Изменить категорию прихода")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.name_var = tk.StringVar(value=current_name)
        self.create_ui()
    
    def create_ui(self):
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Название:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="💾 Сохранить", 
                  command=self.save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Отмена", 
                  command=self.dialog.destroy).pack(side='left', padx=5)
    
    def save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("❌", "Введите название")
            return
        
        # Используем универсальную функцию обновления категории
        cursor = self.db.conn.cursor()
        cursor.execute('UPDATE categories SET name=? WHERE id=?', 
                      (name, self.category_id))
        self.db.conn.commit()
        
        self.callback()
        self.dialog.destroy()
        messagebox.showinfo("✅", "Категория обновлена")


# Импорт Quick Add Window
from quick_add_window import QuickAddWindow
# Импорт Timeline Window
from timeline_window import TimelineWindow
from permissions_ui import PermissionsWindow

if __name__ == '__main__':
    app = MainApp()
    app.run()
