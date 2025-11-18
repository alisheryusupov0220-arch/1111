#!/usr/bin/env python3
"""
Тестирование API сервера
"""

import requests
import json
from datetime import datetime
import time
import subprocess
import sys

BASE_URL = "http://localhost:8000"

def test_api():
    """Тестируем все endpoints"""
    
    print("🧪 ТЕСТИРОВАНИЕ API\n")
    print("=" * 50)
    
    # 1. Проверка работы
    print("\n1️⃣ Тест: Проверка работы API")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        print("   ✅ API работает!")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False
    
    # 2. Получение точек
    print("\n2️⃣ Тест: Получение точек продаж")
    try:
        response = requests.get(f"{BASE_URL}/api/locations")
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Точек: {len(data['data'])}")
        for loc in data['data']:
            print(f"      - {loc['name']}")
        print("   ✅ Точки загружены!")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 3. Получение методов оплаты
    print("\n3️⃣ Тест: Получение методов оплаты")
    try:
        response = requests.get(f"{BASE_URL}/api/payment_methods")
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Методов: {len(data['data'])}")
        for method in data['data']:
            print(f"      - {method['name']} (комиссия {method['commission_percent']}%)")
        print("   ✅ Методы загружены!")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 4. Получение категорий расходов
    print("\n4️⃣ Тест: Получение категорий расходов")
    try:
        response = requests.get(f"{BASE_URL}/api/expense_categories")
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Категорий: {len(data['data'])}")
        for cat in data['data']:
            print(f"      - {cat['name']}")
        print("   ✅ Категории загружены!")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 5. Получение категорий приходов
    print("\n5️⃣ Тест: Получение категорий приходов")
    try:
        response = requests.get(f"{BASE_URL}/api/income_categories")
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Категорий: {len(data['data'])}")
        for cat in data['data']:
            print(f"      - {cat['name']}")
        print("   ✅ Категории загружены!")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 6. Создание отчёта (ГЛАВНЫЙ ТЕСТ!)
    print("\n6️⃣ Тест: Создание отчёта")
    try:
        report_data = {
            "report_date": "2025-10-31",
            "location_id": 1,
            "total_sales": 5000000,
            "payments": [
                {"method_id": 1, "amount": 1000000},  # Uzcard
                {"method_id": 2, "amount": 500000},   # Click
                {"method_id": 3, "amount": 3500000}   # Наличные
            ],
            "expenses": [
                {
                    "category_id": 1,
                    "amount": 100000,
                    "description": "Зарплата кассира"
                }
            ],
            "incomes": [
                {
                    "category_id": 1,
                    "amount": 50000,
                    "description": "Возврат долга"
                }
            ],
            "cash_actual": 3450000,
            "created_by": "test_user"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/create_report",
            json=report_data
        )
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("   ✅ Отчёт создан успешно!")
            print(f"   📝 ID отчёта: {result['report_id']}")
        else:
            print(f"   ⚠️ Ошибка: {result.get('detail', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print("\n" + "=" * 50)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    return True

if __name__ == "__main__":
    # Даём серверу время запуститься
    print("⏳ Ждём запуска сервера...")
    time.sleep(3)
    
    # Запускаем тесты
    test_api()
