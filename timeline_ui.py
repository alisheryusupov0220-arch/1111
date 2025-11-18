#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Timeline UI v2 - С формами добавления операций
Добавлены кнопки: Добавить расход, Добавить приход, Добавить продажу
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional

class TimelineUI:
    """UI для Timeline с формами добавления операций"""
    
    def __init__(self, parent_notebook):
        """Инициализация Timeline UI"""
        self.db_path = "finance_v5.db"
        
        # Создаём вкладку
        self.frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.frame, text="📅 Timeline")
        
        self._create_ui()
        self._load_data()
    
    def _create_ui(self):
        """Создание интерфейса"""
        
        # ========================================
        # ПАНЕЛЬ БЫСТРОГО ДОБАВЛЕНИЯ (ВЕРХ)
        # ========================================
        add_frame = ttk.LabelFrame(self.frame, text="➕ Быстрое добавление", padding=10)
        add_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Кнопки добавления
        btn_container = ttk.Frame(add_frame)
        btn_container.pack()
        
        ttk.Button(btn_container, text="📉 Добавить расход", 
                  command=self._show_add_expense, 
                  width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_container, text="📈 Добавить приход", 
                  command=self._show_add_income, 
                  width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_container, text="💰 Добавить продажу", 
                  command=self._show_add_sale, 
                  width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_container, text="👔 Добавить зарплату", 
                  command=self._show_add_salary, 
                  width=20).pack(side=tk.LEFT, padx=5)
        
        # ========================================
        # ПАНЕЛЬ ФИЛЬТРОВ
        # ========================================
        filter_frame = ttk.LabelFrame(self.frame, text="🔍 Фильтры", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Строка 1: Даты
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
        
        # Строка 2: Тип и пользователь
        filter_row = ttk.Frame(filter_frame)
        filter_row.pack(fill=tk.X, pady=2)
        
        ttk.Label(filter_row, text="Тип:").pack(side=tk.LEFT, padx=5)
        self.type_var = tk.StringVar(value="Все")
        type_combo = ttk.Combobox(filter_row, textvariable=self.type_var, 
                                  values=["Все", "Расходы", "Приходы", "Продажи", "Зарплаты"],
                                  width=12, state="readonly")
        type_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_row, text="Пользователь:").pack(side=tk.LEFT, padx=5)
        self.user_var = tk.StringVar(value="Все")
        self.user_combo = ttk.Combobox(filter_row, textvariable=self.user_var,
                                      width=15, state="readonly")
        self.user_combo.pack(side=tk.LEFT, padx=5)
        
        # Кнопки
        btn_frame = ttk.Frame(filter_row)
        btn_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(btn_frame, text="🔄 Применить", 
                  command=self._apply_filters).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="❌ Сбросить", 
                  command=self._reset_filters).pack(side=tk.LEFT, padx=2)
        
        # ========================================
        # СТАТИСТИКА
        # ========================================
        stats_frame = ttk.LabelFrame(self.frame, text="📊 Статистика", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="", font=("Arial", 10))
        self.stats_label.pack()
        
        # ========================================
        # ТАБЛИЦА
        # ========================================
        table_frame = ttk.Frame(self.frame)
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
        self.tree.column("account", width=100)
        self.tree.column("user", width=120)
        self.tree.column("description", width=250)
        
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
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(action_frame, text="🔄 Обновить", 
                  command=self._load_data).pack(side=tk.LEFT, padx=5)
        
        info_label = ttk.Label(action_frame, 
                              text="💡 Двойной клик = детали операции",
                              foreground="gray")
        info_label.pack(side=tk.RIGHT, padx=5)
    
    # ========================================
    # ФОРМЫ ДОБАВЛЕНИЯ
    # ========================================
    
    def _show_add_expense(self):
        """Форма добавления расхода"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("📉 Добавить расход")
        dialog.geometry("450x400")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Центрирование
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Поля
        ttk.Label(dialog, text="Дата:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        date_entry = ttk.Entry(dialog, width=30)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Категория:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(dialog, textvariable=category_var, width=28, state="readonly")
        category_combo.grid(row=1, column=1, padx=10, pady=10)
        
        # Загрузка категорий
        categories = self._load_expense_categories()
        category_combo["values"] = [f"{cat[1]}" for cat in categories]
        if categories:
            category_combo.current(0)
        
        ttk.Label(dialog, text="Сумма:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        amount_entry = ttk.Entry(dialog, width=30)
        amount_entry.grid(row=2, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Счёт:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        account_var = tk.StringVar(value="Наличные")
        account_combo = ttk.Combobox(dialog, textvariable=account_var, 
                                    values=["Наличные", "Безнал", "Карта", "Каспи"],
                                    width=28, state="readonly")
        account_combo.grid(row=3, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Описание:").grid(row=4, column=0, padx=10, pady=10, sticky="nw")
        desc_text = tk.Text(dialog, width=30, height=5)
        desc_text.grid(row=4, column=1, padx=10, pady=10)
        
        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def save():
            try:
                date = date_entry.get()
                cat_name = category_var.get()
                amount = float(amount_entry.get())
                account = account_var.get()
                desc = desc_text.get("1.0", tk.END).strip()
                
                if not cat_name or amount <= 0:
                    messagebox.showwarning("Ошибка", "Заполните все поля!")
                    return
                
                # Получаем ID категории
                cat_id = next((cat[0] for cat in categories if cat[1] == cat_name), None)
                
                # Сохранение
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # В expenses
                cursor.execute("""
                    INSERT INTO expenses (date, category_id, amount, payment_type, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (date, cat_id, amount, account, desc))
                
                # В timeline
                cursor.execute("""
                    INSERT INTO timeline (date, type, category_id, amount, account_type, payment_type, description)
                    VALUES (?, 'expense', ?, ?, ?, ?, ?)
                """, (date, cat_id, amount, account, account, desc))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Успех", "Расход добавлен!")
                dialog.destroy()
                self._load_data()
                
            except ValueError:
                messagebox.showerror("Ошибка", "Сумма должна быть числом!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{str(e)}")
        
        ttk.Button(btn_frame, text="✅ Сохранить", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _show_add_income(self):
        """Форма добавления прихода"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("📈 Добавить приход")
        dialog.geometry("450x400")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Центрирование
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Аналогично расходам
        ttk.Label(dialog, text="Дата:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        date_entry = ttk.Entry(dialog, width=30)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Категория:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(dialog, textvariable=category_var, width=28, state="readonly")
        category_combo.grid(row=1, column=1, padx=10, pady=10)
        
        categories = self._load_income_categories()
        category_combo["values"] = [f"{cat[1]}" for cat in categories]
        if categories:
            category_combo.current(0)
        
        ttk.Label(dialog, text="Сумма:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        amount_entry = ttk.Entry(dialog, width=30)
        amount_entry.grid(row=2, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Описание:").grid(row=3, column=0, padx=10, pady=10, sticky="nw")
        desc_text = tk.Text(dialog, width=30, height=8)
        desc_text.grid(row=3, column=1, padx=10, pady=10)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        def save():
            try:
                date = date_entry.get()
                cat_name = category_var.get()
                amount = float(amount_entry.get())
                desc = desc_text.get("1.0", tk.END).strip()
                
                if not cat_name or amount <= 0:
                    messagebox.showwarning("Ошибка", "Заполните все поля!")
                    return
                
                cat_id = next((cat[0] for cat in categories if cat[1] == cat_name), None)
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO income (date, category_id, amount, description)
                    VALUES (?, ?, ?, ?)
                """, (date, cat_id, amount, desc))
                
                cursor.execute("""
                    INSERT INTO timeline (date, type, category_id, amount, description)
                    VALUES (?, 'income', ?, ?, ?)
                """, (date, cat_id, amount, desc))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Успех", "Приход добавлен!")
                dialog.destroy()
                self._load_data()
                
            except ValueError:
                messagebox.showerror("Ошибка", "Сумма должна быть числом!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{str(e)}")
        
        ttk.Button(btn_frame, text="✅ Сохранить", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _show_add_sale(self):
        """Форма добавления продажи"""
        messagebox.showinfo("В разработке", "Используйте 'Новый отчёт кассира' для добавления продаж")
    
    def _show_add_salary(self):
        """Форма добавления зарплаты"""
        messagebox.showinfo("В разработке", "Функция будет добавлена в следующей версии")
    
    # ========================================
    # ЗАГРУЗКА КАТЕГОРИЙ
    # ========================================
    
    def _load_expense_categories(self):
        """Загрузка категорий расходов"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM expense_categories WHERE is_active = 1 ORDER BY name")
            categories = cursor.fetchall()
            conn.close()
            return categories
        except:
            return [(1, "Общие расходы")]
    
    def _load_income_categories(self):
        """Загрузка категорий приходов"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM income_categories WHERE is_active = 1 ORDER BY name")
            categories = cursor.fetchall()
            conn.close()
            return categories
        except:
            return [(1, "Общие приходы")]
    
    # ========================================
    # ЗАГРУЗКА ДАННЫХ (БЕЗ ИЗМЕНЕНИЙ)
    # ========================================
    
    def _load_data(self):
        """Загрузка данных"""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self._load_users()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT 
                datetime(date) as formatted_date,
                type,
                category_name,
                amount,
                account_type,
                user_name,
                description
            FROM timeline_view
            WHERE date >= ? AND date <= ?
            ORDER BY date DESC, id DESC
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
                account_display = account if account else "-"
                user_display = user if user else "Система"
                desc_display = desc if desc else "-"
                
                tag = type_val
                
                self.tree.insert("", "end", values=(
                    date_formatted,
                    type_display,
                    category,
                    amount_formatted,
                    account_display,
                    user_display,
                    desc_display
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
    
    def _load_users(self):
        """Загрузка пользователей"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT user_name FROM timeline_view WHERE user_name IS NOT NULL ORDER BY user_name")
            users = ["Все"] + [row[0] for row in cursor.fetchall()]
            self.user_combo["values"] = users
            conn.close()
        except:
            pass
    
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
    
    def _apply_filters(self):
        """Применение фильтров"""
        self._load_data()
    
    def _reset_filters(self):
        """Сброс фильтров"""
        self.date_from.delete(0, tk.END)
        self.date_from.insert(0, datetime.now().strftime("%Y-%m-01"))
        self.date_to.delete(0, tk.END)
        self.date_to.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.type_var.set("Все")
        self.user_var.set("Все")
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

def main():
    """Тест"""
    root = tk.Tk()
    root.title("Timeline Test")
    root.geometry("1200x750")
    
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    timeline = TimelineUI(notebook)
    
    root.mainloop()

if __name__ == "__main__":
    main()

