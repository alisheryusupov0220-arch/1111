#!/usr/bin/env python3
"""
Модуль управления иерархическими категориями
Поддержка неограниченной вложенности + группировка
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from database_v5 import FinanceSystemV5


class CategoryManager:
    """Менеджер категорий с иерархией"""
    
    def __init__(self, parent_db):
        self.db = parent_db
        
        # Создаём окно
        self.window = tk.Toplevel()
        self.window.title("📂 Управление категориями")
        self.window.geometry("1200x800")
        
        # Тип категорий (расходы/приходы)
        self.category_type = 'expense'
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Создать интерфейс"""
        
        # Верхняя панель
        top_frame = ttk.Frame(self.window)
        top_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(top_frame, text="📂 КАТЕГОРИИ", font=('Arial', 18, 'bold')).pack(side='left')
        
        # Переключатель типа
        type_frame = ttk.Frame(top_frame)
        type_frame.pack(side='right')
        
        self.type_var = tk.StringVar(value='expense')
        ttk.Radiobutton(type_frame, text="📤 Расходы", variable=self.type_var, 
                       value='expense', command=self.switch_type).pack(side='left', padx=5)
        ttk.Radiobutton(type_frame, text="📥 Приходы", variable=self.type_var, 
                       value='income', command=self.switch_type).pack(side='left', padx=5)
        
        # Основной контейнер (2 колонки)
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Левая часть - дерево категорий
        left_frame = ttk.LabelFrame(main_frame, text="🌳 Иерархия категорий", padding=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Дерево
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill='both', expand=True)
        
        self.tree = ttk.Treeview(tree_frame, selectmode='browse')
        self.tree.heading('#0', text='Категория')
        
        tree_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        tree_scroll.pack(side='right', fill='y')
        
        # Кнопки управления
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(btn_frame, text="➕ Добавить корневую", 
                  command=self.add_root_category).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="➕ Добавить дочернюю", 
                  command=self.add_child_category).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="✏️ Переименовать", 
                  command=self.rename_category).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="🗑️ Удалить", 
                  command=self.delete_category).pack(side='left', padx=2)
        
        # Правая часть - группы
        right_frame = ttk.LabelFrame(main_frame, text="📊 Группы для аналитики", padding=10)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Инструкция
        info = ttk.Label(right_frame, 
                        text="Группы объединяют категории для анализа\n(Food Cost, Labor Cost и т.д.)",
                        font=('Arial', 9, 'italic'))
        info.pack(pady=(0, 10))
        
        # Список групп
        groups_frame = ttk.Frame(right_frame)
        groups_frame.pack(fill='both', expand=True)
        
        cols = ('Группа', 'Категории')
        self.groups_tree = ttk.Treeview(groups_frame, columns=cols, show='headings', height=15)
        
        self.groups_tree.heading('Группа', text='Группа')
        self.groups_tree.heading('Категории', text='Категории в группе')
        self.groups_tree.column('Группа', width=150)
        self.groups_tree.column('Категории', width=300)
        
        groups_scroll = ttk.Scrollbar(groups_frame, orient='vertical', 
                                      command=self.groups_tree.yview)
        self.groups_tree.configure(yscrollcommand=groups_scroll.set)
        
        self.groups_tree.pack(side='left', fill='both', expand=True)
        groups_scroll.pack(side='right', fill='y')
        
        # Кнопки групп
        group_btn_frame = ttk.Frame(right_frame)
        group_btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(group_btn_frame, text="➕ Создать группу", 
                  command=self.create_group).pack(side='left', padx=2)
        ttk.Button(group_btn_frame, text="⚙️ Настроить", 
                  command=self.configure_group).pack(side='left', padx=2)
        ttk.Button(group_btn_frame, text="🗑️ Удалить группу", 
                  command=self.delete_group).pack(side='left', padx=2)
    
    def switch_type(self):
        """Переключить тип категорий"""
        self.category_type = self.type_var.get()
        self.load_data()
    
    def load_data(self):
        """Загрузить данные"""
        # Очистить дерево
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Загрузить категории
        categories = self.get_categories()
        
        # Построить дерево
        self.build_tree(categories)
        
        # Загрузить группы
        self.load_groups()
    
    def get_categories(self):
        """Получить категории"""
        table = 'expense_categories' if self.category_type == 'expense' else 'income_categories'
        
        query = f"""
        SELECT id, name, parent_id, level, sort_order, is_active
        FROM {table}
        ORDER BY sort_order, name
        """
        
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query)
        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return categories
    
    def build_tree(self, categories, parent_id=None, parent_item=''):
        """Построить дерево рекурсивно"""
        
        # Найти детей текущего родителя
        children = [c for c in categories if c['parent_id'] == parent_id]
        
        for cat in children:
            # Эмодзи в зависимости от уровня
            emoji = '📁' if cat['level'] == 1 else '📂' if cat['level'] == 2 else '📄'
            name = f"{emoji} {cat['name']}"
            
            # Добавить в дерево
            item_id = self.tree.insert(parent_item, 'end', text=name, 
                                       tags=(cat['id'], cat['level']))
            
            # Рекурсивно добавить детей
            self.build_tree(categories, cat['id'], item_id)
    
    def load_groups(self):
        """Загрузить группы"""
        # Очистить
        for item in self.groups_tree.get_children():
            self.groups_tree.delete(item)
        
        # Получить группы
        query = """
        SELECT id, name, description, color
        FROM category_groups
        WHERE is_active = 1
        ORDER BY sort_order
        """
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        groups = cursor.fetchall()
        
        for group in groups:
            group_id, name, desc, color = group
            
            # Получить категории в группе
            cats_query = """
            SELECT COUNT(*) 
            FROM category_group_mapping
            WHERE group_id = ? AND category_type = ?
            """
            cursor.execute(cats_query, (group_id, self.category_type))
            count = cursor.fetchone()[0]
            
            self.groups_tree.insert('', 'end', values=(name, f"{count} категорий"),
                                    tags=(group_id,))
        
        conn.close()
    
    def add_root_category(self):
        """Добавить корневую категорию"""
        name = simpledialog.askstring("Новая категория", 
                                      "Введите название категории:")
        if not name:
            return
        
        table = 'expense_categories' if self.category_type == 'expense' else 'income_categories'
        
        query = f"""
        INSERT INTO {table} (name, parent_id, level, is_active)
        VALUES (?, NULL, 1, 1)
        """
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute(query, (name,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", f"Категория '{name}' добавлена!")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def add_child_category(self):
        """Добавить дочернюю категорию"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите родительскую категорию!")
            return
        
        # Получить ID родителя
        parent_id = self.tree.item(selected[0])['tags'][0]
        parent_level = self.tree.item(selected[0])['tags'][1]
        
        name = simpledialog.askstring("Новая подкатегория", 
                                      "Введите название подкатегории:")
        if not name:
            return
        
        table = 'expense_categories' if self.category_type == 'expense' else 'income_categories'
        
        query = f"""
        INSERT INTO {table} (name, parent_id, level, is_active)
        VALUES (?, ?, ?, 1)
        """
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute(query, (name, parent_id, parent_level + 1))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", f"Подкатегория '{name}' добавлена!")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def rename_category(self):
        """Переименовать категорию"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите категорию!")
            return
        
        cat_id = self.tree.item(selected[0])['tags'][0]
        old_name = self.tree.item(selected[0])['text'].split(' ', 1)[1]  # убираем эмодзи
        
        new_name = simpledialog.askstring("Переименовать", 
                                         f"Новое название для '{old_name}':",
                                         initialvalue=old_name)
        if not new_name:
            return
        
        table = 'expense_categories' if self.category_type == 'expense' else 'income_categories'
        
        query = f"UPDATE {table} SET name = ? WHERE id = ?"
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute(query, (new_name, cat_id))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Категория переименована!")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def delete_category(self):
        """Удалить категорию"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите категорию!")
            return
        
        cat_id = self.tree.item(selected[0])['tags'][0]
        name = self.tree.item(selected[0])['text'].split(' ', 1)[1]
        
        # Проверить есть ли дети
        if self.has_children(cat_id):
            messagebox.showwarning("Внимание", 
                                  "Нельзя удалить категорию с подкатегориями!\n"
                                  "Сначала удалите дочерние категории.")
            return
        
        # Подтверждение
        if not messagebox.askyesno("Подтверждение", 
                                   f"Удалить категорию '{name}'?"):
            return
        
        table = 'expense_categories' if self.category_type == 'expense' else 'income_categories'
        
        query = f"UPDATE {table} SET is_active = 0 WHERE id = ?"
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute(query, (cat_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Категория удалена!")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def has_children(self, cat_id):
        """Проверить есть ли дочерние категории"""
        table = 'expense_categories' if self.category_type == 'expense' else 'income_categories'
        
        query = f"""
        SELECT COUNT(*) FROM {table} 
        WHERE parent_id = ? AND is_active = 1
        """
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(query, (cat_id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def create_group(self):
        """Создать новую группу"""
        name = simpledialog.askstring("Новая группа", "Название группы:")
        if not name:
            return
        
        desc = simpledialog.askstring("Описание", "Описание группы (опционально):")
        
        query = """
        INSERT INTO category_groups (name, description, is_active)
        VALUES (?, ?, 1)
        """
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute(query, (name, desc or ''))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", f"Группа '{name}' создана!")
            self.load_groups()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def configure_group(self):
        """Настроить группу (добавить категории)"""
        selected = self.groups_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите группу!")
            return
        
        group_id = self.groups_tree.item(selected[0])['tags'][0]
        group_name = self.groups_tree.item(selected[0])['values'][0]
        
        # Открыть окно настройки
        GroupConfigWindow(self.db, group_id, group_name, self.category_type, self.load_groups)
    
    def delete_group(self):
        """Удалить группу"""
        selected = self.groups_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите группу!")
            return
        
        group_id = self.groups_tree.item(selected[0])['tags'][0]
        name = self.groups_tree.item(selected[0])['values'][0]
        
        if not messagebox.askyesno("Подтверждение", f"Удалить группу '{name}'?"):
            return
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE category_groups SET is_active = 0 WHERE id = ?", 
                          (group_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Группа удалена!")
            self.load_groups()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


class GroupConfigWindow:
    """Окно настройки группы"""
    
    def __init__(self, db, group_id, group_name, category_type, callback):
        self.db = db
        self.group_id = group_id
        self.group_name = group_name
        self.category_type = category_type
        self.callback = callback
        
        self.window = tk.Toplevel()
        self.window.title(f"⚙️ Настройка группы: {group_name}")
        self.window.geometry("800x600")
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Создать интерфейс"""
        ttk.Label(self.window, text=f"Выберите категории для группы '{self.group_name}':",
                 font=('Arial', 12)).pack(pady=10)
        
        # Две колонки: доступные и выбранные
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Доступные
        left_frame = ttk.LabelFrame(main_frame, text="📋 Все категории", padding=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.available_tree = ttk.Treeview(left_frame, selectmode='extended')
        self.available_tree.heading('#0', text='Категория')
        self.available_tree.pack(fill='both', expand=True)
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(side='left', padx=10)
        
        ttk.Button(btn_frame, text="→ Добавить →", 
                  command=self.add_to_group).pack(pady=5)
        ttk.Button(btn_frame, text="← Убрать ←", 
                  command=self.remove_from_group).pack(pady=5)
        
        # Выбранные
        right_frame = ttk.LabelFrame(main_frame, text="✅ В группе", padding=10)
        right_frame.pack(side='left', fill='both', expand=True, padx=(5, 0))
        
        self.selected_tree = ttk.Treeview(right_frame, selectmode='extended')
        self.selected_tree.heading('#0', text='Категория')
        self.selected_tree.pack(fill='both', expand=True)
        
        # Кнопка закрыть
        ttk.Button(self.window, text="✅ Готово", 
                  command=self.close).pack(pady=10)
    
    def load_data(self):
        """Загрузить категории"""
        table = 'expense_categories' if self.category_type == 'expense' else 'income_categories'
        
        # Все категории
        query = f"""
        SELECT id, name, parent_id, level
        FROM {table}
        WHERE is_active = 1
        ORDER BY sort_order, name
        """
        
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query)
        all_cats = [dict(row) for row in cursor.fetchall()]
        
        # Категории в группе
        query2 = """
        SELECT category_id 
        FROM category_group_mapping
        WHERE group_id = ? AND category_type = ?
        """
        cursor.execute(query2, (self.group_id, self.category_type))
        in_group = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # Заполняем деревья
        self.build_tree(self.available_tree, all_cats, exclude=in_group)
        self.build_tree(self.selected_tree, all_cats, include=in_group)
    
    def build_tree(self, tree, categories, parent_id=None, parent_item='', 
                   exclude=None, include=None):
        """Построить дерево"""
        exclude = exclude or []
        include = include or []
        
        children = [c for c in categories if c['parent_id'] == parent_id]
        
        for cat in children:
            # Фильтрация
            if exclude and cat['id'] in exclude:
                continue
            if include and cat['id'] not in include:
                continue
            
            emoji = '📁' if cat['level'] == 1 else '📂' if cat['level'] == 2 else '📄'
            name = f"{emoji} {cat['name']}"
            
            item_id = tree.insert(parent_item, 'end', text=name, tags=(cat['id'],))
            
            self.build_tree(tree, categories, cat['id'], item_id, exclude, include)
    
    def add_to_group(self):
        """Добавить в группу"""
        selected = self.available_tree.selection()
        if not selected:
            return
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        for item in selected:
            cat_id = self.available_tree.item(item)['tags'][0]
            
            # Добавляем и всех детей рекурсивно
            self.add_category_and_children(cursor, cat_id)
        
        conn.commit()
        conn.close()
        
        self.load_data()
    
    def add_category_and_children(self, cursor, cat_id):
        """Добавить категорию и всех детей"""
        # Добавить саму категорию
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO category_group_mapping 
                (group_id, category_id, category_type)
                VALUES (?, ?, ?)
            """, (self.group_id, cat_id, self.category_type))
        except:
            pass
        
        # Найти детей
        table = 'expense_categories' if self.category_type == 'expense' else 'income_categories'
        cursor.execute(f"""
            SELECT id FROM {table} 
            WHERE parent_id = ? AND is_active = 1
        """, (cat_id,))
        
        children = cursor.fetchall()
        for child in children:
            self.add_category_and_children(cursor, child[0])
    
    def remove_from_group(self):
        """Убрать из группы"""
        selected = self.selected_tree.selection()
        if not selected:
            return
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        for item in selected:
            cat_id = self.selected_tree.item(item)['tags'][0]
            
            cursor.execute("""
                DELETE FROM category_group_mapping
                WHERE group_id = ? AND category_id = ? AND category_type = ?
            """, (self.group_id, cat_id, self.category_type))
        
        conn.commit()
        conn.close()
        
        self.load_data()
    
    def close(self):
        """Закрыть"""
        self.callback()
        self.window.destroy()


if __name__ == "__main__":
    # Тест
    db = FinanceSystemV5()
    root = tk.Tk()
    root.withdraw()
    app = CategoryManager(db)
    root.mainloop()
