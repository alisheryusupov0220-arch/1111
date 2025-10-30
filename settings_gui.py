#!/usr/bin/env python3
"""
GUI для управления настройками системы
Простой интерфейс для изменения config.json
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from settings import config

class SettingsGUI:
    """Графический интерфейс настроек"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⚙️ Настройки Air Waffle Finance")
        self.root.geometry("700x600")
        
        # Создаём вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладки
        self.create_general_tab()
        self.create_telegram_tab()
        self.create_payments_tab()
        self.create_reports_tab()
        self.create_integrations_tab()
        
        # Кнопки внизу
        self.create_bottom_buttons()
    
    def create_general_tab(self):
        """Вкладка: Общие"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='🏠 Общие')
        
        # База данных
        ttk.Label(frame, text="📊 БАЗА ДАННЫХ", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=10, padx=10)
        
        ttk.Label(frame, text="Путь к БД:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.db_path_var = tk.StringVar(value=config.db_path)
        ttk.Entry(frame, textvariable=self.db_path_var, width=50).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Button(frame, text="📂 Выбрать", command=self.select_db_file).grid(row=1, column=2, padx=5)
        
        # Бэкапы
        self.backup_enabled_var = tk.BooleanVar(value=config.get('database.backup_enabled', True))
        ttk.Checkbutton(frame, text="Автоматические бэкапы", variable=self.backup_enabled_var).grid(row=2, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        # UI
        ttk.Label(frame, text="🎨 ИНТЕРФЕЙС", font=('Arial', 12, 'bold')).grid(row=3, column=0, columnspan=2, sticky='w', pady=10, padx=10)
        
        ttk.Label(frame, text="Знаков после запятой:").grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.decimal_var = tk.IntVar(value=config.decimal_places)
        ttk.Spinbox(frame, from_=0, to=2, textvariable=self.decimal_var, width=10).grid(row=4, column=1, sticky='w', padx=10, pady=5)
        
        ttk.Label(frame, text="Разделитель тысяч:").grid(row=5, column=0, sticky='w', padx=10, pady=5)
        self.separator_var = tk.StringVar(value=config.get('ui.thousand_separator', ','))
        ttk.Combobox(frame, textvariable=self.separator_var, values=[',', ' ', '.', ''], width=10, state='readonly').grid(row=5, column=1, sticky='w', padx=10, pady=5)
    
    def create_telegram_tab(self):
        """Вкладка: Telegram"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='🤖 Telegram')
        
        ttk.Label(frame, text="🤖 TELEGRAM БОТ", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=10, padx=10)
        
        # Включить/выключить
        self.tg_enabled_var = tk.BooleanVar(value=config.telegram_enabled)
        ttk.Checkbutton(frame, text="✅ Включить Telegram бота", variable=self.tg_enabled_var, command=self.toggle_telegram).grid(row=1, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        # Токен
        ttk.Label(frame, text="Bot Token:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.bot_token_var = tk.StringVar(value=config.bot_token)
        self.bot_token_entry = ttk.Entry(frame, textvariable=self.bot_token_var, width=50, show='*')
        self.bot_token_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # Показать токен
        self.show_token_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="👁️ Показать токен", variable=self.show_token_var, command=self.toggle_token_visibility).grid(row=3, column=1, sticky='w', padx=10)
        
        # Admin Chat ID
        ttk.Label(frame, text="Admin Chat ID:").grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.admin_chat_var = tk.StringVar(value=config.get('telegram.admin_chat_id', ''))
        ttk.Entry(frame, textvariable=self.admin_chat_var, width=50).grid(row=4, column=1, padx=10, pady=5)
        
        # Уведомления
        self.notifications_var = tk.BooleanVar(value=config.get('telegram.notifications_enabled', False))
        ttk.Checkbutton(frame, text="Отправлять уведомления админу", variable=self.notifications_var).grid(row=5, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        # Инструкция
        info_text = """
        📝 КАК ПОЛУЧИТЬ ТОКЕН:
        1. Найдите @BotFather в Telegram
        2. Отправьте /newbot
        3. Следуйте инструкциям
        4. Скопируйте токен сюда
        """
        ttk.Label(frame, text=info_text, justify='left', foreground='gray').grid(row=6, column=0, columnspan=2, sticky='w', padx=10, pady=10)
        
        # Тест подключения
        ttk.Button(frame, text="🔌 Тест подключения", command=self.test_telegram).grid(row=7, column=0, columnspan=2, pady=10)
    
    def create_payments_tab(self):
        """Вкладка: Методы оплаты"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='💳 Оплата')
        
        ttk.Label(frame, text="💳 МЕТОДЫ ОПЛАТЫ", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=10, padx=10)
        
        # Группировка
        self.group_payments_var = tk.BooleanVar(value=config.group_payments)
        ttk.Checkbutton(frame, text="📊 Группировать методы по типу (Uzcard вместо Uzcard YATT, Uzcard Payme...)", variable=self.group_payments_var).grid(row=1, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        ttk.Label(frame, text="Включить методы:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', padx=10, pady=10)
        
        # Терминалы
        self.terminals_var = tk.BooleanVar(value=config.get('payment_methods.enabled_methods.terminals', True))
        ttk.Checkbutton(frame, text="📟 Терминалы", variable=self.terminals_var).grid(row=3, column=0, sticky='w', padx=20, pady=5)
        
        # Онлайн
        self.online_var = tk.BooleanVar(value=config.get('payment_methods.enabled_methods.online', True))
        ttk.Checkbutton(frame, text="🌐 Онлайн платежи", variable=self.online_var).grid(row=4, column=0, sticky='w', padx=20, pady=5)
        
        # Доставки
        self.delivery_var = tk.BooleanVar(value=config.get('payment_methods.enabled_methods.delivery', True))
        ttk.Checkbutton(frame, text="🚚 Доставки", variable=self.delivery_var).grid(row=5, column=0, sticky='w', padx=20, pady=5)
        
        ttk.Label(frame, text="Порядок отображения:", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky='w', padx=10, pady=10)
        
        # Порядок (простой список)
        order = config.get_payment_order()
        order_text = " → ".join(order)
        ttk.Label(frame, text=order_text).grid(row=7, column=0, sticky='w', padx=20, pady=5)
        ttk.Button(frame, text="🔄 Изменить порядок", command=self.change_order).grid(row=8, column=0, padx=20, pady=5)
    
    def create_reports_tab(self):
        """Вкладка: Отчёты"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='📋 Отчёты')
        
        ttk.Label(frame, text="📋 НАСТРОЙКИ ОТЧЁТОВ", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=10, padx=10)
        
        # Автосохранение
        self.autosave_var = tk.BooleanVar(value=config.get('reports.auto_save', True))
        ttk.Checkbutton(frame, text="💾 Автоматическое сохранение", variable=self.autosave_var).grid(row=1, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        # Подсчёт наличных
        self.require_cash_var = tk.BooleanVar(value=config.require_cash_count)
        ttk.Checkbutton(frame, text="💵 Обязательный подсчёт наличных", variable=self.require_cash_var).grid(row=2, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        # Категории расходов
        self.require_category_var = tk.BooleanVar(value=config.get('reports.require_expense_category', False))
        ttk.Checkbutton(frame, text="📂 Обязательная категория расходов", variable=self.require_category_var).grid(row=3, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        # Отрицательная касса
        self.negative_cash_var = tk.BooleanVar(value=config.get('reports.allow_negative_cash', False))
        ttk.Checkbutton(frame, text="⚠️ Разрешить отрицательную кассу", variable=self.negative_cash_var).grid(row=4, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        # Порог предупреждения
        ttk.Label(frame, text="Предупреждать при расхождении:").grid(row=5, column=0, sticky='w', padx=10, pady=5)
        self.warn_threshold_var = tk.DoubleVar(value=config.warn_threshold)
        ttk.Spinbox(frame, from_=0, to=100, increment=0.5, textvariable=self.warn_threshold_var, width=10).grid(row=5, column=1, sticky='w', padx=10, pady=5)
        ttk.Label(frame, text="%").grid(row=5, column=1, sticky='w', padx=70)
    
    def create_integrations_tab(self):
        """Вкладка: Интеграции"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='🔌 Интеграции')
        
        ttk.Label(frame, text="🔌 ИНТЕГРАЦИИ", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=10, padx=10)
        
        # Bank API
        self.bank_api_var = tk.BooleanVar(value=config.get('integrations.bank_api_enabled', False))
        ttk.Checkbutton(frame, text="🏦 Включить Bank API", variable=self.bank_api_var, command=self.toggle_bank_api).grid(row=1, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        ttk.Label(frame, text="API URL:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.bank_url_var = tk.StringVar(value=config.get('integrations.bank_api_url', ''))
        self.bank_url_entry = ttk.Entry(frame, textvariable=self.bank_url_var, width=50)
        self.bank_url_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(frame, text="API Key:").grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.bank_key_var = tk.StringVar(value=config.get('integrations.bank_api_key', ''))
        self.bank_key_entry = ttk.Entry(frame, textvariable=self.bank_key_var, width=50, show='*')
        self.bank_key_entry.grid(row=3, column=1, padx=10, pady=5)
        
        # Excel Export
        self.excel_var = tk.BooleanVar(value=config.get('integrations.export_excel_enabled', True))
        ttk.Checkbutton(frame, text="📊 Экспорт в Excel", variable=self.excel_var).grid(row=4, column=0, columnspan=2, sticky='w', padx=10, pady=10)
        
        ttk.Label(frame, text="Папка экспорта:").grid(row=5, column=0, sticky='w', padx=10, pady=5)
        self.export_path_var = tk.StringVar(value=config.get('integrations.export_path', 'exports/'))
        ttk.Entry(frame, textvariable=self.export_path_var, width=50).grid(row=5, column=1, padx=10, pady=5)
        ttk.Button(frame, text="📂", command=self.select_export_folder).grid(row=5, column=2, padx=5)
        
        self.toggle_bank_api()  # Применить состояние
    
    def create_bottom_buttons(self):
        """Кнопки внизу окна"""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="💾 Сохранить", command=self.save_settings, style='Accent.TButton').pack(side='right', padx=5)
        ttk.Button(button_frame, text="❌ Отмена", command=self.root.quit).pack(side='right', padx=5)
        ttk.Button(button_frame, text="🔄 Сброс", command=self.reset_settings).pack(side='left', padx=5)
        ttk.Button(button_frame, text="📤 Экспорт", command=self.export_config).pack(side='left', padx=5)
        ttk.Button(button_frame, text="📥 Импорт", command=self.import_config).pack(side='left', padx=5)
    
    # ========== ОБРАБОТЧИКИ ==========
    
    def toggle_telegram(self):
        """Включить/выключить telegram поля"""
        enabled = self.tg_enabled_var.get()
        state = 'normal' if enabled else 'disabled'
        self.bot_token_entry['state'] = state
    
    def toggle_token_visibility(self):
        """Показать/скрыть токен"""
        show = self.show_token_var.get()
        self.bot_token_entry['show'] = '' if show else '*'
    
    def toggle_bank_api(self):
        """Включить/выключить bank api поля"""
        enabled = self.bank_api_var.get()
        state = 'normal' if enabled else 'disabled'
        self.bank_url_entry['state'] = state
        self.bank_key_entry['state'] = state
    
    def select_db_file(self):
        """Выбрать файл БД"""
        filename = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite Database", "*.db")])
        if filename:
            self.db_path_var.set(filename)
    
    def select_export_folder(self):
        """Выбрать папку экспорта"""
        folder = filedialog.askdirectory()
        if folder:
            self.export_path_var.set(folder + '/')
    
    def change_order(self):
        """Изменить порядок методов оплаты"""
        messagebox.showinfo("В разработке", "Функция drag&drop в следующей версии!")
    
    def test_telegram(self):
        """Тест подключения к Telegram"""
        token = self.bot_token_var.get()
        if not token:
            messagebox.showerror("Ошибка", "Введите токен!")
            return
        
        messagebox.showinfo("Тест", "Функция в разработке!\nТокен будет проверен при сохранении.")
    
    def save_settings(self):
        """Сохранить все настройки"""
        try:
            # Общие
            config.set('database.path', self.db_path_var.get())
            config.set('database.backup_enabled', self.backup_enabled_var.get())
            config.set('ui.decimal_places', self.decimal_var.get())
            config.set('ui.thousand_separator', self.separator_var.get())
            
            # Telegram
            config.set('telegram.enabled', self.tg_enabled_var.get())
            config.set('telegram.bot_token', self.bot_token_var.get())
            config.set('telegram.admin_chat_id', self.admin_chat_var.get())
            config.set('telegram.notifications_enabled', self.notifications_var.get())
            
            # Методы оплаты
            config.set('payment_methods.group_by_type', self.group_payments_var.get())
            config.set('payment_methods.enabled_methods.terminals', self.terminals_var.get())
            config.set('payment_methods.enabled_methods.online', self.online_var.get())
            config.set('payment_methods.enabled_methods.delivery', self.delivery_var.get())
            
            # Отчёты
            config.set('reports.auto_save', self.autosave_var.get())
            config.set('reports.require_cash_count', self.require_cash_var.get())
            config.set('reports.require_expense_category', self.require_category_var.get())
            config.set('reports.allow_negative_cash', self.negative_cash_var.get())
            config.set('reports.warn_threshold_percent', self.warn_threshold_var.get())
            
            # Интеграции
            config.set('integrations.bank_api_enabled', self.bank_api_var.get())
            config.set('integrations.bank_api_url', self.bank_url_var.get())
            config.set('integrations.bank_api_key', self.bank_key_var.get())
            config.set('integrations.export_excel_enabled', self.excel_var.get())
            config.set('integrations.export_path', self.export_path_var.get())
            
            # Сохраняем в файл
            config.save_config()
            
            messagebox.showinfo("✅ Успех", "Настройки сохранены!")
            
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Не удалось сохранить:\n{e}")
    
    def reset_settings(self):
        """Сброс настроек"""
        if messagebox.askyesno("Сброс", "Сбросить все настройки к значениям по умолчанию?"):
            config.reset_to_defaults()
            messagebox.showinfo("✅", "Настройки сброшены!\nПерезапустите приложение.")
            self.root.quit()
    
    def export_config(self):
        """Экспорт конфига"""
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if filename:
            config.export_to_file(filename)
            messagebox.showinfo("✅", f"Конфиг экспортирован:\n{filename}")
    
    def import_config(self):
        """Импорт конфига"""
        filename = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if filename:
            config.import_from_file(filename)
            messagebox.showinfo("✅", "Конфиг импортирован!\nПерезапустите приложение.")
            self.root.quit()
    
    def run(self):
        """Запустить GUI"""
        self.root.mainloop()


if __name__ == '__main__':
    app = SettingsGUI()
    app.run()
