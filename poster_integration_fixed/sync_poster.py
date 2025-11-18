#!/usr/bin/env python3
"""
Модуль синхронизации категорий с Poster API
Автоматически обновляет список ингредиентов из Poster
"""

import requests
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Tuple


class PosterSync:
    """Синхронизация с Poster API"""
    
    def __init__(self, db_path='finance_v5.db'):
        self.db_path = db_path
        self.settings = self.get_settings()
    
    def get_settings(self) -> Dict:
        """Получить настройки Poster из БД"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT api_token, api_url, supplier_id, storage_id, sync_interval_hours
                FROM poster_settings
                WHERE is_active = 1
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                print("⚠️ Poster настройки не найдены или отключены")
                return None
            
            if not row[0] or len(row[0]) < 10:
                print("⚠️ API Token не настроен или некорректен")
                return None
            
            return {
                'api_token': row[0],
                'api_url': row[1],
                'supplier_id': row[2],
                'storage_id': row[3],
                'sync_interval_hours': row[4]
            }
        except sqlite3.Error as e:
            print(f"❌ Ошибка БД: {e}")
            return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def fetch_from_poster(self, method: str, params: Dict = None) -> Dict:
        """Выполнить запрос к Poster API"""
        if not self.settings:
            raise Exception("Poster settings not configured")
        
        url = f"{self.settings['api_url']}{method}"
        params = params or {}
        params['token'] = self.settings['api_token']
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('response'):
                raise Exception(f"Invalid response from Poster: {data}")
            
            return data['response']
        
        except requests.RequestException as e:
            raise Exception(f"Poster API error: {str(e)}")
    
    def get_poster_ingredients(self) -> List[Dict]:
        """Получить все ингредиенты из Poster"""
        return self.fetch_from_poster('menu.getIngredients')
    
    def get_poster_products(self) -> List[Dict]:
        """Получить продукты типа '3' (ингредиенты) из Poster"""
        all_products = self.fetch_from_poster('menu.getProducts')
        # Фильтруем только type: "3"
        return [p for p in all_products if p.get('type') == '3']
    
    def sync_categories(self) -> Tuple[int, int, int]:
        """
        Синхронизировать категории с Poster
        Возвращает: (добавлено, обновлено, деактивировано)
        """
        if not self.settings:
            raise Exception("Poster not configured")
        
        start_time = time.time()
        added = 0
        updated = 0
        deactivated = 0
        
        try:
            # Получаем данные из Poster
            print("📡 Получение данных из Poster...")
            ingredients = self.get_poster_ingredients()
            products = self.get_poster_products()
            
            print(f"✅ Получено: {len(ingredients)} ингредиентов, {len(products)} продуктов")
            
            # Объединяем все элементы
            all_items = []
            poster_ids = set()
            
            # Ингредиенты
            for ing in ingredients:
                poster_id = str(ing['ingredient_id'])
                poster_ids.add(poster_id)
                all_items.append({
                    'poster_id': poster_id,
                    'name': ing['ingredient_name'],
                    'poster_type': 'ingredient',
                    'category_id': ing.get('category_id'),
                    'unit': ing.get('ingredient_unit', '')
                })
            
            # Продукты
            for prod in products:
                poster_id = str(prod['product_id'])
                poster_ids.add(poster_id)
                all_items.append({
                    'poster_id': poster_id,
                    'name': prod['product_name'],
                    'poster_type': 'product',
                    'ingredient_id': prod.get('ingredient_id'),
                    'unit': prod.get('unit', '')
                })
            
            # Синхронизация с БД
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Для каждого элемента из Poster
            for item in all_items:
                # Проверяем существует ли
                cursor.execute("""
                    SELECT id, name FROM expense_categories
                    WHERE poster_id = ?
                """, (item['poster_id'],))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Обновляем существующий
                    cursor.execute("""
                        UPDATE expense_categories
                        SET name = ?,
                            poster_type = ?,
                            is_active_in_poster = 1,
                            synced_at = ?
                        WHERE poster_id = ?
                    """, (
                        item['name'],
                        item['poster_type'],
                        datetime.now(),
                        item['poster_id']
                    ))
                    
                    if cursor.rowcount > 0:
                        updated += 1
                        print(f"🔄 Обновлено: {item['name']}")
                
                else:
                    # Добавляем новый
                    cursor.execute("""
                        INSERT INTO expense_categories 
                        (name, poster_id, poster_type, is_active_in_poster, 
                         visible_for_cashier, is_active, synced_at)
                        VALUES (?, ?, ?, 1, 1, 1, ?)
                    """, (
                        item['name'],
                        item['poster_id'],
                        item['poster_type'],
                        datetime.now()
                    ))
                    
                    added += 1
                    print(f"➕ Добавлено: {item['name']}")
            
            # Деактивируем то, чего нет в Poster
            cursor.execute("""
                SELECT id, name, poster_id FROM expense_categories
                WHERE poster_id IS NOT NULL
                AND is_active_in_poster = 1
            """)
            
            for row in cursor.fetchall():
                cat_id, name, poster_id = row
                if poster_id not in poster_ids:
                    cursor.execute("""
                        UPDATE expense_categories
                        SET is_active_in_poster = 0
                        WHERE id = ?
                    """, (cat_id,))
                    
                    deactivated += 1
                    print(f"⚠️ Деактивировано (удалено из Poster): {name}")
            
            # Логируем синхронизацию
            duration = time.time() - start_time
            cursor.execute("""
                INSERT INTO poster_sync_logs 
                (items_added, items_updated, items_deactivated, status, duration_seconds)
                VALUES (?, ?, ?, 'success', ?)
            """, (added, updated, deactivated, duration))
            
            # Обновляем last_sync_at
            cursor.execute("""
                UPDATE poster_settings
                SET last_sync_at = ?
                WHERE is_active = 1
            """, (datetime.now(),))
            
            conn.commit()
            conn.close()
            
            print(f"\n✅ Синхронизация завершена за {duration:.1f}с")
            print(f"   Добавлено: {added}")
            print(f"   Обновлено: {updated}")
            print(f"   Деактивировано: {deactivated}")
            
            return (added, updated, deactivated)
        
        except Exception as e:
            # Логируем ошибку
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO poster_sync_logs 
                    (status, error_message)
                    VALUES ('error', ?)
                """, (str(e),))
                conn.commit()
                conn.close()
            except:
                pass
            
            print(f"❌ Ошибка синхронизации: {e}")
            raise


def sync_now():
    """Запустить синхронизацию сейчас"""
    syncer = PosterSync()
    return syncer.sync_categories()


if __name__ == "__main__":
    print("🚀 Запуск синхронизации с Poster...")
    try:
        added, updated, deactivated = sync_now()
        print(f"\n✅ Готово! Добавлено: {added}, Обновлено: {updated}, Деактивировано: {deactivated}")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        exit(1)
