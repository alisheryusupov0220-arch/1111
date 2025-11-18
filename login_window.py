#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Login Window - Окно входа в систему
Выбор пользователя для проверки прав
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class LoginWindow:
    """Окно входа - выбор пользователя"""
    
    def __init__(self):
        self.selected_user_id = None
        self.selected_username = None
        
        self.window = tk.Tk()
        self.window.title("🔐 Вход в систему")
        self.window.geometry("400x300")
        
        # Центрирование
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        self._create_ui()
        self._load_users()
    
    def _create_ui(self):
        """Создание интерфейса"""
        # Заголовок
        header = ttk.Frame(self.window, padding=20)
        header.pack(fill=tk.X)
        
        ttk.Label(header, text="💰 AIR WAFFLE FINANCE", 
                 font=("Arial", 16, "bold")).pack()
        ttk.Label(header, text="Выберите пользователя", 
                 font=("Arial", 10)).pack()
        
        # Список пользователей
        list_frame = ttk.Frame(self.window, padding=20)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(list_frame, text="👤 Пользователь:", 
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
        
        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(list_frame, textvariable=self.user_var,
                                      state="readonly", font=("Arial", 12),
                                      width=30)
        self.user_combo.pack(pady=10)
        
        # Кнопки
        btn_frame = ttk.Frame(self.window, padding=20)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="✅ Войти", 
                  command=self._login, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Отмена", 
                  command=self.window.quit, width=15).pack(side=tk.LEFT, padx=5)
        
        # Enter для входа
        self.window.bind('<Return>', lambda e: self._login())
    
    def _load_users(self):
        """Загрузка пользователей"""
        try:
            conn = sqlite3.connect("finance_v5.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, telegram_id
                FROM users
                WHERE is_active = 1
                ORDER BY username
            """)
            
            self.users = cursor.fetchall()
            conn.close()
            
            if self.users:
                user_list = [f"{row[1]} (ID: {row[2]})" for row in self.users]
                self.user_combo["values"] = user_list
                self.user_combo.current(0)
            else:
                messagebox.showerror("Ошибка", "Нет активных пользователей!")
                self.window.quit()
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей:\n{str(e)}")
            self.window.quit()
    
    def _login(self):
        """Вход"""
        selection = self.user_combo.current()
        if selection < 0:
            messagebox.showwarning("Внимание", "Выберите пользователя!")
            return
        
        user = self.users[selection]
        self.selected_user_id = user[0]
        self.selected_username = user[1]
        
        self.window.destroy()
    
    def show(self):
        """Показать окно и вернуть выбранного пользователя"""
        self.window.mainloop()
        return self.selected_user_id, self.selected_username

# Быстрая функция для использования
def select_user():
    """Показать окно выбора пользователя"""
    login = LoginWindow()
    return login.show()

if __name__ == "__main__":
    user_id, username = select_user()
    if user_id:
        print(f"Выбран пользователь: {username} (ID: {user_id})")
    else:
        print("Вход отменён")
