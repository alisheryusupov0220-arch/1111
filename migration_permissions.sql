-- =====================================================
-- МИГРАЦИЯ: Гибкая система прав (Telegram-like)
-- Дата: 2025-11-07
-- Описание: Система разрешений вместо жёстких ролей
-- =====================================================

-- ========================================
-- 1. ТАБЛИЦА ПРАВ (permissions)
-- ========================================

CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,           -- Системное имя: 'quick_add_expense'
    category TEXT NOT NULL,              -- Категория: 'finance', 'view', 'settings', 'admin'
    display_name TEXT NOT NULL,          -- Отображаемое: "Быстрое добавление расходов"
    description TEXT,                    -- Описание для пользователя
    sort_order INTEGER DEFAULT 0,        -- Порядок отображения
    is_active INTEGER DEFAULT 1,         -- Активно ли право
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- 2. СВЯЗЬ ПОЛЬЗОВАТЕЛЬ-ПРАВА
-- ========================================

CREATE TABLE IF NOT EXISTS user_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    granted_by INTEGER,                  -- Кто дал право (user_id)
    granted_at TEXT DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,                          -- Заметки (например: "временный доступ")
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id),
    
    UNIQUE(user_id, permission_id)       -- Одно право один раз
);

-- ========================================
-- 3. ИНДЕКСЫ
-- ========================================

CREATE INDEX IF NOT EXISTS idx_permissions_category ON permissions(category);
CREATE INDEX IF NOT EXISTS idx_permissions_active ON permissions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_permissions_user ON user_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_permissions_permission ON user_permissions(permission_id);

-- ========================================
-- 4. ЗАПОЛНЕНИЕ ПРАВ
-- ========================================

-- КАТЕГОРИЯ: ФИНАНСЫ (finance)
INSERT OR IGNORE INTO permissions (name, category, display_name, description, sort_order) VALUES
('create_cashier_report', 'finance', '📊 Создавать отчёты кассира', 'Создание ежедневных отчётов кассира', 1),
('quick_add_expense', 'finance', '📉 Быстрое добавление расходов', 'Добавлять расходы вне отчётов', 2),
('quick_add_income', 'finance', '📈 Быстрое добавление приходов', 'Добавлять приходы вне отчётов', 3),
('edit_operations', 'finance', '✏️ Редактировать операции', 'Изменять существующие операции', 4),
('delete_operations', 'finance', '🗑️ Удалять операции', 'Удалять операции из системы', 5);

-- КАТЕГОРИЯ: ПРОСМОТР (view)
INSERT OR IGNORE INTO permissions (name, category, display_name, description, sort_order) VALUES
('view_timeline', 'view', '📅 Просмотр Timeline', 'Видеть все операции во всех счетах', 11),
('view_own_reports', 'view', '👤 Свои отчёты', 'Просматривать свои отчёты кассира', 12),
('view_all_reports', 'view', '👥 Все отчёты', 'Просматривать отчёты всех кассиров', 13),
('view_analytics', 'view', '📊 Аналитика', 'Доступ к дашбордам и графикам', 14),
('view_balances', 'view', '💰 Балансы счетов', 'Видеть остатки на всех счетах', 15);

-- КАТЕГОРИЯ: НАСТРОЙКИ (settings)
INSERT OR IGNORE INTO permissions (name, category, display_name, description, sort_order) VALUES
('manage_categories', 'settings', '📁 Управление категориями', 'Создавать/редактировать категории', 21),
('manage_accounts', 'settings', '🏦 Управление счетами', 'Создавать/редактировать счета', 22),
('manage_payment_methods', 'settings', '💳 Методы оплаты', 'Настройка методов оплаты', 23),
('manage_locations', 'settings', '📍 Точки продаж', 'Управление точками продаж', 24),
('manage_poster', 'settings', '📡 Настройки Poster', 'Интеграция с Poster POS', 25);

-- КАТЕГОРИЯ: АДМИНИСТРИРОВАНИЕ (admin)
INSERT OR IGNORE INTO permissions (name, category, display_name, description, sort_order) VALUES
('manage_users', 'admin', '👥 Управление пользователями', 'Добавлять/удалять пользователей', 31),
('manage_permissions', 'admin', '🔐 Управление правами', 'Давать/убирать права пользователям', 32),
('view_logs', 'admin', '📋 Просмотр логов', 'Видеть историю действий системы', 33),
('system_settings', 'admin', '⚙️ Системные настройки', 'Доступ к настройкам системы', 34),
('export_data', 'admin', '📤 Экспорт данных', 'Экспортировать данные в Excel/PDF', 35);

-- ========================================
-- 5. ПРЕДСТАВЛЕНИЕ (VIEW) для удобства
-- ========================================

CREATE VIEW IF NOT EXISTS user_permissions_view AS
SELECT 
    u.id as user_id,
    u.username,
    u.telegram_id,
    p.id as permission_id,
    p.name as permission_name,
    p.category,
    p.display_name,
    p.description,
    up.granted_at,
    granted_by_user.username as granted_by_name
