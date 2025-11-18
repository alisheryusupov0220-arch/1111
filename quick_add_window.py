#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Add Window - Быстрое добавление расходов и приходов
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from permissions_manager import permissions


class QuickAddWindow:
    """Окно быстрого добавления операций"""

    def __init__(self, parent, db, current_user_id):
        self.parent = parent
        self.db = db
        self.db_path = "finance_v5.db"
        self.current_user_id = current_user_id
        self.permissions = permissions

        self.window = tk.Toplevel(parent)
        self.window.title("⚡ Быстрое добавление")
        self.window.geometry("600x500")

        # Центрируем окно
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")

        self._create_ui()

    def _create_ui(self):
        header = ttk.Frame(self.window, padding=20)
        header.pack(fill=tk.X)

        ttk.Label(header, text="⚡ Быстрое добавление",
                  font=("Arial", 16, "bold")).pack()
        ttk.Label(header, text="Добавить расход или приход без отчёта",
                  font=("Arial", 10)).pack()

        btn_frame = ttk.Frame(self.window, padding=20)
        btn_frame.pack()

        ttk.Button(btn_frame, text="📉 Добавить расход",
                   command=self._show_expense_form,
                   width=25).pack(side=tk.LEFT, padx=10)

        ttk.Button(btn_frame, text="📈 Добавить приход",
                   command=self._show_income_form,
                   width=25).pack(side=tk.LEFT, padx=10)

        self.form_frame = ttk.Frame(self.window, padding=20)
        self.form_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Button(self.window, text="❌ Закрыть",
                   command=self.window.destroy).pack(pady=10)

    # ------------------------------------------------------------------
    # Формы
    # ------------------------------------------------------------------
    def _show_expense_form(self):
        if not self.permissions.has_permission(self.current_user_id, 'quick_add_expense'):
            messagebox.showerror("Доступ запрещён", "У вас нет прав для добавления расходов.")
            return

        for widget in self.form_frame.winfo_children():
            widget.destroy()

        row = 0

        ttk.Label(self.form_frame, text="📅 Дата:", font=("Arial", 10, "bold"))\
            .grid(row=row, column=0, sticky="w", pady=10)
        date_entry = ttk.Entry(self.form_frame, width=35, font=("Arial", 10))
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.grid(row=row, column=1, pady=10, sticky="ew")

        row += 1

        ttk.Label(self.form_frame, text="📁 Категория:", font=("Arial", 10, "bold"))\
            .grid(row=row, column=0, sticky="w", pady=10)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(self.form_frame, textvariable=category_var,
                                      width=33, state="readonly", font=("Arial", 10))
        category_combo.grid(row=row, column=1, pady=10, sticky="ew")

        expense_categories = self._load_expense_categories()
        if expense_categories:
            category_combo["values"] = [cat[1] for cat in expense_categories]
            category_combo.current(0)
        else:
            messagebox.showwarning("Внимание", "Нет категорий расходов. Создайте их сначала.")
            return

        row += 1

        ttk.Label(self.form_frame, text="💰 Сумма:", font=("Arial", 10, "bold"))\
            .grid(row=row, column=0, sticky="w", pady=10)
        amount_entry = ttk.Entry(self.form_frame, width=35, font=("Arial", 10))
        amount_entry.grid(row=row, column=1, pady=10, sticky="ew")

        row += 1

        ttk.Label(self.form_frame, text="💳 Счёт (списать с):", font=("Arial", 10, "bold"))\
            .grid(row=row, column=0, sticky="w", pady=10)
        account_var = tk.StringVar()
        account_combo = ttk.Combobox(self.form_frame, textvariable=account_var,
                                     width=33, state="readonly", font=("Arial", 10))
        account_combo.grid(row=row, column=1, pady=10, sticky="ew")

        accounts = self._load_accounts()
        if accounts:
            account_combo["values"] = [acc[1] for acc in accounts]
            account_combo.current(0)
        else:
            messagebox.showwarning("Внимание", "Нет счетов. Создайте их сначала.")
            return

        row += 1

        ttk.Label(self.form_frame, text="📝 Описание:", font=("Arial", 10, "bold"))\
            .grid(row=row, column=0, sticky="nw", pady=10)
        desc_text = tk.Text(self.form_frame, width=35, height=4, font=("Arial", 10))
        desc_text.grid(row=row, column=1, pady=10, sticky="ew")

        row += 1

        def save_expense():
            try:
                date_value = date_entry.get().strip()
                category_name = category_var.get()
                amount_value = self._parse_amount(amount_entry.get())
                account_name = account_var.get()
                description = desc_text.get("1.0", tk.END).strip()

                if not category_name or not account_name:
                    messagebox.showwarning("Ошибка", "Заполните все обязательные поля!")
                    return

                if amount_value <= 0:
                    messagebox.showwarning("Ошибка", "Сумма должна быть больше нуля!")
                    return

                category_id = next((c[0] for c in expense_categories if c[1] == category_name), None)
                account_id = next((a[0] for a in accounts if a[1] == account_name), None)

                if not category_id or not account_id:
                    messagebox.showerror("Ошибка", "Категория или счёт не найдены")
                    return

                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO timeline (date, type, category_id, account_id, amount, description, user_id, source)
                    VALUES (?, 'expense', ?, ?, ?, ?, ?, 'quick_add')
                    """,
                    (date_value, category_id, account_id, amount_value, description, self.current_user_id)
                )
                conn.commit()
                conn.close()

                messagebox.showinfo("✅ Успех", f"Расход добавлен!\nСумма: {self._format_amount(amount_value)}")
                amount_entry.delete(0, tk.END)
                desc_text.delete("1.0", tk.END)
                amount_entry.focus_set()

            except ValueError as err:
                messagebox.showerror("Ошибка", str(err))
            except Exception as exc:
                messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{exc}")

        ttk.Button(self.form_frame, text="✅ Сохранить расход",
                   command=save_expense).grid(row=row, column=0, columnspan=2, pady=20)

        self.form_frame.columnconfigure(1, weight=1)
        amount_entry.focus_set()

    def _show_income_form(self):
        if not self.permissions.has_permission(self.current_user_id, 'quick_add_income'):
            messagebox.showerror("Доступ запрещён", "У вас нет прав для добавления приходов.")
            return

        for widget in self.form_frame.winfo_children():
            widget.destroy()

        row = 0

        ttk.Label(self.form_frame, text="📅 Дата:", font=("Arial", 10, "bold"))\
            .grid(row=row, column=0, sticky="w", pady=10)
        date_entry = ttk.Entry(self.form_frame, width=35, font=("Arial", 10))
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.grid(row=row, column=1, pady=10, sticky="ew")

        row += 1

        ttk.Label(self.form_frame, text="📁 Категория:", font=("Arial", 10, "bold"))\
            .grid(row=row, column=0, sticky="w", pady=10)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(self.form_frame, textvariable=category_var,
                                      width=33, state="readonly", font=("Arial", 10))
        category_combo.grid(row=row, column=1, pady=10, sticky="ew")

        income_categories = self._load_income_categories()
        if income_categories:
            category_combo["values"] = [cat[1] for cat in income_categories]
            category_combo.current(0)
        else:
            messagebox.showwarning("Внимание", "Нет категорий приходов. Создайте их сначала.")
            return

        row += 1

        ttk.Label(self.form_frame, text="💰 Сумма:", font=("Arial", 10, "bold"))\
            .grid(row=row, column=0, sticky="w", pady=10)
        amount_entry = ttk.Entry(self.form_frame, width=35, font=("Arial", 10))
        amount_entry.grid(row=row, column=1, pady=10, sticky="ew")

        row += 1

        ttk.Label(self.form_frame, text="💳 Счёт (зачислить на):", font=("Arial", 10, "bold"))\
            .grid(row=row, column=0, sticky="w", pady=10)
        account_var = tk.StringVar()
        account_combo = ttk.Combobox(self.form_frame, textvariable=account_var,
                                     width=33, state="readonly", font=("Arial", 10))
        account_combo.grid(row=row, column=1, pady=10, sticky="ew")

        accounts = self._load_accounts()
        if accounts:
            account_combo["values"] = [acc[1] for acc in accounts]
            account_combo.current(0)
        else:
            messagebox.showwarning("Внимание", "Нет счетов. Создайте их сначала.")
            return

        row += 1

        ttk.Label(self.form_frame, text="📝 Описание:", font=("Arial", 10, "bold"))\
            .grid(row=row, column=0, sticky="nw", pady=10)
        desc_text = tk.Text(self.form_frame, width=35, height=4, font=("Arial", 10))
        desc_text.grid(row=row, column=1, pady=10, sticky="ew")

        row += 1

        def save_income():
            try:
                date_value = date_entry.get().strip()
                category_name = category_var.get()
                amount_value = self._parse_amount(amount_entry.get())
                account_name = account_var.get()
                description = desc_text.get("1.0", tk.END).strip()

                if not category_name or not account_name:
                    messagebox.showwarning("Ошибка", "Заполните все обязательные поля!")
                    return

                if amount_value <= 0:
                    messagebox.showwarning("Ошибка", "Сумма должна быть больше нуля!")
                    return

                category_id = next((c[0] for c in income_categories if c[1] == category_name), None)
                account_id = next((a[0] for a in accounts if a[1] == account_name), None)

                if not category_id or not account_id:
                    messagebox.showerror("Ошибка", "Категория или счёт не найдены")
                    return

                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO timeline (date, type, category_id, account_id, amount, description, user_id, source)
                    VALUES (?, 'income', ?, ?, ?, ?, ?, 'quick_add')
                    """,
                    (date_value, category_id, account_id, amount_value, description, self.current_user_id)
                )
                conn.commit()
                conn.close()

                messagebox.showinfo("✅ Успех", f"Приход добавлен!\nСумма: {self._format_amount(amount_value)}")
                amount_entry.delete(0, tk.END)
                desc_text.delete("1.0", tk.END)
                amount_entry.focus_set()

            except ValueError as err:
                messagebox.showerror("Ошибка", str(err))
            except Exception as exc:
                messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{exc}")

        ttk.Button(self.form_frame, text="✅ Сохранить приход",
                   command=save_income).grid(row=row, column=0, columnspan=2, pady=20)

        self.form_frame.columnconfigure(1, weight=1)
        amount_entry.focus_set()

    # ------------------------------------------------------------------
    # Вспомогательные методы
    # ------------------------------------------------------------------
    def _load_accounts(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM accounts WHERE is_active = 1 ORDER BY name")
            accounts = cursor.fetchall()
            conn.close()
            return accounts
        except Exception as exc:
            print(f"Ошибка загрузки счетов: {exc}")
            return []

    def _load_expense_categories(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM expense_categories WHERE is_active = 1 ORDER BY name")
            categories = cursor.fetchall()
            conn.close()
            return categories
        except Exception as exc:
            print(f"Ошибка загрузки категорий расходов: {exc}")
            return []

    def _load_income_categories(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM income_categories WHERE is_active = 1 ORDER BY name")
            categories = cursor.fetchall()
            conn.close()
            return categories
        except Exception as exc:
            print(f"Ошибка загрузки категорий приходов: {exc}")
            return []

    def _parse_amount(self, value: str) -> float:
        if not value:
            raise ValueError("Сумма должна быть указана")
        cleaned = value.replace(" ", "").replace(",", ".")
        return float(cleaned)

    def _format_amount(self, amount: float) -> str:
        try:
            return f"{int(amount):,}".replace(",", " ") + " UZS"
        except Exception:
            return f"{amount} UZS"

