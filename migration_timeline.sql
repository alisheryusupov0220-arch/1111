-- Миграция: создание таблицы Timeline для единой ленты событий

-- 1. Создаём таблицу timeline (главная лента событий)
CREATE TABLE IF NOT EXISTS timeline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('expense', 'income', 'sale', 'payment', 'salary')),
    category_id INTEGER,
    account_id INTEGER,
    amount REAL NOT NULL,
    description TEXT,
    user_id INTEGER,
    report_id INTEGER,
    payment_method_id INTEGER,
    source TEXT DEFAULT 'desktop',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES expense_categories(id),
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (report_id) REFERENCES daily_reports(id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id)
);

-- 2. Создаём таблицу projects (для мультипроекта в будущем)
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 3. Добавляем колонку project_id в timeline (опционально)
ALTER TABLE timeline ADD COLUMN project_id INTEGER DEFAULT NULL;
-- FOREIGN KEY (project_id) REFERENCES projects(id) - добавим позже если нужно

-- 4. Создаём VIEW для удобного просмотра
CREATE VIEW IF NOT EXISTS timeline_view AS
SELECT 
    t.id,
    t.date,
    t.type,
    t.amount,
    t.description,
    t.source,
    t.created_at,
    COALESCE(ec.name, 'Без категории') as category_name,
    a.name as account_name,
    a.account_type,
    u.full_name as user_name,
    u.role as user_role,
    pm.name as payment_method_name,
    dr.report_date as report_date,
    l.name as location_name
FROM timeline t
LEFT JOIN expense_categories ec ON t.category_id = ec.id
LEFT JOIN accounts a ON t.account_id = a.id
LEFT JOIN users u ON t.user_id = u.id
LEFT JOIN payment_methods pm ON t.payment_method_id = pm.id
LEFT JOIN daily_reports dr ON t.report_id = dr.id
LEFT JOIN locations l ON dr.location_id = l.id;

-- 5. Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_timeline_date ON timeline(date);
CREATE INDEX IF NOT EXISTS idx_timeline_type ON timeline(type);
CREATE INDEX IF NOT EXISTS idx_timeline_user ON timeline(user_id);
CREATE INDEX IF NOT EXISTS idx_timeline_report ON timeline(report_id);
CREATE INDEX IF NOT EXISTS idx_timeline_account ON timeline(account_id);

-- 6. Обновляем таблицу users (если нужно добавить role и full_name)
-- Проверяем наличие колонок
-- Если их нет, они уже должны быть в таблице users

SELECT 'Миграция Timeline завершена!' as result;