FROM users u
JOIN user_permissions up ON u.id = up.user_id
JOIN permissions p ON up.permission_id = p.id
LEFT JOIN users granted_by_user ON up.granted_by = granted_by_user.id
WHERE u.is_active = 1 AND p.is_active = 1
ORDER BY u.username, p.category, p.sort_order;

-- ========================================
-- 6. ФУНКЦИЯ ПРОВЕРКИ ПРАВ (через VIEW)
-- ========================================

-- Быстрая проверка права для пользователя:
-- SELECT COUNT(*) FROM user_permissions 
-- WHERE user_id = ? AND permission_id = (SELECT id FROM permissions WHERE name = ?)

-- Или через VIEW:
-- SELECT 1 FROM user_permissions_view 
-- WHERE user_id = ? AND permission_name = ? LIMIT 1

-- ========================================
-- 7. ПРЕДУСТАНОВЛЕННЫЕ ШАБЛОНЫ РОЛЕЙ
-- ========================================

-- Для удобства создаём таблицу шаблонов (необязательно, но удобно)
CREATE TABLE IF NOT EXISTS role_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,           -- 'owner', 'manager', 'cashier'
    display_name TEXT NOT NULL,          -- 'Владелец', 'Менеджер', 'Кассир'
    description TEXT,
    is_active INTEGER DEFAULT 1
);

INSERT OR IGNORE INTO role_templates (name, display_name, description) VALUES
('owner', '👑 Владелец', 'Полный доступ ко всем функциям'),
('manager', '🎯 Менеджер', 'Управление финансами и просмотр аналитики'),
('cashier', '🧾 Кассир', 'Создание отчётов кассира');

-- Связь шаблон-права
CREATE TABLE IF NOT EXISTS role_template_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_template_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    
    FOREIGN KEY (role_template_id) REFERENCES role_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    
    UNIQUE(role_template_id, permission_id)
);

-- Наполнение шаблона OWNER (все права)
INSERT OR IGNORE INTO role_template_permissions (role_template_id, permission_id)
SELECT 1, id FROM permissions WHERE is_active = 1;

-- Наполнение шаблона MANAGER
INSERT OR IGNORE INTO role_template_permissions (role_template_id, permission_id)
SELECT 2, id FROM permissions WHERE name IN (
    'quick_add_expense',
    'quick_add_income',
    'view_timeline',
    'view_all_reports',
    'view_analytics',
    'view_balances',
    'manage_categories'
);

-- Наполнение шаблона CASHIER
INSERT OR IGNORE INTO role_template_permissions (role_template_id, permission_id)
SELECT 3, id FROM permissions WHERE name IN (
    'create_cashier_report',
    'view_own_reports',
    'view_balances'
);

-- ========================================
-- 8. МИГРАЦИЯ СТАРЫХ ДАННЫХ (если есть колонка role)
-- ========================================

-- Если у тебя уже есть users с колонкой role, мигрируем:

-- Для owner - даём все права
INSERT OR IGNORE INTO user_permissions (user_id, permission_id, granted_by, notes)
SELECT 
    u.id,
    p.id,
    NULL,
    'Автомиграция из роли owner'
FROM users u
CROSS JOIN permissions p
WHERE u.role = 'owner' AND u.is_active = 1 AND p.is_active = 1;

-- Для manager - даём права по шаблону
INSERT OR IGNORE INTO user_permissions (user_id, permission_id, granted_by, notes)
SELECT 
    u.id,
    rtp.permission_id,
    NULL,
    'Автомиграция из роли manager'
FROM users u
JOIN role_template_permissions rtp ON rtp.role_template_id = 2
WHERE u.role = 'manager' AND u.is_active = 1;

-- Для cashier - даём права по шаблону
INSERT OR IGNORE INTO user_permissions (user_id, permission_id, granted_by, notes)
SELECT 
    u.id,
    rtp.permission_id,
    NULL,
    'Автомиграция из роли cashier'
FROM users u
JOIN role_template_permissions rtp ON rtp.role_template_id = 3
WHERE u.role = 'cashier' AND u.is_active = 1;

-- ========================================
-- ПРОВЕРКА
-- ========================================

-- Посмотреть все права:
-- SELECT * FROM permissions ORDER BY category, sort_order;

-- Посмотреть права пользователя:
-- SELECT * FROM user_permissions_view WHERE user_id = 1;

-- Посмотреть все права по категориям:
-- SELECT category, COUNT(*) as count FROM permissions WHERE is_active = 1 GROUP BY category;

-- ========================================
-- ИСПОЛЬЗОВАНИЕ В КОДЕ
-- ========================================

-- Python функция проверки:
/*
def has_permission(user_id, permission_name):
    conn = sqlite3.connect('finance_v5.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 1 FROM user_permissions up
        JOIN permissions p ON up.permission_id = p.id
        WHERE up.user_id = ? AND p.name = ? AND p.is_active = 1
        LIMIT 1
    ''', (user_id, permission_name))
    
    result = cursor.fetchone()
    conn.close()
    
    return result is not None

# Использование:
if has_permission(current_user_id, 'quick_add_expense'):
    # Показать кнопку "Быстрое добавление расходов"
    pass
*/

-- =====================================================
-- ГОТОВО!
-- =====================================================
