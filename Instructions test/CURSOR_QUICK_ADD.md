# 🤖 ИНСТРУКЦИЯ ДЛЯ CURSOR AI

## 🎯 ЗАДАЧА: Создать окно "⚡ Быстрое добавление расходов/приходов"

---

## 📋 ЧТО НУЖНО СДЕЛАТЬ:

### **Шаг 1: Добавить кнопку на главный экран**

**Файл:** `main_app.py`

**Найти:** Сетку кнопок (около строки 78-93)

**Добавить кнопку:**
```python
buttons = [
    ("📅 Timeline", self.show_timeline, 0, 0),
    ("📊 Новый отчёт кассира", self.new_cashier_report, 0, 1),
    ("👀 Просмотр отчётов", self.view_reports, 0, 2),
    ("⚡ Быстрое добавление", self.show_quick_add, 1, 0),  # <-- ДОБАВИТЬ ЭТО!
    ("💰 Балансы счетов", self.view_balances, 1, 1),      # <-- Сдвинуть вниз
    # ... остальные кнопки
]
```

---

### **Шаг 2: Создать метод show_quick_add**

**В `main_app.py` добавить метод:**

```python
def show_quick_add(self):
    """Быстрое добавление расходов/приходов"""
    QuickAddWindow(self.root, self.db)
```

---

### **Шаг 3: Создать файл `quick_add_window.py`**

