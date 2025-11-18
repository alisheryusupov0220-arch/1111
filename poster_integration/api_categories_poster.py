"""
Обновлённые API эндпоинты для работы с категориями
Добавить в api_server.py
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from datetime import datetime

router = APIRouter(prefix="/api/categories", tags=["categories"])


# ============ МОДЕЛИ ============

class Category(BaseModel):
    id: int
    name: str
    poster_id: Optional[str]
    is_active: bool
    is_active_in_poster: bool
    visible_for_cashier: bool


class ToggleVisibilityRequest(BaseModel):
    visible: bool


# ============ ЭНДПОИНТЫ ДЛЯ КАССИРА ============

@router.get("/for_cashier")
async def get_categories_for_cashier(db_path: str = 'finance_v5.db'):
    """
    Получить категории для кассира
    Только активные + видимые + есть в Poster
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, poster_id, is_active, 
                   is_active_in_poster, visible_for_cashier
            FROM expense_categories
            WHERE is_active = 1
            AND visible_for_cashier = 1
            AND (is_active_in_poster = 1 OR poster_id IS NULL)
            ORDER BY name
        """)
        
        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "success": True,
            "data": categories,
            "count": len(categories)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def get_all_categories(
    include_inactive: bool = False,
    db_path: str = 'finance_v5.db'
):
    """
    Получить все категории (для менеджера)
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT id, name, poster_id, poster_type,
                   is_active, is_active_in_poster, 
                   visible_for_cashier, synced_at
            FROM expense_categories
        """
        
        if not include_inactive:
            query += " WHERE is_active = 1"
        
        query += " ORDER BY name"
        
        cursor.execute(query)
        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "success": True,
            "data": categories,
            "count": len(categories)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{category_id}/toggle_visibility")
async def toggle_category_visibility(
    category_id: int,
    request: ToggleVisibilityRequest,
    db_path: str = 'finance_v5.db'
):
    """
    Переключить видимость категории для кассира
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE expense_categories
            SET visible_for_cashier = ?
            WHERE id = ?
        """, (1 if request.visible else 0, category_id))
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Category not found")
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Visibility updated"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/poster_status")
async def get_poster_status(db_path: str = 'finance_v5.db'):
    """
    Получить статус интеграции с Poster
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Настройки Poster
        cursor.execute("""
            SELECT is_active, last_sync_at, sync_interval_hours
            FROM poster_settings
            WHERE id = 1
        """)
        settings = cursor.fetchone()
        
        # Статистика категорий
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_active_in_poster = 1 THEN 1 ELSE 0 END) as active_in_poster,
                SUM(CASE WHEN visible_for_cashier = 1 THEN 1 ELSE 0 END) as visible_for_cashier,
                SUM(CASE WHEN poster_id IS NOT NULL THEN 1 ELSE 0 END) as from_poster
            FROM expense_categories
            WHERE is_active = 1
        """)
        stats = cursor.fetchone()
        
        # Последние логи
        cursor.execute("""
            SELECT sync_date, items_added, items_updated, 
                   items_deactivated, status
            FROM poster_sync_logs
            ORDER BY sync_date DESC
            LIMIT 5
        """)
        logs = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "success": True,
            "poster_enabled": bool(settings['is_active']) if settings else False,
            "last_sync": settings['last_sync_at'] if settings else None,
            "sync_interval_hours": settings['sync_interval_hours'] if settings else 6,
            "stats": dict(stats) if stats else {},
            "recent_logs": logs
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync_now")
async def trigger_sync_now(db_path: str = 'finance_v5.db'):
    """
    Запустить синхронизацию с Poster прямо сейчас
    """
    try:
        from sync_poster import sync_now
        
        added, updated, deactivated = sync_now()
        
        return {
            "success": True,
            "message": "Sync completed",
            "added": added,
            "updated": updated,
            "deactivated": deactivated
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ ДОБАВИТЬ В main api_server.py ============
"""
# В api_server.py добавить:

from api_categories_poster import router as categories_router

app.include_router(categories_router)

# И запустить scheduler при старте:

from poster_scheduler import start_scheduler

@app.on_event("startup")
async def startup_event():
    # Запуск Poster scheduler
    start_scheduler()
    logger.info("🚀 Poster scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    from poster_scheduler import stop_scheduler
    stop_scheduler()
    logger.info("⏹️ Poster scheduler stopped")
"""
