#!/usr/bin/env python3
"""
Скрипт для добавления категорий из Google Sheets в систему
"""

import requests

API_URL = "https://web-production-8396.up.railway.app"

# Новые категории расходов из комментариев Google Sheets
EXPENSE_CATEGORIES = [
    "Корзинка (мелкие закупки)",
    "Хавас (овощи/зелень)",
    "Пересдача",
    "Отмены заказов",
    "Долги",
    "Авансы сотрудникам",
    "Алайский рынок",
    "Доставка/Такси",
    "Доп продукты (булочки, фарш)",
    "Мороженое",
    "Недобитые чеки"
]

def add_expense_category(name):
    """Добавить категорию расходов"""
    data = {
        "name": name,
        "is_active": True
    }
    
    try:
        response = requests.post(f"{API_URL}/api/expense_categories", json=data)
        if response.status_code == 200:
            print(f"✅ Добавлено: {name}")
            return True
        else:
            print(f"❌ Ошибка для '{name}': {response.text}")
            return False
    except Exception as e:
        print(f"❌ Исключение для '{name}': {e}")
        return False

def main():
    print("🚀 ДОБАВЛЕНИЕ КАТЕГОРИЙ ИЗ GOOGLE SHEETS")
    print("="*80)
    
    success_count = 0
    
    for category in EXPENSE_CATEGORIES:
        if add_expense_category(category):
            success_count += 1
    
    print("\n" + "="*80)
    print(f"✅ Успешно добавлено: {success_count}/{len(EXPENSE_CATEGORIES)}")
    
    # Проверяем результат
    print("\n📋 СПИСОК ВСЕХ КАТЕГОРИЙ:")
    try:
        response = requests.get(f"{API_URL}/api/expense_categories")
        if response.status_code == 200:
            categories = response.json()['data']
            for i, cat in enumerate(categories, 1):
                print(f"{i:2}. {cat['name']}")
    except Exception as e:
        print(f"Ошибка получения списка: {e}")

if __name__ == "__main__":
    main()
