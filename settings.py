#!/usr/bin/env python3
"""
Менеджер настроек - чтение/запись config.json
Централизованное управление всеми параметрами
"""

import json
import os
from typing import Any, Dict

class ConfigManager:
    """Управление конфигурацией"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Загрузить конфиг"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Конфиг не найден: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_config(self):
        """Сохранить конфиг"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Получить значение по пути (через точку)
        Пример: config.get('telegram.bot_token')
        """
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, path: str, value: Any):
        """
        Установить значение по пути
        Пример: config.set('telegram.bot_token', 'new_token')
        """
        keys = path.split('.')
        target = self.config
        
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        target[keys[-1]] = value
    
    def get_section(self, section: str) -> Dict:
        """Получить целый раздел"""
        return self.config.get(section, {})
    
    # ========== БЫСТРЫЙ ДОСТУП К ЧАСТЫМ НАСТРОЙКАМ ==========
    
    @property
    def bot_token(self) -> str:
        """Telegram bot token"""
        return self.get('telegram.bot_token', '')
    
    @bot_token.setter
    def bot_token(self, value: str):
        self.set('telegram.bot_token', value)
    
    @property
    def db_path(self) -> str:
        """Путь к базе данных"""
        return self.get('database.path', 'finance_v5.db')
    
    @property
    def telegram_enabled(self) -> bool:
        """Telegram бот включён"""
        return self.get('telegram.enabled', False)
    
    @property
    def group_payments(self) -> bool:
        """Группировать методы оплаты"""
        return self.get('payment_methods.group_by_type', False)
    
    @property
    def require_cash_count(self) -> bool:
        """Требовать подсчёт наличных"""
        return self.get('reports.require_cash_count', True)
    
    @property
    def warn_threshold(self) -> float:
        """Порог предупреждения о расхождении (%)"""
        return self.get('reports.warn_threshold_percent', 5.0)
    
    @property
    def decimal_places(self) -> int:
        """Количество знаков после запятой"""
        return self.get('ui.decimal_places', 0)
    
    def is_method_enabled(self, method_type: str) -> bool:
        """Проверить включён ли метод оплаты"""
        return self.get(f'payment_methods.enabled_methods.{method_type}', True)
    
    def get_payment_order(self) -> list:
        """Порядок отображения методов оплаты"""
        return self.get('payment_methods.show_order', ['terminal', 'online', 'delivery'])
    
    # ========== ВАЛИДАЦИЯ ==========
    
    def validate(self) -> tuple[bool, list]:
        """
        Проверить корректность конфига
        Возвращает: (valid, errors)
        """
        errors = []
        
        # Проверка токена
        if self.telegram_enabled and not self.bot_token:
            errors.append("Telegram включён, но токен не указан")
        
        # Проверка БД
        if not self.db_path:
            errors.append("Не указан путь к базе данных")
        
        # Проверка порога
        if not (0 <= self.warn_threshold <= 100):
            errors.append("Порог предупреждения должен быть 0-100%")
        
        return len(errors) == 0, errors
    
    # ========== ЭКСПОРТ/ИМПОРТ ==========
    
    def export_to_file(self, filepath: str):
        """Экспорт конфига в файл"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def import_from_file(self, filepath: str):
        """Импорт конфига из файла"""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.save_config()
    
    def reset_to_defaults(self):
        """Сброс к настройкам по умолчанию"""
        # Сохраняем только токен и путь к БД
        token = self.bot_token
        db = self.db_path
        
        # Загружаем дефолтный конфиг
        self._load_config()
        
        # Восстанавливаем важные данные
        self.bot_token = token
        self.set('database.path', db)
        
        self.save_config()


# Глобальный экземпляр для использования во всём проекте
config = ConfigManager()


if __name__ == '__main__':
    # Тест
    print("📋 Текущие настройки:")
    print(f"Bot Token: {config.bot_token[:20]}...")
    print(f"DB Path: {config.db_path}")
    print(f"Telegram: {'✅' if config.telegram_enabled else '❌'}")
    print(f"Group Payments: {'✅' if config.group_payments else '❌'}")
    print(f"Warn Threshold: {config.warn_threshold}%")
    
    print("\n🔍 Валидация:")
    valid, errors = config.validate()
    if valid:
        print("✅ Конфиг корректен")
    else:
        print("❌ Ошибки:")
        for error in errors:
            print(f"  - {error}")
