#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Timeline Window v3 - С правильной структурой БД
Использует timeline напрямую + загружает счета из accounts
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class TimelineWindow:
    """Окно Timeline - единая лента событий"""
    
    def __init__(self, parent, db):
        """Инициализация окна Timeline"""
        self.parent = parent
        self.db = db
        self.db_path = "finance_v5.db"
        
        # Создаём окно
        self.window = tk.Toplevel(parent)
        self.window.title("📅 Timeline - История операций")
        self.window.geometry("1400x800")
        
        # Центрирование окна
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        self._create_ui()
        self._load_data()
    
    def _create_ui(self):
        """Создание интерфейса"""
        
        # ========================================
        # ПАНЕЛЬ ФИЛЬТРОВ
        # ========================================
        filter_frame = ttk.LabelFrame(self.window, text="🔍 Фильтры", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Даты
        date_row = ttk.Frame(filter_frame)
        date_row.pack(fill=tk.X, pady=2)
        
        ttk.Label(date_row, text="От:").pack(side=tk.LEFT, padx=5)
        self.date_from = ttk.Entry(date_row, width=12)
        self.date_from.pack(side=tk.LEFT, padx=5)
        self.date_from.insert(0, datetime.now().strftime("%Y-%m-01"))
        
        ttk.Label(date_row, text="До:").pack(side=tk.LEFT, padx=5)
        self.date_to = ttk.Entry(date_row, width=12)
        self.date_to.pack(side=tk.LEFT, padx=5)
        self.date_to.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Тип
        filter_row = ttk.Frame(filter_frame)
        filter_row.pack(fill=tk.X, pady=2)
        
        ttk.Label(filter_row, text="Тип:").pack(side=tk.LEFT, padx=5)
        self.type_var = tk.StringVar(value="Все")
        type_combo = ttk.Combobox(filter_row, textvariable=self.type_var, 
                                  values=["Все", "Расходы", "Приходы", "Продажи", "Зарплаты"],
                                  width=12, state="readonly")
        type_combo.pack(side=tk.LEFT, padx=5)
        
        # Кнопки
        btn_frame = ttk.Frame(filter_row)
        btn_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(btn_frame, text="🔄 Применить", 
                  command=self._load_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="❌ Сбросить", 
                  command=self._reset_filters).pack(side=tk.LEFT, padx=2)
        
        # ========================================
        # СТАТИСТИКА
        # ========================================
        stats_frame = ttk.LabelFrame(self.window, text="📊 Статистика", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="", font=("Arial", 10))
        self.stats_label.pack()
        
        # ========================================
        # ТАБЛИЦА
        # ========================================
        table_frame = ttk.Frame(self.window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        
        columns = ("date", "type", "category", "amount", "account", "user", "description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Заголовки
        self.tree.heading("date", text="📅 Дата и время")
        self.tree.heading("type", text="📝 Тип")
        self.tree.heading("category", text="📁 Категория")
        self.tree.heading("amount", text="💰 Сумма")
        self.tree.heading("account", text="💳 Счёт")
        self.tree.heading("user", text="👤 Пользователь")
        self.tree.heading("description", text="📄 Описание")
        
        # Ширина
        self.tree.column("date", width=150)
        self.tree.column("type", width=100)
        self.tree.column("category", width=150)
        self.tree.column("amount", width=120)
        self.tree.column("account", width=150)
        self.tree.column("user", width=120)
        self.tree.column("description", width=300)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Цвета
        self.tree.tag_configure("expense", foreground="#d32f2f")
        self.tree.tag_configure("income", foreground="#388e3c")
        self.tree.tag_configure("sale", foreground="#1976d2")
        self.tree.tag_configure("salary", foreground="#f57c00")
        
        # Двойной клик
        self.tree.bind("<Double-1>", self._show_details)
        
        # ========================================
        # ПАНЕЛЬ ДЕЙСТВИЙ
        # ========================================
        action_frame = ttk.Frame(self.window)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(action_frame, text="🔄 Обновить", 
                  command=self._load_data).pack(side=tk.LEFT, padx=5)

        info_label = ttk.Label(
            action_frame,
            text="💡 Для добавления операций используйте 'Быстрое добавление' или 'Новый отчёт кассира'",
            foreground="gray",
            font=("Arial", 9)
        )
        info_label.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(action_frame, text="❌ Закрыть", 
                  command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _load_data(self):
        """Загрузка данных"""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Используем JOIN с accounts для получения названия счёта
            query = """
            SELECT 
                datetime(t.date) as formatted_date,
                t.type,
                COALESCE(ec.name, ic.name, 'Без категории') as category_name,
                t.amount,
                COALESCE(a.name, '-') as account_name,
                COALESCE(u.username, 'Система') as user_name,
                COALESCE(t.description, '-') as description
            FROM timeline t
            LEFT JOIN expense_categories ec ON t.category_id = ec.id AND t.type = 'expense'
            LEFT JOIN income_categories ic ON t.category_id = ic.id AND t.type = 'income'
            LEFT JOIN accounts a ON t.account_id = a.id
            LEFT JOIN users u ON t.user_id = u.id
            WHERE t.date >= ? AND t.date <= ?
            ORDER BY t.date DESC, t.id DESC
            """
            
            cursor.execute(query, (self.date_from.get(), self.date_to.get() + " 23:59:59"))
            rows = cursor.fetchall()
            
            total_expenses = 0
            total_income = 0
            total_sales = 0
            
            for row in rows:
                date_str, type_val, category, amount, account, user, desc = row
                
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    date_formatted = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    date_formatted = date_str
                
                type_map = {
                    "expense": "Расход",
                    "income": "Приход",
                    "sale": "Продажа",
                    "salary": "Зарплата"
                }
                type_display = type_map.get(type_val, type_val)
                
                amount_formatted = self._format_amount(amount)
                
                tag = type_val
                
                self.tree.insert("", "end", values=(
                    date_formatted,
                    type_display,
                    category,
                    amount_formatted,
                    account,
                    user,
                    desc
                ), tags=(tag,))
                
                if type_val == "expense":
                    total_expenses += amount
                elif type_val == "income":
                    total_income += amount
                elif type_val == "sale":
                    total_sales += amount
            
            conn.close()
            self._update_stats(len(rows), total_expenses, total_income, total_sales)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
    
    def _format_amount(self, amount: float) -> str:
        """Форматирование суммы"""
        try:
            amount_str = f"{int(amount):,}".replace(",", " ")
            return f"{amount_str} UZS"
        except:
            return f"{amount} UZS"
    
    def _update_stats(self, count: int, expenses: float, income: float, sales: float):
        """Обновление статистики"""
        stats_text = (
            f"📝 Операций: {count}  |  "
            f"📉 Расходы: {self._format_amount(expenses)}  |  "
            f"📈 Приходы: {self._format_amount(income)}  |  "
            f"💰 Продажи: {self._format_amount(sales)}"
        )
        self.stats_label.config(text=stats_text)
    
    def _reset_filters(self):
        """Сброс фильтров"""
        self.date_from.delete(0, tk.END)
        self.date_from.insert(0, datetime.now().strftime("%Y-%m-01"))
        self.date_to.delete(0, tk.END)
        self.date_to.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.type_var.set("Все")
        self._load_data()
    
    def _show_details(self, event):
        """Детали операции"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item["values"]
        
        details = (
            f"📅 Дата: {values[0]}\n"
            f"📝 Тип: {values[1]}\n"
            f"📁 Категория: {values[2]}\n"
            f"💰 Сумма: {values[3]}\n"
            f"💳 Счёт: {values[4]}\n"
            f"👤 Пользователь: {values[5]}\n"
            f"📄 Описание: {values[6]}"
        )
        
        messagebox.showinfo("Детали операции", details)

# Для совместимости
TimelineUI = TimelineWindow
