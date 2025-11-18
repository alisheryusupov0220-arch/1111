-- =====================================================
-- МИГРАЦИЯ: Инкасация и Переводы (ПРАВИЛЬНАЯ для SQLite)
-- Дата: 2025-11-08
-- =====================================================

-- Проверка: есть ли уже колонки?
-- PRAGMA table_info(timeline);

-- 1. Добавить новые колонки в timeline
ALTER TABLE timeline ADD COLUMN from_account_id INTEGER;
ALTER TABLE timeline ADD COLUMN to_account_id INTEGER;
ALTER TABLE timeline ADD COLUMN commission_amount REAL DEFAULT 0;

-- 2. Создать индексы
CREATE INDEX IF NOT EXISTS idx_timeline_from_account ON timeline(from_account_id);
CREATE INDEX IF NOT EXISTS idx_timeline_to_account ON timeline(to_account_id);
CREATE INDEX IF NOT EXISTS idx_timeline_type ON timeline(type);

-- 3. Добавить новые права
INSERT INTO permissions (name, category, display_name, description, sort_order, is_active) 
VALUES ('quick_incasation', 'finance', '🏦 Инкасация', 'Переводить наличные на банк.счёт', 6, 1);

INSERT INTO permissions (name, category, display_name, description, sort_order, is_active)
VALUES ('quick_transfer', 'finance', '🔄 Переводы между счетами', 'Переводить между счетами', 7, 1);

-- 4. Создать VIEW для удобного просмотра
DROP VIEW IF EXISTS timeline_extended;

CREATE VIEW timeline_extended AS
SELECT 
    t.id,
    t.date,
    t.type,
    t.amount,
    t.description,
    t.source,
    t.user_id,
    
    -- Обычный счёт
    a.name as account_name,
    a.account_type,
    
    -- Для переводов/инкасации
    from_acc.name as from_account_name,
    from_acc.account_type as from_account_type,
    to_acc.name as to_account_name,
    to_acc.account_type as to_account_type,
    
    -- Комиссия
    t.commission_amount,
    
    -- Категории
    ec.name as expense_category,
    ic.name as income_category,
    
    -- Пользователь
    u.username,
    
    t.created_at
FROM timeline t
LEFT JOIN accounts a ON t.account_id = a.id
LEFT JOIN accounts from_acc ON t.from_account_id = from_acc.id
LEFT JOIN accounts to_acc ON t.to_account_id = to_acc.id
LEFT JOIN expense_categories ec ON t.category_id = ec.id AND t.type = 'expense'
LEFT JOIN income_categories ic ON t.category_id = ic.id AND t.type = 'income'
LEFT JOIN users u ON t.user_id = u.id
ORDER BY t.date DESC, t.created_at DESC;

-- 5. Проверка результата
SELECT '=== ПРОВЕРКА МИГРАЦИИ ===' as info;

SELECT 'Колонки timeline:' as info;
PRAGMA table_info(timeline);

SELECT 'Новые права:' as info;
SELECT * FROM permissions WHERE name IN ('quick_incasation', 'quick_transfer');

SELECT 'VIEW создан:' as info;
SELECT COUNT(*) as count FROM sqlite_master WHERE type='view' AND name='timeline_extended';

SELECT '=== МИГРАЦИЯ ЗАВЕРШЕНА ===' as info;
