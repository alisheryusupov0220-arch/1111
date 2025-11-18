#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Permissions System - Модуль управления правами пользователей
Telegram-like система разрешений
"""

import sqlite3
from typing import List, Dict, Optional, Tuple

class PermissionsManager:
    """Менеджер системы прав"""
    
    def __init__(self, db_path: str = "finance_v5.db"):
        self.db_path = db_path
    
    # ========================================
    # ПРОВЕРКА ПРАВ
    # ========================================
    
    def has_permission(self, user_id: int, permission_name: str) -> bool:
        """
        Проверить есть ли у пользователя право
        
        Args:
            user_id: ID пользователя
            permission_name: Системное имя права (например: 'quick_add_expense')
        
        Returns:
            True если право есть, False если нет
        
        Example:
            if permissions.has_permission(user_id, 'quick_add_expense'):
                show_button()
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 1 FROM user_permissions up
                JOIN permissions p ON up.permission_id = p.id
                JOIN users u ON up.user_id = u.id
                WHERE up.user_id = ? 
                  AND p.name = ? 
                  AND p.is_active = 1
                  AND u.is_active = 1
                LIMIT 1
            """, (user_id, permission_name))
            
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
            
        except Exception as e:
            print(f"Ошибка проверки права: {e}")
            return False
    
    def has_any_permission(self, user_id: int, permission_names: List[str]) -> bool:
        """
        Проверить есть ли хотя бы одно из прав
        
        Example:
            if permissions.has_any_permission(user_id, ['quick_add_expense', 'quick_add_income']):
                show_quick_add_button()
        """
        return any(self.has_permission(user_id, name) for name in permission_names)
    
    def has_all_permissions(self, user_id: int, permission_names: List[str]) -> bool:
        """
        Проверить есть ли все права из списка
        
        Example:
            if permissions.has_all_permissions(user_id, ['manage_users', 'manage_permissions']):
                show_admin_panel()
        """
        return all(self.has_permission(user_id, name) for name in permission_names)
    
    # ========================================
    # ПОЛУЧЕНИЕ ПРАВ
    # ========================================
    
    def get_user_permissions(self, user_id: int) -> List[Dict]:
        """
        Получить все права пользователя
        
        Returns:
            [
                {
                    'id': 1,
                    'name': 'quick_add_expense',
                    'category': 'finance',
                    'display_name': 'Быстрое добавление расходов',
                    'description': '...',
                    'granted_at': '2025-11-07 10:00:00'
                },
                ...
            ]
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    p.id,
                    p.name,
                    p.category,
                    p.display_name,
                    p.description,
                    up.granted_at,
                    up.notes
                FROM user_permissions up
                JOIN permissions p ON up.permission_id = p.id
                WHERE up.user_id = ? AND p.is_active = 1
                ORDER BY p.category, p.sort_order
            """, (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'display_name': row[3],
                    'description': row[4],
                    'granted_at': row[5],
                    'notes': row[6]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"Ошибка получения прав: {e}")
            return []
    
    def get_all_permissions(self, category: Optional[str] = None) -> List[Dict]:
        """
        Получить все доступные права в системе
        
        Args:
            category: Фильтр по категории ('finance', 'view', 'settings', 'admin')
        
        Returns:
            Список всех прав с группировкой по категориям
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if category:
                cursor.execute("""
                    SELECT id, name, category, display_name, description, sort_order
                    FROM permissions
                    WHERE is_active = 1 AND category = ?
                    ORDER BY sort_order
                """, (category,))
            else:
                cursor.execute("""
                    SELECT id, name, category, display_name, description, sort_order
                    FROM permissions
                    WHERE is_active = 1
                    ORDER BY category, sort_order
                """)
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'display_name': row[3],
                    'description': row[4],
                    'sort_order': row[5]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"Ошибка получения списка прав: {e}")
            return []
    
    def get_permissions_by_category(self) -> Dict[str, List[Dict]]:
        """
        Получить права сгруппированные по категориям
        
        Returns:
            {
                'finance': [...],
                'view': [...],
                'settings': [...],
                'admin': [...]
            }
        """
        all_perms = self.get_all_permissions()
        grouped = {}
        
        for perm in all_perms:
            category = perm['category']
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(perm)
        
        return grouped
    
    # ========================================
    # УПРАВЛЕНИЕ ПРАВАМИ
    # ========================================
    
    def grant_permission(self, user_id: int, permission_name: str, 
                        granted_by: Optional[int] = None, 
                        notes: Optional[str] = None) -> bool:
        """
        Дать право пользователю
        
        Args:
            user_id: ID пользователя
            permission_name: Системное имя права
            granted_by: ID пользователя кто даёт право
            notes: Заметки (например: "временный доступ")
        
        Returns:
            True если успешно, False если ошибка
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Получаем ID права
            cursor.execute("SELECT id FROM permissions WHERE name = ? AND is_active = 1", 
                          (permission_name,))
            perm_result = cursor.fetchone()
            
            if not perm_result:
                print(f"Право '{permission_name}' не найдено")
                conn.close()
                return False
            
            permission_id = perm_result[0]
            
            # Даём право
            cursor.execute("""
                INSERT OR IGNORE INTO user_permissions (user_id, permission_id, granted_by, notes)
                VALUES (?, ?, ?, ?)
            """, (user_id, permission_id, granted_by, notes))
            
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            
            return success
            
        except Exception as e:
            print(f"Ошибка при выдаче права: {e}")
            return False
    
    def revoke_permission(self, user_id: int, permission_name: str) -> bool:
        """
        Отобрать право у пользователя
        
        Args:
            user_id: ID пользователя
            permission_name: Системное имя права
        
        Returns:
            True если успешно, False если ошибка
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM user_permissions
                WHERE user_id = ? 
                  AND permission_id = (SELECT id FROM permissions WHERE name = ?)
            """, (user_id, permission_name))
            
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            
            return success
            
        except Exception as e:
            print(f"Ошибка при отзыве права: {e}")
            return False
    
    def grant_permissions_bulk(self, user_id: int, permission_names: List[str],
                              granted_by: Optional[int] = None) -> int:
        """
        Дать несколько прав сразу
        
        Returns:
            Количество успешно выданных прав
        """
        count = 0
        for perm_name in permission_names:
            if self.grant_permission(user_id, perm_name, granted_by):
                count += 1
        return count
    
    def revoke_all_permissions(self, user_id: int) -> bool:
        """
        Отобрать все права у пользователя
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM user_permissions WHERE user_id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Ошибка при отзыве всех прав: {e}")
            return False
    
    # ========================================
    # РАБОТА С ШАБЛОНАМИ РОЛЕЙ
    # ========================================
    
    def apply_role_template(self, user_id: int, template_name: str,
                           granted_by: Optional[int] = None) -> bool:
        """
        Применить шаблон роли к пользователю
        
        Args:
            user_id: ID пользователя
            template_name: Имя шаблона ('owner', 'manager', 'cashier')
            granted_by: Кто применяет шаблон
        
        Returns:
            True если успешно
        
        Example:
            # Сделать пользователя менеджером
            permissions.apply_role_template(user_id, 'manager', admin_id)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Получаем ID шаблона
            cursor.execute("SELECT id FROM role_templates WHERE name = ? AND is_active = 1",
                          (template_name,))
            template_result = cursor.fetchone()
            
            if not template_result:
                print(f"Шаблон '{template_name}' не найден")
                conn.close()
                return False
            
            template_id = template_result[0]
            
            # Удаляем старые права
            cursor.execute("DELETE FROM user_permissions WHERE user_id = ?", (user_id,))
            
            # Даём права по шаблону
            cursor.execute("""
                INSERT INTO user_permissions (user_id, permission_id, granted_by, notes)
                SELECT ?, permission_id, ?, 'Применён шаблон: ' || ?
                FROM role_template_permissions
                WHERE role_template_id = ?
            """, (user_id, granted_by, template_name, template_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Ошибка применения шаблона: {e}")
            return False
    
    def get_role_templates(self) -> List[Dict]:
        """Получить список доступных шаблонов ролей"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, display_name, description
                FROM role_templates
                WHERE is_active = 1
                ORDER BY id
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'display_name': row[2],
                    'description': row[3]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"Ошибка получения шаблонов: {e}")
            return []

# ========================================
# ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР
# ========================================

# Создаём глобальный экземпляр для использования в приложении
permissions = PermissionsManager()

# ========================================
# ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
# ========================================

if __name__ == "__main__":
    # Пример 1: Проверка права
    user_id = 1
    if permissions.has_permission(user_id, 'quick_add_expense'):
        print("✅ Пользователь может добавлять расходы")
    else:
        print("❌ Доступ запрещён")
    
    # Пример 2: Получить все права пользователя
    user_perms = permissions.get_user_permissions(user_id)
    print(f"\nПрава пользователя {user_id}:")
    for perm in user_perms:
        print(f"  - {perm['display_name']}")
    
    # Пример 3: Дать право
    permissions.grant_permission(user_id, 'view_analytics', granted_by=1, 
                                notes="Доступ к аналитике на неделю")
    
    # Пример 4: Применить шаблон
    permissions.apply_role_template(user_id, 'manager', granted_by=1)
    
    # Пример 5: Получить все права по категориям
    grouped = permissions.get_permissions_by_category()
    print("\nВсе права в системе:")
    for category, perms in grouped.items():
        print(f"\n📁 {category.upper()}:")
        for perm in perms:
            print(f"  - {perm['display_name']}")
