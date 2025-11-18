#!/usr/bin/env python3
"""
Scheduler для автоматической синхронизации с Poster
Запускается на Railway как фоновый процесс
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import sqlite3
from datetime import datetime
import time
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PosterScheduler:
    """Планировщик синхронизации с Poster"""
    
    def __init__(self, db_path='finance_v5.db'):
        self.db_path = db_path
        self.scheduler = BackgroundScheduler()
        self.sync_job = None
    
    def get_sync_interval(self) -> int:
        """Получить интервал синхронизации из БД (в часах)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sync_interval_hours 
                FROM poster_settings 
                WHERE is_active = 1
                LIMIT 1
            """)
            row = cursor.fetchone()
            conn.close()
            
            return row[0] if row else 6  # По умолчанию 6 часов
        except:
            return 6
    
    def is_poster_enabled(self) -> bool:
        """Проверить включена ли синхронизация"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT is_active, api_token 
                FROM poster_settings 
                WHERE is_active = 1
                LIMIT 1
            """)
            row = cursor.fetchone()
            conn.close()
            
            if row and row[1] and row[1] != 'YOUR_TOKEN_HERE':
                return True
            return False
        except:
            return False
    
    def sync_task(self):
        """Задача синхронизации"""
        if not self.is_poster_enabled():
            logger.info("⏸️ Poster синхронизация отключена")
            return
        
        logger.info("🔄 Запуск синхронизации с Poster...")
        
        try:
            from sync_poster import sync_now
            added, updated, deactivated = sync_now()
            logger.info(f"✅ Синхронизация завершена: +{added} ~{updated} -{deactivated}")
        except Exception as e:
            logger.error(f"❌ Ошибка синхронизации: {e}")
    
    def start(self):
        """Запустить планировщик"""
        if not self.is_poster_enabled():
            logger.warning("⚠️ Poster не настроен, планировщик не запущен")
            return
        
        interval_hours = self.get_sync_interval()
        
        # Добавляем задачу с интервалом
        self.sync_job = self.scheduler.add_job(
            self.sync_task,
            trigger=IntervalTrigger(hours=interval_hours),
            id='poster_sync',
            name='Poster API Sync',
            replace_existing=True
        )
        
        # Первая синхронизация сразу
        self.scheduler.add_job(
            self.sync_task,
            trigger='date',
            run_date=datetime.now(),
            id='poster_sync_initial',
            name='Initial Poster Sync'
        )
        
        self.scheduler.start()
        logger.info(f"🚀 Планировщик запущен: синхронизация каждые {interval_hours} часов")
    
    def stop(self):
        """Остановить планировщик"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("⏹️ Планировщик остановлен")
    
    def run_now(self):
        """Запустить синхронизацию прямо сейчас"""
        self.sync_task()


# Глобальный экземпляр
_scheduler = None


def get_scheduler(db_path='finance_v5.db') -> PosterScheduler:
    """Получить синглтон планировщика"""
    global _scheduler
    if _scheduler is None:
        _scheduler = PosterScheduler(db_path)
    return _scheduler


def start_scheduler():
    """Запустить планировщик (вызывать при старте приложения)"""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler():
    """Остановить планировщик"""
    scheduler = get_scheduler()
    scheduler.stop()


def sync_now_manual():
    """Ручная синхронизация"""
    scheduler = get_scheduler()
    scheduler.run_now()


if __name__ == "__main__":
    # Для тестирования
    logger.info("🧪 Тестовый запуск scheduler...")
    
    scheduler = get_scheduler()
    scheduler.start()
    
    try:
        # Работаем бесконечно
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("\n⏹️ Остановка...")
        scheduler.stop()