Создать новый файл в папке проекта со следующей структурой:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Add Window - Быстрое добавление расходов и приходов
Без привязки к отчётам кассира
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class QuickAddWindow:
    """Окно быстрого добавления"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.db_path = "finance_v5.db"
        
        # Создаём окно
        self.window = tk.Toplevel(parent)
        self.window.title("⚡ Быстрое добавление")
        self.window.geometry("600x500")
        
        # Центрирование
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        self._create_ui()
    
    def _create_ui(self):
        """Создание интерфейса"""
        
        # Заголовок
        header = ttk.Frame(self.window, padding=20)
        header.pack(fill=tk.X)
        
        ttk.Label(header, text="⚡ Быстрое добавление", 
                 font=("Arial", 16, "bold")).pack()
        ttk.Label(header, text="Добавить расход или приход без отчёта", 
                 font=("Arial", 10)).pack()
        
        # Кнопки выбора
        btn_frame = ttk.Frame(self.window, padding=20)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="📉 Добавить расход", 
                  command=self._show_expense_form,
                  width=25).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(btn_frame, text="📈 Добавить приход", 
                  command=self._show_income_form,
                  width=25).pack(side=tk.LEFT, padx=10)
        
        # Фрейм для форм
        self.form_frame = ttk.Frame(self.window, padding=20)
        self.form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка закрыть
        ttk.Button(self.window, text="❌ Закрыть", 
                  command=self.window.destroy).pack(pady=10)
    
    def _show_expense_form(self):
        """Форма добавления расхода"""
        # Очищаем фрейм
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        
        # ФОРМА РАСХОДА
        row = 0
        
        # Дата
        ttk.Label(self.form_frame, text="📅 Дата:", 
                 font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=10)
        date_entry = ttk.Entry(self.form_frame, width=35, font=("Arial", 10))
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.grid(row=row, column=1, pady=10, sticky="ew")
        
        row += 1
        
        # Категория
        ttk.Label(self.form_frame, text="📁 Категория:", 
                 font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=10)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(self.form_frame, textvariable=category_var, 
                                     width=33, state="readonly", font=("Arial", 10))
        category_combo.grid(row=row, column=1, pady=10, sticky="ew")
        
        # Загрузка категорий
        categories = self._load_expense_categories()
        if categories:
            category_combo["values"] = [cat[1] for cat in categories]
            category_combo.current(0)
        
        row += 1
        
        # Сумма
        ttk.Label(self.form_frame, text="💰 Сумма:", 
                 font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=10)
        amount_entry = ttk.Entry(self.form_frame, width=35, font=("Arial", 10))
        amount_entry.grid(row=row, column=1, pady=10, sticky="ew")
        
        row += 1
        
        # Счёт
        ttk.Label(self.form_frame, text="💳 Счёт (списать с):", 
                 font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=10)
        account_var = tk.StringVar()
        account_combo = ttk.Combobox(self.form_frame, textvariable=account_var, 
                                    width=33, state="readonly", font=("Arial", 10))
        account_combo.grid(row=row, column=1, pady=10, sticky="ew")
        
        # Загрузка счетов
        accounts = self._load_accounts()
        if accounts:
            account_combo["values"] = [acc[1] for acc in accounts]
            account_combo.current(0)
        
        row += 1
        
        # Описание
        ttk.Label(self.form_frame, text="📝 Описание:", 
                 font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="nw", pady=10)
        desc_text = tk.Text(self.form_frame, width=35, height=4, font=("Arial", 10))
        desc_text.grid(row=row, column=1, pady=10, sticky="ew")
        
        row += 1
        
        # Кнопка сохранить
        def save_expense():
            try:
                date = date_entry.get()
                cat_name = category_var.get()
                amount_str = amount_entry.get().strip().replace(" ", "")
                account_name = account_var.get()
                desc = desc_text.get("1.0", tk.END).strip()
                
                # Валидация
                if not cat_name or not amount_str or not account_name:
                    messagebox.showwarning("Ошибка", "Заполните все поля!")
                    return
                
                amount = float(amount_str)
                if amount <= 0:
                    messagebox.showwarning("Ошибка", "Сумма должна быть больше нуля!")
                    return
                
                # ID
                cat_id = next((c[0] for c in categories if c[1] == cat_name), None)
                acc_id = next((a[0] for a in accounts if a[1] == account_name), None)
                
                # Сохранение
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO timeline (date, type, category_id, amount, account_id, description, source)
                    VALUES (?, 'expense', ?, ?, ?, ?, 'quick_add')
                """, (date, cat_id, amount, acc_id, desc))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("✅ Успех", f"Расход добавлен!\nСумма: {self._format_amount(amount)}")
                
                # Очистка формы
                amount_entry.delete(0, tk.END)
                desc_text.delete("1.0", tk.END)
                
            except ValueError:
                messagebox.showerror("Ошибка", "Сумма должна быть числом!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сохранения:\n{str(e)}")
        
        ttk.Button(self.form_frame, text="✅ Сохранить расход", 
                  command=save_expense).grid(row=row, column=0, columnspan=2, pady=20)
        
        # Растягивание
        self.form_frame.columnconfigure(1, weight=1)
        
        # Фокус
        amount_entry.focus()
    
    def _show_income_form(self):
        """Форма добавления прихода"""
        # Аналогично _show_expense_form, но:
        # - type = 'income'
        # - Категории из income_categories
        # - Текст "зачислить на" вместо "списать с"
        
        # РЕАЛИЗУЙ АНАЛОГИЧНО РАСХОДУ!
        # Копируй логику из _show_expense_form
        # Меняй:
        # 1. category_var → _load_income_categories()
        # 2. type = 'income'
        # 3. Текст кнопки "✅ Сохранить приход"
        
        pass  # <-- РЕАЛИЗОВАТЬ!
    
    # Вспомогательные методы
    
    def _load_accounts(self):
        """Загрузка счетов"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM accounts WHERE is_active = 1 ORDER BY name")
            accounts = cursor.fetchall()
            conn.close()
            return accounts
        except:
            return []
    
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
            return []
    
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
            return []
    
    def _format_amount(self, amount):
        """Форматирование суммы"""
        return f"{int(amount):,}".replace(",", " ") + " UZS"
```

---

### **Шаг 4: Добавить импорт в main_app.py**

**В конце файла `main_app.py`, перед `if __name__ == '__main__':`**

```python
# Импорт Quick Add Window
from quick_add_window import QuickAddWindow

if __name__ == '__main__':
    app = MainApp()
    app.run()
```

---

### **Шаг 5: Убрать кнопки добавления из Timeline**

**Файл:** `timeline_window.py`

**Найти:** Панель "➕ Быстрое добавление" (строка ~38-50)

**УДАЛИТЬ ВСЮ ПАНЕЛЬ:**
```python
# ========================================
# ПАНЕЛЬ БЫСТРОГО ДОБАВЛЕНИЯ
# ========================================
add_frame = ttk.LabelFrame(...)
# ... ВСЁ ЭТО УДАЛИТЬ!
```

**И удалить методы:**
- `_show_add_expense()`
- `_show_add_income()`
- `_show_add_sale()`

Timeline должен быть **только для просмотра**!

---

## ✅ РЕЗУЛЬТАТ:

После выполнения:

1. **На главном экране** появится кнопка "⚡ Быстрое добавление"
2. **При клике** откроется окно с кнопками "Расход" / "Приход"
3. **Формы** добавляют напрямую в `timeline`
4. **Timeline** показывает всё (read-only)

---

## 🧪 ТЕСТИРОВАНИЕ:

1. Запусти `python3 main_app.py`
2. Жми "⚡ Быстрое добавление"
3. Жми "📉 Добавить расход"
4. Заполни форму, сохрани
5. Открой Timeline → увидишь операцию!

---

## 🐛 ВОЗМОЖНЫЕ ОШИБКИ:

### Ошибка: "No module named 'quick_add_window'"
→ Файл не в папке проекта или не сохранён

### Ошибка: "no such table: timeline"
→ Миграция не применена (но у вас timeline уже есть)

### Форма не сохраняет
→ Проверь что в `_show_income_form()` реализована та же логика что и в `_show_expense_form()`

---

## 📝 ВАЖНО:

В `_show_income_form()` нужно **самому реализовать** форму!

Копируй логику из `_show_expense_form()` и меняй:
1. `_load_income_categories()` вместо `_load_expense_categories()`
2. `type = 'income'` вместо `'expense'`
3. Текст "Сохранить приход" вместо "Сохранить расход"

---

**Версия:** 1.0  
**Для:** Cursor AI  
**Язык:** Python + Tkinter  
**Сложность:** Средняя ⭐⭐⭐
