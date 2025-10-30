#!/usr/bin/env python3
"""
Модуль валидации ввода
Безопасные функции для всех типов данных
"""

from datetime import datetime, date
from typing import Optional, List

def safe_float(prompt: str, min_value: float = None, max_value: float = None, allow_zero: bool = True) -> Optional[float]:
    """Безопасный ввод числа с плавающей точкой"""
    while True:
        value = input(prompt).strip()
        
        if not value:
            return None
        
        try:
            num = float(value)
            
            if not allow_zero and num == 0:
                print("❌ Значение не может быть нулём")
                continue
            
            if min_value is not None and num < min_value:
                print(f"❌ Значение должно быть >= {min_value}")
                continue
            
            if max_value is not None and num > max_value:
                print(f"❌ Значение должно быть <= {max_value}")
                continue
            
            return num
        
        except ValueError:
            print("❌ Введите корректное число!")

def safe_int(prompt: str, min_value: int = None, max_value: int = None, valid_values: List[int] = None) -> Optional[int]:
    """Безопасный ввод целого числа"""
    while True:
        value = input(prompt).strip()
        
        if not value:
            return None
        
        try:
            num = int(value)
            
            if valid_values and num not in valid_values:
                print(f"❌ Выберите из: {', '.join(map(str, valid_values))}")
                continue
            
            if min_value is not None and num < min_value:
                print(f"❌ Значение должно быть >= {min_value}")
                continue
            
            if max_value is not None and num > max_value:
                print(f"❌ Значение должно быть <= {max_value}")
                continue
            
            return num
        
        except ValueError:
            print("❌ Введите целое число!")

def safe_date(prompt: str = "Введите дату (ДД.ММ.ГГГГ): ") -> Optional[date]:
    """Безопасный ввод даты"""
    while True:
        value = input(prompt).strip()
        
        if not value:
            return None
        
        try:
            return datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            print("❌ Неверный формат! Используйте ДД.ММ.ГГГГ (например: 24.10.2025)")

def safe_choice(prompt: str, choices: List[str], case_sensitive: bool = False) -> Optional[str]:
    """Безопасный выбор из списка"""
    while True:
        value = input(prompt).strip()
        
        if not value:
            return None
        
        if not case_sensitive:
            value = value.lower()
            choices_lower = [c.lower() for c in choices]
            if value in choices_lower:
                return choices[choices_lower.index(value)]
        else:
            if value in choices:
                return value
        
        print(f"❌ Выберите из: {', '.join(choices)}")

def confirm(prompt: str = "Продолжить? (да/нет): ") -> bool:
    """Подтверждение действия"""
    choice = safe_choice(prompt, ['да', 'yes', 'y', 'д', 'нет', 'no', 'n', 'н'])
    return choice in ['да', 'yes', 'y', 'д'] if choice else False
