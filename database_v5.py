#!/usr/bin/env python3
"""
Система учёта финансов V5
Полная структура с дневными отчётами кассира
"""

import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional
import json

class FinanceSystemV5:
    def __init__(self, db_path: str = 'finance_v5.db'):
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.init_database()
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def init_database(self):
        cursor = self.conn.cursor()
        
        # ========== РС СЧЕТА ==========
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                account_type TEXT CHECK (account_type IN ('cash', 'bank')),
                currency TEXT DEFAULT 'UZS',
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ========== МЕТОДЫ ОПЛАТЫ ==========
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_methods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                method_type TEXT CHECK (method_type IN ('terminal', 'online', 'delivery')),
                default_account_id INTEGER,
                commission_percent REAL DEFAULT 0,
                description TEXT,
                is_visible INTEGER DEFAULT 1,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (default_account_id) REFERENCES accounts(id)
            )
        ''')
        
        # ========== ТОЧКИ ПРОДАЖ ==========
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                address TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ========== КАТЕГОРИИ (для приходов не от продаж И расходов) ==========
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER,
                category_type TEXT CHECK (category_type IN ('income', 'expense')),
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES categories(id)
            )
        ''')
        
        # ========== КАТЕГОРИИ РАСХОДОВ (упрощённая версия для GUI) ==========
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expense_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ========== ДНЕВНЫЕ ОТЧЁТЫ КАССИРА ==========
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TEXT NOT NULL,
                location_id INTEGER NOT NULL,
                total_sales REAL NOT NULL,
                cash_expected REAL,
                cash_actual REAL,
                cash_difference REAL,
                cash_breakdown TEXT,
                status TEXT DEFAULT 'open' CHECK (status IN ('open', 'closed', 'verified')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                closed_at TEXT,
                verified_by TEXT,
                verified_at TEXT,
                notes TEXT,
                FOREIGN KEY (location_id) REFERENCES locations(id),
                UNIQUE(report_date, location_id)
            )
        ''')
        
        # ========== ПРОДАЖИ ПО МЕТОДАМ ОПЛАТЫ В ОТЧЁТЕ ==========
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS report_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                payment_method_id INTEGER NOT NULL,
                account_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                commission_amount REAL,
                net_amount REAL,
                FOREIGN KEY (report_id) REFERENCES daily_reports(id) ON DELETE CASCADE,
                FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id),
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        ''')
        
        # ========== ПРИХОДЫ НЕ ОТ ПРОДАЖ ==========
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS non_sales_income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                category_id INTEGER,
                account_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                FOREIGN KEY (report_id) REFERENCES daily_reports(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        ''')
        
        # ========== РАСХОДЫ В ОТЧЁТЕ ==========
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS report_expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                category_id INTEGER,
                account_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                FOREIGN KEY (report_id) REFERENCES daily_reports(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        ''')
        
        # ========== ПОЛЬЗОВАТЕЛИ ==========
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                full_name TEXT,
                role TEXT CHECK (role IN ('owner', 'manager', 'accountant', 'cashier')),
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Индексы
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_date ON daily_reports(report_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_location ON daily_reports(location_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_report_payments ON report_payments(report_id)')
        
        self.conn.commit()
    
    # ========== СЧЕТА ==========
    
    def add_account(self, name: str, account_type: str, currency: str = 'UZS', description: str = '') -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO accounts (name, account_type, currency, description)
            VALUES (?, ?, ?, ?)
        ''', (name, account_type, currency, description))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_accounts(self, account_type: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        if account_type:
            cursor.execute('SELECT * FROM accounts WHERE is_active=1 AND account_type=? ORDER BY name', (account_type,))
        else:
            cursor.execute('SELECT * FROM accounts WHERE is_active=1 ORDER BY account_type, name')
        return [dict(row) for row in cursor.fetchall()]
    
    def update_account(self, account_id: int, name: str = None, description: str = None) -> bool:
        cursor = self.conn.cursor()
        updates = []
        params = []
        
        if name:
            updates.append('name=?')
            params.append(name)
        if description is not None:
            updates.append('description=?')
            params.append(description)
        
        if not updates:
            return False
        
        params.append(account_id)
        query = f"UPDATE accounts SET {', '.join(updates)} WHERE id=?"
        cursor.execute(query, params)
        self.conn.commit()
        return True
    
    # ========== МЕТОДЫ ОПЛАТЫ ==========
    
    def add_payment_method(self, name: str, method_type: str, default_account_id: int,
                          commission_percent: float = 0, description: str = '') -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO payment_methods (name, method_type, default_account_id, commission_percent, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, method_type, default_account_id, commission_percent, description))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_payment_methods(self, method_type: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        if method_type:
            cursor.execute('''
                SELECT pm.*, a.name as default_account_name
                FROM payment_methods pm
                LEFT JOIN accounts a ON pm.default_account_id = a.id
                WHERE pm.is_active=1 AND pm.method_type=?
                ORDER BY pm.name
            ''', (method_type,))
        else:
            cursor.execute('''
                SELECT pm.*, a.name as default_account_name
                FROM payment_methods pm
                LEFT JOIN accounts a ON pm.default_account_id = a.id
                WHERE pm.is_active=1
                ORDER BY pm.method_type, pm.name
            ''')
        return [dict(row) for row in cursor.fetchall()]
    
    def update_payment_method_default_account(self, method_id: int, account_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('UPDATE payment_methods SET default_account_id=? WHERE id=?', (account_id, method_id))
        self.conn.commit()
        return True
    
    # ========== ТОЧКИ ==========
    
    def add_location(self, name: str, address: str = '') -> int:
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO locations (name, address) VALUES (?, ?)', (name, address))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_locations(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM locations WHERE is_active=1 ORDER BY name')
        return [dict(row) for row in cursor.fetchall()]
    
    # ========== КАТЕГОРИИ ==========
    
    def add_category(self, name: str, category_type: str, parent_id: int = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO categories (name, category_type, parent_id) VALUES (?, ?, ?)',
                      (name, category_type, parent_id))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_categories(self, category_type: str = None, parent_id: int = None) -> List[Dict]:
        cursor = self.conn.cursor()
        
        query = 'SELECT * FROM categories WHERE is_active=1'
        params = []
        
        if category_type:
            query += ' AND category_type=?'
            params.append(category_type)
        
        if parent_id is not None:
            query += ' AND parent_id=?'
            params.append(parent_id)
        else:
            query += ' AND parent_id IS NULL'
        
        query += ' ORDER BY name'
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_subcategories(self, parent_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM categories WHERE parent_id=? AND is_active=1 ORDER BY name', (parent_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ========== ДНЕВНЫЕ ОТЧЁТЫ ==========
    
    def create_daily_report(self, report_date: date, location_id: int, total_sales: float,
                           created_by: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO daily_reports (report_date, location_id, total_sales, created_by)
            VALUES (?, ?, ?, ?)
        ''', (report_date.isoformat(), location_id, total_sales, created_by))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_daily_report(self, report_date: date, location_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT dr.*, l.name as location_name
            FROM daily_reports dr
            JOIN locations l ON dr.location_id = l.id
            WHERE dr.report_date=? AND dr.location_id=?
        ''', (report_date.isoformat(), location_id))
        
        result = cursor.fetchone()
        return dict(result) if result else None
    
    def add_report_payment(self, report_id: int, payment_method_id: int, account_id: int, amount: float) -> int:
        # Получаем комиссию метода
        cursor = self.conn.cursor()
        cursor.execute('SELECT commission_percent FROM payment_methods WHERE id=?', (payment_method_id,))
        method = cursor.fetchone()
        
        commission_percent = method[0] if method else 0
        commission_amount = amount * (commission_percent / 100)
        net_amount = amount - commission_amount
        
        cursor.execute('''
            INSERT INTO report_payments (report_id, payment_method_id, account_id, amount, commission_amount, net_amount)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (report_id, payment_method_id, account_id, amount, commission_amount, net_amount))
        self.conn.commit()
        return cursor.lastrowid
    
    def add_non_sales_income(self, report_id: int, account_id: int, amount: float,
                            category_id: int = None, description: str = '') -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO non_sales_income (report_id, category_id, account_id, amount, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (report_id, category_id, account_id, amount, description))
        self.conn.commit()
        return cursor.lastrowid
    
    def add_report_expense(self, report_id: int, account_id: int, amount: float,
                          category_id: int = None, description: str = '') -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO report_expenses (report_id, category_id, account_id, amount, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (report_id, category_id, account_id, amount, description))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_report_cash(self, report_id: int, cash_expected: float, cash_actual: float, cash_breakdown: dict):
        cash_difference = cash_actual - cash_expected
        
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE daily_reports 
            SET cash_expected=?, cash_actual=?, cash_difference=?, cash_breakdown=?
            WHERE id=?
        ''', (cash_expected, cash_actual, cash_difference, json.dumps(cash_breakdown), report_id))
        self.conn.commit()
    
    def close_report(self, report_id: int):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE daily_reports SET status='closed', closed_at=CURRENT_TIMESTAMP WHERE id=?
        ''', (report_id,))
        self.conn.commit()
    
    def get_report_details(self, report_id: int) -> Dict:
        """Получить полный отчёт со всеми деталями"""
        cursor = self.conn.cursor()
        
        # Основная информация
        cursor.execute('''
            SELECT dr.*, l.name as location_name
            FROM daily_reports dr
            JOIN locations l ON dr.location_id = l.id
            WHERE dr.id=?
        ''', (report_id,))
        report = dict(cursor.fetchone())
        
        # Платежи
        cursor.execute('''
            SELECT rp.*, pm.name as payment_method_name, a.name as account_name
            FROM report_payments rp
            JOIN payment_methods pm ON rp.payment_method_id = pm.id
            JOIN accounts a ON rp.account_id = a.id
            WHERE rp.report_id=?
        ''', (report_id,))
        report['payments'] = [dict(row) for row in cursor.fetchall()]
        
        # Приходы не от продаж
        cursor.execute('''
            SELECT nsi.*, c.name as category_name, a.name as account_name
            FROM non_sales_income nsi
            LEFT JOIN categories c ON nsi.category_id = c.id
            JOIN accounts a ON nsi.account_id = a.id
            WHERE nsi.report_id=?
        ''', (report_id,))
        report['non_sales_income'] = [dict(row) for row in cursor.fetchall()]
        
        # Расходы
        cursor.execute('''
            SELECT re.*, c.name as category_name, a.name as account_name
            FROM report_expenses re
            LEFT JOIN categories c ON re.category_id = c.id
            JOIN accounts a ON re.account_id = a.id
            WHERE re.report_id=?
        ''', (report_id,))
        report['expenses'] = [dict(row) for row in cursor.fetchall()]
        
        return report
    
    def get_account_balance(self) -> Dict:
        """Рассчитать балансы всех счетов"""
        cursor = self.conn.cursor()
        accounts = self.get_accounts()
        result = {}
        
        for acc in accounts:
            acc_id = acc['id']
            
            # Приходы от продаж
            cursor.execute('''
                SELECT SUM(net_amount) FROM report_payments WHERE account_id=?
            ''', (acc_id,))
            sales_income = cursor.fetchone()[0] or 0
            
            # Для кассы - добавляем наличные из отчётов
            if acc['account_type'] == 'cash':
                cursor.execute('''
                    SELECT SUM(cash_actual) FROM daily_reports
                ''')
                cash_from_reports = cursor.fetchone()[0] or 0
                sales_income += cash_from_reports
            
            # Приходы не от продаж
            cursor.execute('''
                SELECT SUM(amount) FROM non_sales_income WHERE account_id=?
            ''', (acc_id,))
            non_sales = cursor.fetchone()[0] or 0
            
            # Расходы
            cursor.execute('''
                SELECT SUM(amount) FROM report_expenses WHERE account_id=?
            ''', (acc_id,))
            expenses = cursor.fetchone()[0] or 0
            
            balance = sales_income + non_sales - expenses
            
            result[acc_id] = {
                'name': acc['name'],
                'type': acc['account_type'],
                'balance': balance,
                'sales_income': sales_income,
                'non_sales_income': non_sales,
                'expenses': expenses
            }
        
        return result
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    # ========== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ УПРАВЛЕНИЯ ==========
    
    def add_payment_method(self, name: str, method_type: str, commission: float, account_id: int):
        """Добавить метод оплаты"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO payment_methods (name, method_type, commission_percent, default_account_id)
            VALUES (?, ?, ?, ?)
        ''', (name, method_type, commission, account_id))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_payment_method(self, method_id: int, name: str, method_type: str, 
                            commission: float, account_id: int, is_active: bool = True):
        """Обновить метод оплаты"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE payment_methods 
            SET name=?, method_type=?, commission_percent=?, default_account_id=?, is_active=?
            WHERE id=?
        ''', (name, method_type, commission, account_id, is_active, method_id))
        self.conn.commit()
    
    def delete_payment_method(self, method_id: int):
        """Удалить метод оплаты (мягкое удаление)"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE payment_methods SET is_active=0 WHERE id=?', (method_id,))
        self.conn.commit()
    
    def toggle_payment_method_visibility(self, method_id: int, is_visible: bool):
        """Переключить видимость метода оплаты в отчётах"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE payment_methods SET is_visible=? WHERE id=?', (is_visible, method_id))
        self.conn.commit()
    
    def get_payment_method(self, method_id: int) -> dict:
        """Получить один метод оплаты"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT pm.id, pm.name, pm.method_type, pm.commission_percent, 
                   pm.default_account_id, pm.is_visible, pm.is_active, a.name as account_name
            FROM payment_methods pm
            LEFT JOIN accounts a ON pm.default_account_id = a.id
            WHERE pm.id = ?
        ''', (method_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return dict(row)
    
    def add_location(self, name: str, address: str = ''):
        """Добавить точку продаж"""
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO locations (name, address) VALUES (?, ?)', (name, address))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_location(self, location_id: int, name: str, address: str = '', is_active: bool = True):
        """Обновить точку"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE locations SET name=?, address=?, is_active=? WHERE id=?
        ''', (name, address, is_active, location_id))
        self.conn.commit()
    
    def delete_location(self, location_id: int):
        """Удалить точку (мягкое удаление)"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE locations SET is_active=0 WHERE id=?', (location_id,))
        self.conn.commit()
    
    def add_account(self, name: str, account_type: str, initial_balance: float = 0):
        """Добавить счёт"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO accounts (name, account_type) VALUES (?, ?)
        ''', (name, account_type))
        account_id = cursor.lastrowid
        self.conn.commit()
        return account_id
    
    def update_account(self, account_id: int, name: str, account_type: str, is_active: bool = True):
        """Обновить счёт"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE accounts SET name=?, account_type=?, is_active=? WHERE id=?
        ''', (name, account_type, is_active, account_id))
        self.conn.commit()
    
    def delete_account(self, account_id: int):
        """Удалить счёт (мягкое удаление)"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE accounts SET is_active=0 WHERE id=?', (account_id,))
        self.conn.commit()
    
    def add_expense_category(self, name: str, description: str = ''):
        """Добавить категорию расходов"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO expense_categories (name, description) VALUES (?, ?)
        ''', (name, description))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_expense_category(self, category_id: int, name: str, description: str = '', is_active: bool = True):
        """Обновить категорию"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE expense_categories SET name=?, description=?, is_active=? WHERE id=?
        ''', (name, description, is_active, category_id))
        self.conn.commit()
    
    def delete_expense_category(self, category_id: int):
        """Удалить категорию (мягкое удаление)"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE expense_categories SET is_active=0 WHERE id=?', (category_id,))
        self.conn.commit()
    
    def get_expense_categories(self) -> list:
        """Получить все категории расходов"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, description, is_active 
            FROM expense_categories 
            WHERE is_active = 1
            ORDER BY name
        ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_reports(self, limit: int = 50, location_id: int = None) -> list:
        """Получить список отчётов"""
        cursor = self.conn.cursor()
        
        query = '''
            SELECT dr.id, dr.report_date, l.name as location, dr.total_sales, 
                   dr.cash_expected, dr.cash_actual, dr.cash_difference, dr.status, dr.created_by
            FROM daily_reports dr
            LEFT JOIN locations l ON dr.location_id = l.id
        '''
        
        params = []
        if location_id:
            query += ' WHERE dr.location_id = ?'
            params.append(location_id)
        
        query += ' ORDER BY dr.report_date DESC, dr.id DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        
        return [dict(row) for row in cursor.fetchall()]

