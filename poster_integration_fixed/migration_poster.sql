-- Миграция: добавление поддержки Poster API

-- 1. Добавляем колонки для Poster в expense_categories
ALTER TABLE expense_categories ADD COLUMN poster_id TEXT DEFAULT NULL;
ALTER TABLE expense_categories ADD COLUMN poster_type TEXT DEFAULT NULL; -- 'ingredient' или 'product'
ALTER TABLE expense_categories ADD COLUMN is_active_in_poster INTEGER DEFAULT 1;
ALTER TABLE expense_categories ADD COLUMN visible_for_cashier INTEGER DEFAULT 1;
ALTER TABLE expense_categories ADD COLUMN synced_at TIMESTAMP DEFAULT NULL;

-- 2. То же для income_categories
ALTER TABLE income_categories ADD COLUMN poster_id TEXT DEFAULT NULL;
ALTER TABLE income_categories ADD COLUMN poster_type TEXT DEFAULT NULL;
ALTER TABLE income_categories ADD COLUMN is_active_in_poster INTEGER DEFAULT 1;
ALTER TABLE income_categories ADD COLUMN visible_for_cashier INTEGER DEFAULT 1;
ALTER TABLE income_categories ADD COLUMN synced_at TIMESTAMP DEFAULT NULL;

-- 3. Таблица настроек Poster
CREATE TABLE IF NOT EXISTS poster_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_token TEXT NOT NULL,
    api_url TEXT DEFAULT 'https://joinposter.com/api/',
    supplier_id TEXT DEFAULT '1',
    storage_id TEXT DEFAULT '1',
    sync_interval_hours INTEGER DEFAULT 6,
    last_sync_at TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Таблица логов синхронизации
CREATE TABLE IF NOT EXISTS poster_sync_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sync_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    items_added INTEGER DEFAULT 0,
    items_updated INTEGER DEFAULT 0,
    items_deactivated INTEGER DEFAULT 0,
    status TEXT, -- 'success' или 'error'
    error_message TEXT,
    duration_seconds REAL
);

-- 5. Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_expense_poster_id ON expense_categories(poster_id);
CREATE INDEX IF NOT EXISTS idx_income_poster_id ON income_categories(poster_id);
CREATE INDEX IF NOT EXISTS idx_expense_cashier_visible ON expense_categories(visible_for_cashier, is_active_in_poster);

-- 6. Вставляем настройки по умолчанию (токен нужно будет настроить через UI)
INSERT INTO poster_settings (api_token, api_url, supplier_id, storage_id, sync_interval_hours, is_active) 
VALUES ('', 'https://joinposter.com/api/', '1', '1', 6, 0); -- is_active=0 пока не настроено

SELECT 'Миграция Poster завершена!' as result;
