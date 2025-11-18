-- Миграция БД: добавление иерархии категорий

-- 1. Добавляем колонки для иерархии в expense_categories
ALTER TABLE expense_categories ADD COLUMN parent_id INTEGER DEFAULT NULL;
ALTER TABLE expense_categories ADD COLUMN level INTEGER DEFAULT 1;
ALTER TABLE expense_categories ADD COLUMN sort_order INTEGER DEFAULT 0;

-- 2. То же для income_categories
ALTER TABLE income_categories ADD COLUMN parent_id INTEGER DEFAULT NULL;
ALTER TABLE income_categories ADD COLUMN level INTEGER DEFAULT 1;
ALTER TABLE income_categories ADD COLUMN sort_order INTEGER DEFAULT 0;

-- 3. Создаём таблицу для маппинга категорий на группы
CREATE TABLE IF NOT EXISTS category_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    color TEXT DEFAULT '#3498db',
    sort_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Таблица связи категорий с группами
CREATE TABLE IF NOT EXISTS category_group_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    category_type TEXT NOT NULL, -- 'expense' или 'income'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES category_groups(id),
    UNIQUE(group_id, category_id, category_type)
);

-- 5. Создаём стандартные группы
INSERT INTO category_groups (name, description, color, sort_order) VALUES
('Food Cost', 'Себестоимость продуктов и напитков', '#e74c3c', 1),
('Labor Cost', 'Затраты на персонал', '#3498db', 2),
('Overhead', 'Постоянные расходы', '#95a5a6', 3),
('Marketing', 'Маркетинг и реклама', '#9b59b6', 4),
('Other', 'Прочие расходы', '#34495e', 5);

-- 6. Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_expense_parent ON expense_categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_income_parent ON income_categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_group_mapping ON category_group_mapping(group_id, category_type);

SELECT 'Миграция завершена успешно!' as result;
