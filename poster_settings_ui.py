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
        self.token_entry = ttk.Entry(form_frame, textvariable=self.token_var, width=50)
        self.token_entry.grid(row=0, column=1, pady=5, sticky='ew')
        
        self.show_token_btn = ttk.Button(form_frame, text="🔒", width=3, 
                  command=self.toggle_token_visibility)
        self.show_token_btn.grid(row=0, column=2, padx=5)
        
        # Статус токена
        self.token_status_label = ttk.Label(form_frame, text="", font=('Arial', 8, 'italic'))
        self.token_status_label.grid(row=1, column=1, sticky='w')
        
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
        ttk.Button(btn_frame, text="🔍 Диагностика", 
                  command=self.run_diagnostics).pack(side='left', padx=5)
        
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
    
    def toggle_token_visibility(self):
        """Переключить видимость токена"""
        if self.token_entry.cget('show') == '':
            self.token_entry.config(show='*')
            self.show_token_btn.config(text='🔒')
        else:
            self.token_entry.config(show='')
            self.show_token_btn.config(text='👁️')
    
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
            
            # Загружаем токен (без проверки на YOUR_TOKEN_HERE)
            if token:
                self.token_var.set(token)
                # Показываем статус токена
                if len(token) > 10:
                    masked = token[:4] + '...' + token[-4:]
                    self.token_status_label.config(text=f"Сохранён: {masked}", foreground='green')
                else:
                    self.token_status_label.config(text="Токен сохранён ✓", foreground='green')
            else:
                self.token_status_label.config(text="Токен не настроен", foreground='red')
            
            self.url_var.set(url or 'https://joinposter.com/api/')
            self.supplier_var.set(supplier or '1')
            self.storage_var.set(storage or '1')
            self.interval_var.set(interval or 6)
            self.active_var.set(bool(is_active))
            
            if last_sync:
                self.status_label.config(text=f"Последняя синхронизация: {last_sync}")
        else:
            self.token_status_label.config(text="Токен не настроен", foreground='red')
    
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
        
        if len(token) < 10:
            messagebox.showerror("Ошибка", "API Token слишком короткий!\nПроверьте правильность токена.")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            is_active_value = 1 if self.active_var.get() else 0
            
            # Проверяем существует ли запись
            cursor.execute("SELECT id FROM poster_settings WHERE id = 1")
            exists = cursor.fetchone()
            
            if exists:
                # Обновляем
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
                    is_active_value
                ))
                print(f"✅ Updated settings: is_active={is_active_value}")
            else:
                # Вставляем новую запись
                cursor.execute("""
                    INSERT INTO poster_settings 
                    (id, api_token, api_url, supplier_id, storage_id, sync_interval_hours, is_active)
                    VALUES (1, ?, ?, ?, ?, ?, ?)
                """, (
                    token,
                    self.url_var.get(),
                    self.supplier_var.get(),
                    self.storage_var.get(),
                    self.interval_var.get(),
                    is_active_value
                ))
                print(f"✅ Inserted settings: is_active={is_active_value}")
            
            conn.commit()
            
            # ПРОВЕРКА что сохранилось
            cursor.execute("SELECT is_active, api_token FROM poster_settings WHERE id = 1")
            check = cursor.fetchone()
            if check:
                saved_active, saved_token = check
                print(f"✅ Verified: is_active={saved_active}, token={saved_token[:4]}...{saved_token[-4:]}")
                
                if saved_active != is_active_value:
                    messagebox.showerror("Ошибка", 
                        f"⚠️ is_active сохранился неправильно!\n"
                        f"Ожидалось: {is_active_value}\n"
                        f"Сохранилось: {saved_active}")
                    conn.close()
                    return
            
            conn.close()
            
            # Обновляем статус токена
            if len(token) > 10:
                masked = token[:4] + '...' + token[-4:]
                self.token_status_label.config(text=f"Сохранён: {masked}", foreground='green')
            
            status_msg = "✅ Настройки сохранены!\n\n"
            if is_active_value == 1:
                status_msg += "🔄 Синхронизация ВКЛЮЧЕНА\nБудет запускаться автоматически."
            else:
                status_msg += "⏸️ Синхронизация ВЫКЛЮЧЕНА\nЧтобы включить, поставьте галочку."
            
            messagebox.showinfo("Успех", status_msg)
            
            # Перезапустить scheduler
            try:
                from poster_scheduler import get_scheduler
                scheduler = get_scheduler(self.db_path)
                if scheduler:
                    scheduler.stop()
                if is_active_value == 1:
                    scheduler.start()
                    print("✅ Scheduler started")
                else:
                    print("⏸️ Scheduler stopped (is_active=0)")
            except Exception as e:
                print(f"⚠️ Scheduler restart error: {e}")
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")
            print(f"❌ Save error: {e}")
    
    def test_connection(self):
        """Тест подключения к Poster"""
        token = self.token_var.get().strip()
        url = self.url_var.get().strip()
        
        if not token:
            messagebox.showerror("Ошибка", "Укажите API Token!")
            return
        
        if len(token) < 10:
            messagebox.showerror("Ошибка", "API Token слишком короткий!")
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
                error_msg = data.get('error', 'Неверный ответ от API')
                raise Exception(error_msg)
        
        except requests.Timeout:
            messagebox.showerror("Ошибка", "❌ Превышено время ожидания.\nПроверьте интернет соединение.")
            self.status_label.config(text="❌ Timeout")
        except requests.RequestException as e:
            messagebox.showerror("Ошибка", f"❌ Ошибка сети:\n\n{e}")
            self.status_label.config(text="❌ Ошибка сети")
        except Exception as e:
            messagebox.showerror("Ошибка", f"❌ Не удалось подключиться:\n\n{e}")
            self.status_label.config(text="❌ Ошибка подключения")
    
    def run_diagnostics(self):
        """Запустить диагностику настроек"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Проверка таблицы
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='poster_settings'
            """)
            if not cursor.fetchone():
                messagebox.showerror("Ошибка",
                    "❌ Таблица poster_settings не существует!\n\n"
                    "Выполните миграцию:\n"
                    "sqlite3 finance_v5.db < migration_poster.sql")
                conn.close()
                return
            
            # Проверка данных
            cursor.execute("""
                SELECT id, api_token, api_url, supplier_id, storage_id, 
                       sync_interval_hours, is_active, last_sync_at
                FROM poster_settings
                WHERE id = 1
            """)
            row = cursor.fetchone()
            
            if not row:
                messagebox.showwarning("Диагностика",
                    "⚠️ Запись в poster_settings не найдена!\n\n"
                    "Это нормально для первой настройки.\n"
                    "Введите токен и нажмите 'Сохранить'.")
                conn.close()
                return
            
            id, token, url, supplier, storage, interval, is_active, last_sync = row
            
            # Проверка логов
            cursor.execute("SELECT COUNT(*) FROM poster_sync_logs")
            log_count = cursor.fetchone()[0]
            
            conn.close()
            
            # Формируем отчёт
            report = "🔍 ДИАГНОСТИКА POSTER API\n\n"
            
            report += f"📊 Настройки (id={id}):\n"
            report += f"  Token: {'✅ Настроен' if token and len(token) > 10 else '❌ Не настроен'}\n"
            if token and len(token) > 10:
                report += f"         ({token[:4]}...{token[-4:]})\n"
            report += f"  URL: {url or '❌ Нет'}\n"
            report += f"  Supplier: {supplier or '❌ Нет'}\n"
            report += f"  Storage: {storage or '❌ Нет'}\n"
            report += f"  Интервал: {interval or 6} часов\n"
            report += f"  Активность: {'✅ ВКЛЮЧЕНО' if is_active == 1 else '❌ ВЫКЛЮЧЕНО'}\n"
            report += f"  Последняя синхронизация:\n"
            report += f"         {last_sync or '(никогда)'}\n\n"
            
            report += f"📝 Логи синхронизации: {log_count} записей\n\n"
            
            # ГЛАВНАЯ ПРОВЕРКА
            report += "🎯 СТАТУС:\n"
            if not token or len(token) < 10:
                report += "  ❌ API Token не настроен\n"
                report += "  → Введите токен и сохраните\n"
            elif is_active != 1:
                report += "  ⚠️ Синхронизация ВЫКЛЮЧЕНА\n"
                report += "  → Поставьте галочку '✅ Включить'\n"
                report += "  → Нажмите 'Сохранить'\n"
            else:
                report += "  ✅ ВСЁ НАСТРОЕНО ПРАВИЛЬНО!\n"
                report += "  → Можно синхронизировать\n"
            
            messagebox.showinfo("Диагностика", report)
            
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"❌ Ошибка БД:\n\n{e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"❌ Ошибка диагностики:\n\n{e}")
    
    def sync_now(self):
        """Запустить синхронизацию сейчас"""
        token = self.token_var.get().strip()
        
        if not token:
            messagebox.showerror("Ошибка", 
                "❌ API Token не настроен!\n\n"
                "1. Введите API Token\n"
                "2. Нажмите 'Сохранить'\n"
                "3. Попробуйте снова")
            return
        
        if len(token) < 10:
            messagebox.showerror("Ошибка", "API Token слишком короткий!\nСохраните правильный токен.")
            return
        
        # Проверяем сохранён ли токен в БД
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT api_token, is_active FROM poster_settings WHERE id = 1")
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                messagebox.showerror("Ошибка",
                    "❌ Настройки не сохранены в БД!\n\n"
                    "Нажмите 'Сохранить' перед синхронизацией.")
                return
            
            saved_token, is_active = row
            
            # Если токен не совпадает - нужно сохранить
            if saved_token != token:
                conn.close()
                messagebox.showwarning("Внимание",
                    "⚠️ Токен изменён но не сохранён!\n\n"
                    "Нажмите 'Сохранить' чтобы применить изменения.")
                return
            
            # Если is_active = 0, временно включаем для синхронизации
            if is_active == 0:
                print("⚠️ is_active=0, временно включаем для синхронизации")
                cursor.execute("UPDATE poster_settings SET is_active = 1 WHERE id = 1")
                conn.commit()
                should_restore = True
            else:
                should_restore = False
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"❌ Ошибка проверки БД:\n{e}")
            return
        
        try:
            self.status_label.config(text="🔄 Синхронизация...")
            self.window.update()
            
            syncer = PosterSync(self.db_path)
            added, updated, deactivated = syncer.sync_categories()
            
            # Восстанавливаем is_active если нужно
            if should_restore:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE poster_settings SET is_active = 0 WHERE id = 1")
                conn.commit()
                conn.close()
                print("⚠️ Восстановлено is_active=0")
            
            messagebox.showinfo("Успех", 
                f"✅ Синхронизация завершена!\n\n"
                f"Добавлено: {added}\n"
                f"Обновлено: {updated}\n"
                f"Деактивировано: {deactivated}")
            
            self.status_label.config(text=f"✅ Последняя синхронизация: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.load_sync_history()
        
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Sync error: {error_msg}")
            
            if 'settings not configured' in error_msg.lower() or 'not found' in error_msg.lower():
                messagebox.showerror("Ошибка", 
                    "❌ Poster не настроен!\n\n"
                    "1. Проверьте что API Token введён\n"
                    "2. Нажмите 'Сохранить'\n"
                    "3. Попробуйте снова\n\n"
                    f"Детали: {error_msg}")
            else:
                messagebox.showerror("Ошибка", f"❌ Ошибка синхронизации:\n\n{error_msg}")
            
            self.status_label.config(text="❌ Ошибка синхронизации")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = PosterSettingsWindow()
    root.mainloop()
