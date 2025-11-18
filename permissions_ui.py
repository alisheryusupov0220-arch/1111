#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from permissions_manager import permissions


class PermissionsWindow:
    def __init__(self, parent, db, current_user_id):
        self.parent, self.db, self.db_path = parent, db, "finance_v5.db"
        self.operator_user_id = current_user_id
        self.selected_user_id = None
        self.permission_checkboxes = {}

        self.window = tk.Toplevel(parent)
        self.window.title("👥 Управление правами")
        self.window.geometry("1200x700")
        self._create_ui()
        self._load_users()

    def _create_ui(self):
        # Заголовок
        header = ttk.Frame(self.window, padding=20)
        header.pack(fill=tk.X)
        ttk.Label(header, text="👥 Управление пользователями", font=("Arial", 16, "bold")).pack()

        # Split панель
        paned = ttk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ЛЕВАЯ: Список пользователей
        left = ttk.Frame(paned, padding=10)
        paned.add(left, weight=1)

        ttk.Label(left, text="📋 Пользователи", font=("Arial", 12, "bold")).pack()
        ttk.Button(left, text="➕ Добавить", command=self._add_user).pack()

        # Таблица
        vsb = ttk.Scrollbar(left)
        self.users_tree = ttk.Treeview(
            left, columns=("id", "username", "telegram_id"), show="headings", yscrollcommand=vsb.set
        )
        self.users_tree.heading("id", text="ID")
        self.users_tree.heading("username", text="Имя")
        self.users_tree.heading("telegram_id", text="Telegram")
        self.users_tree.column("id", width=40)
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        vsb.config(command=self.users_tree.yview)

        self.users_tree.bind("<<TreeviewSelect>>", self._on_user_select)

        ttk.Button(left, text="📋 Применить шаблон", command=self._apply_template).pack()

        # ПРАВАЯ: Права
        right = ttk.Frame(paned, padding=10)
        paned.add(right, weight=2)

        self.rights_header = ttk.Label(right, text="Выберите пользователя", font=("Arial", 12, "bold"))
        self.rights_header.pack()

        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        self._create_permissions_tabs()

        btn_frame = ttk.Frame(right)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="✅ Сохранить", command=self._save_permissions).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self._reload_permissions).pack(side=tk.RIGHT, padx=5)

        ttk.Button(self.window, text="❌ Закрыть", command=self.window.destroy).pack(pady=5)

    def _create_permissions_tabs(self):
        cat_names = {"finance": "💰 Финансы", "view": "👁️ Просмотр", "settings": "⚙️ Настройки", "admin": "🔐 Админ"}

        for cat, perms in permissions.get_permissions_by_category().items():
            frame = ttk.Frame(self.notebook, padding=20)
            self.notebook.add(frame, text=cat_names.get(cat, cat))

            for p in perms:
                var = tk.BooleanVar()
                ttk.Checkbutton(frame, text=p["display_name"], variable=var).pack(anchor="w")
                if p["description"]:
                    ttk.Label(
                        frame, text=f"   {p['description']}", foreground="gray", font=("Arial", 9)
                    ).pack(anchor="w")
                self.permission_checkboxes[p["name"]] = {"var": var, "id": p["id"]}

    def _load_users(self):
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        conn = sqlite3.connect(self.db_path)
        for row in conn.execute("SELECT id, username, telegram_id FROM users WHERE is_active=1 ORDER BY username"):
            self.users_tree.insert("", "end", values=row)
        conn.close()

    def _on_user_select(self, _event):
        sel = self.users_tree.selection()
        if not sel:
            return
        vals = self.users_tree.item(sel[0])["values"]
        self.selected_user_id = vals[0]
        self.rights_header.config(text=f"Права: {vals[1]}")
        self._load_user_permissions()

    def _load_user_permissions(self):
        if not self.selected_user_id:
            return
        user_perms = {p["name"] for p in permissions.get_user_permissions(self.selected_user_id)}
        for name, data in self.permission_checkboxes.items():
            data["var"].set(name in user_perms)

    def _reload_permissions(self):
        if self.selected_user_id:
            self._load_user_permissions()

    def _save_permissions(self):
        if not self.selected_user_id:
            messagebox.showwarning("Внимание", "Выберите пользователя!")
            return

        checked = [name for name, data in self.permission_checkboxes.items() if data["var"].get()]
        current = {p["name"] for p in permissions.get_user_permissions(self.selected_user_id)}

        to_grant = set(checked) - current
        to_revoke = current - set(checked)

        for perm_name in to_grant:
            permissions.grant_permission(self.selected_user_id, perm_name, granted_by=self.operator_user_id)
        for perm_name in to_revoke:
            permissions.revoke_permission(self.selected_user_id, perm_name)

        messagebox.showinfo("✅", f"Добавлено: {len(to_grant)}, Удалено: {len(to_revoke)}")

    def _add_user(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("➕ Добавить")
        dialog.geometry("400x200")
        dialog.transient(self.window)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Имя:").grid(row=0, column=0, sticky="w", pady=10)
        username_entry = ttk.Entry(frame, width=30)
        username_entry.grid(row=0, column=1, pady=10)

        ttk.Label(frame, text="Telegram ID:").grid(row=1, column=0, sticky="w", pady=10)
        telegram_entry = ttk.Entry(frame, width=30)
        telegram_entry.grid(row=1, column=1, pady=10)

        def save():
            username = username_entry.get().strip()
            telegram_id = telegram_entry.get().strip()
            if not username or not telegram_id:
                messagebox.showwarning("Ошибка", "Заполните поля!")
                return
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute(
                    "INSERT INTO users (username, telegram_id, is_active) VALUES (?, ?, 1)", (username, telegram_id)
                )
                conn.commit()
                conn.close()
                messagebox.showinfo("✅", "Добавлен!")
                dialog.destroy()
                self._load_users()
            except sqlite3.IntegrityError:
                messagebox.showerror("Ошибка", "Такой ID уже есть!")

        ttk.Button(frame, text="✅ Сохранить", command=save).grid(row=2, column=0, pady=20)
        ttk.Button(frame, text="❌ Отмена", command=dialog.destroy).grid(row=2, column=1)

    def _apply_template(self):
        if not self.selected_user_id:
            messagebox.showwarning("Внимание", "Выберите пользователя!")
            return

        dialog = tk.Toplevel(self.window)
        dialog.title("📋 Шаблон")
        dialog.geometry("400x200")
        dialog.transient(self.window)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Выберите:", font=("Arial", 12, "bold")).pack()
        ttk.Label(frame, text="⚠️ Все права будут заменены!", foreground="red").pack()

        role_var = tk.StringVar()
        for template in permissions.get_role_templates():
            ttk.Radiobutton(
                frame,
                text=f"{template['display_name']}: {template['description']}",
                variable=role_var,
                value=template["name"],
            ).pack(anchor="w")

        def apply():
            if role_var.get() and permissions.apply_role_template(
                self.selected_user_id, role_var.get(), granted_by=self.operator_user_id
            ):
                messagebox.showinfo("✅", "Применено!")
                dialog.destroy()
                self._load_user_permissions()

        ttk.Button(frame, text="✅ Применить", command=apply).pack()
        ttk.Button(frame, text="❌ Отмена", command=dialog.destroy).pack()


