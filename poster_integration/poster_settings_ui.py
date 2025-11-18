#!/usr/bin/env python3
"""
UI для настройки интеграции с Poster
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from sync_poster import PosterSync


class PosterSettingsWindow:
    """Окно настроек Poster"""
    
    def __init__(self, db_path='finance_v5.db'):
        self.db_path = db_path
        
        self.window = tk.Toplevel()
        self.window.title("⚙️ Настройки Poster API")
        self.window.geometry("700x600")
        
        self.create_widgets()
        self.load_settings()
        self.load_sync_history()
    
    def create_widgets(self):
        """Создать интерфейс"""
        
        # Заголовок
        header = ttk.Label(self.window, text="📡 ИНТЕГРАЦИЯ С POSTER", 
                          font=('Arial', 16, 'bold'))
        header.pack(pady=20)
        
        # Основная форма
        form_frame = ttk.LabelFrame(self.window, text="Настройки API", padding=20)
        form_frame.pack(fill='x', padx=20, pady=10)
        
        # API Token
        ttk.Label(form_frame, text="API Token:").grid(row=0, column=0, sticky='w', pady=5)
        self.token_var = tk.StringVar()
        token_entry = ttk.Entry(form_frame, textvariable=self.token_var, width=50, show='*')
        token_entry.grid(row=0, column=1, pady=5, sticky='ew')
        
        ttk.Button(form_frame, text="👁️", width=3, 
                  command=lambda: token_entry.config(show='' if token_entry.cget('show') == '*' else '*')
                  ).grid(row=0, column=2, padx=5)
        
        # API URL
        ttk.Label(form_frame, text="API URL:").grid(row=1, column=0, sticky='w', pady=5)
        self.url_var = tk.StringVar(value='https://joinposter.com/api/')
        ttk.Entry(form_frame, textvariable=self.url_var, width=50).grid(row=1, column=1, pady=5, sticky='ew')
        
        # Supplier ID
        ttk.Label(form_frame, text="Supplier ID:").grid(row=2, column=0, sticky='w', pady=5)
        self.supplier_var = tk.StringVar(value='1')
        ttk.Entry(form_frame, textvariable=self.supplier_var, width=20).grid(row=2, column=1, pady=5, sticky='w')
        
        # Storage ID
        ttk.Label(form_frame, text="Storage ID:").grid(row=3, column=0, sticky='w', pady=5)
        self.storage_var = tk.StringVar(value='1')
        ttk.Entry(form_frame, textvariable=self.storage_var, width=20).grid(row=3, column=1, pady=5, sticky='w')
        
        # Интервал синхронизации
        ttk.Label(form_frame, text="Синхронизация каждые:").grid(row=4, column=0, sticky='w', pady=5)
        interval_frame = ttk.Frame(form_frame)
        interval_frame.grid(row=4, column=1, sticky='w')
        
        self.interval_var = tk.IntVar(value=6)
        ttk.Spinbox(interval_frame, from_=1, to=24, textvariable=self.interval_var, 
                   width=10).pack(side='left')
        ttk.Label(interval_frame, text="часов").pack(side='left', padx=5)
        
        # Активность
        self.active_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(form_frame, text="✅ Включить автоматическую синхронизацию", 
                       variable=self.active_var).grid(row=5, column=0, columnspan=2, pady=10, sticky='w')
        
        form_frame.columnconfigure(1, weight=1)
        
        # Кнопки управления
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(btn_frame, text="💾 Сохранить", 
                  command=self.save_settings).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Синхронизировать сейчас", 
                  command=self.sync_now).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🧪 Тест подключения", 
                  command=self.test_connection).pack(side='left', padx=5)
        
        # История синхронизации
        history_frame = ttk.LabelFrame(self.window, text="📊 История синхронизации", padding=10)
        history_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        cols = ('Дата', 'Добавлено', 'Обновлено', 'Деактивировано', 'Статус')
        self.history_tree = ttk.Treeview(history_frame, columns=cols, show='headings', height=8)
        
        for col in cols:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(history_frame, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Статус
        self.status_label = ttk.Label(self.window, text="", font=('Arial', 9, 'italic'))
        self.status_label.pack(pady=10)
    
    def load_settings(self):
        """Загрузить настройки из БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT api_token, api_url, supplier_id, storage_id, 
                   sync_interval_hours, is_active, last_sync_at
            FROM poster_settings
            WHERE id = 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            token, url, supplier, storage, interval, is_active, last_sync = row
            
            if token and token != 'YOUR_TOKEN_HERE':
                self.token_var.set(token)
            
            self.url_var.set(url or 'https://joinposter.com/api/')
            self.supplier_var.set(supplier or '1')
            self.storage_var.set(storage or '1')
            self.interval_var.set(interval or 6)
            self.active_var.set(bool(is_active))
            
            if last_sync:
                self.status_label.config(text=f"Последняя синхронизация: {last_sync}")
    
    def load_sync_history(self):
        """Загрузить историю синхронизации"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT sync_date, items_added, items_updated, items_deactivated, status
            FROM poster_sync_logs
            ORDER BY sync_date DESC
            LIMIT 20
        """)
        
        for row in cursor.fetchall():
            date, added, updated, deactivated, status = row
            status_emoji = '✅' if status == 'success' else '❌'
            self.history_tree.insert('', 'end', values=(
                date, added, updated, deactivated, status_emoji
            ))
        
        conn.close()
    
    def save_settings(self):
        """Сохранить настройки"""
        token = self.token_var.get().strip()
        
        if not token:
            messagebox.showerror("Ошибка", "API Token обязателен!")
            return
        
        if self.active_var.get() and token == 'YOUR_TOKEN_HERE':
            messagebox.showerror("Ошибка", "Укажите настоящий API Token!")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE poster_settings
                SET api_token = ?,
                    api_url = ?,
                    supplier_id = ?,
                    storage_id = ?,
                    sync_interval_hours = ?,
                    is_active = ?
                WHERE id = 1
            """, (
                token,
                self.url_var.get(),
                self.supplier_var.get(),
                self.storage_var.get(),
                self.interval_var.get(),
                1 if self.active_var.get() else 0
            ))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Настройки сохранены!\n\n"
                                         "Синхронизация начнётся автоматически.")
            
            # Перезапустить scheduler
            try:
                from poster_scheduler import get_scheduler
                scheduler = get_scheduler(self.db_path)
                scheduler.stop()
                if self.active_var.get():
                    scheduler.start()
            except:
                pass
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")
    
    def test_connection(self):
        """Тест подключения к Poster"""
        token = self.token_var.get().strip()
        url = self.url_var.get().strip()
        
        if not token or token == 'YOUR_TOKEN_HERE':
            messagebox.showerror("Ошибка", "Укажите API Token!")
            return
        
        try:
            import requests
            
            self.status_label.config(text="🔄 Проверка подключения...")
            self.window.update()
            
            response = requests.get(
                f"{url}menu.getIngredients",
                params={'token': token},
                timeout=10
            )
            
            data = response.json()
            
            if data.get('response'):
                count = len(data['response'])
                messagebox.showinfo("Успех", 
                    f"✅ Подключение успешно!\n\n"
                    f"Найдено ингредиентов: {count}")
                self.status_label.config(text="✅ Подключение работает")
            else:
                raise Exception("Неверный ответ от API")
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"❌ Не удалось подключиться:\n\n{e}")
            self.status_label.config(text="❌ Ошибка подключения")
    
    def sync_now(self):
        """Запустить синхронизацию сейчас"""
        if not self.token_var.get() or self.token_var.get() == 'YOUR_TOKEN_HERE':
            messagebox.showerror("Ошибка", "Сначала настройте и сохраните API Token!")
            return
        
        try:
            self.status_label.config(text="🔄 Синхронизация...")
            self.window.update()
            
            syncer = PosterSync(self.db_path)
            added, updated, deactivated = syncer.sync_categories()
            
            messagebox.showinfo("Успех", 
                f"✅ Синхронизация завершена!\n\n"
                f"Добавлено: {added}\n"
                f"Обновлено: {updated}\n"
                f"Деактивировано: {deactivated}")
            
            self.status_label.config(text=f"✅ Последняя синхронизация: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.load_sync_history()
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"❌ Ошибка синхронизации:\n\n{e}")
            self.status_label.config(text="❌ Ошибка синхронизации")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = PosterSettingsWindow()
    root.mainloop()
