from datetime import datetime, timedelta

# Твой импорт db_session, как и был
from database import db_session


# 1. Функция переименована в 'dashboard'
# 2. Добавлены параметры start_date/end_date
# 3. Логика дат адаптирована под .date() (как было у тебя)
# 4. Возвращаемый словарь обновлен по инструкции
# 5. Сохранена твоя логика округления .round(..., 1)
def dashboard(days: int = 30, start_date: str = None, end_date: str = None):
    if start_date and end_date:
        start_dt = datetime.fromisoformat(start_date).date()
        end_dt = datetime.fromisoformat(end_date).date()
    else:
        end_dt = datetime.now().date()
        start_dt = end_dt - timedelta(days=days)

    with db_session() as conn:
        revenue = (
            conn.execute(
                "SELECT SUM(amount) FROM timeline WHERE type='income' AND date >= ? AND date <= ?",
                (start_dt, end_dt),
            ).fetchone()[0]
            or 0
        )

        total_expenses = (
            conn.execute(
                "SELECT SUM(amount) FROM timeline WHERE type='expense' AND date >= ? AND date <= ?",
                (start_dt, end_dt),
            ).fetchone()[0]
            or 0
        )

        # Получаем все активные блоки
        blocks = conn.execute(
            "SELECT code FROM analytic_blocks WHERE is_active = 1"
        ).fetchall()

        result_data = {
            "revenue": revenue,
            "total_expenses": total_expenses,
            "profit": revenue - total_expenses,
            "profitability": round((revenue - total_expenses) / revenue * 100, 1) if revenue > 0 else 0,
        }

        # Динамически считаем данные для каждого блока
        prime_cost = 0
        for block_row in blocks:
            block_code = block_row[0]
            
            block_amount = (
                conn.execute(
                    """
                    SELECT SUM(t.amount) FROM timeline t
                    JOIN analytics_settings s ON t.category_id = s.category_id
                    WHERE t.type='expense' AND s.analytic_type = ? AND t.date >= ? AND t.date <= ?
                    """,
                    (block_code, start_dt, end_dt),
                ).fetchone()[0]
                or 0
            )
            
            block_percentage = (block_amount / revenue * 100) if revenue > 0 else 0
            
            result_data[block_code] = block_amount
            result_data[f"{block_code}_percentage"] = round(block_percentage, 1)
            
            # Для prime_cost суммируем food_cost и labor_cost
            if block_code in ['food_cost', 'labor_cost']:
                prime_cost += block_amount

        # Добавляем prime_cost только если есть оба компонента
        if 'food_cost' in result_data and 'labor_cost' in result_data:
            result_data['prime_cost'] = prime_cost
            result_data['prime_cost_percentage'] = round(
                (prime_cost / revenue * 100) if revenue > 0 else 0, 1
            )

        print("Dashboard data:", result_data)
        return result_data


# 1. Функция переименована в 'pivot_table'
# 2. Добавлены параметры start_date/end_date
# 3. Полностью заменен SQL-запрос и логика обработки по инструкции
def pivot_table(days: int = 30, start_date: str = None, end_date: str = None, group_by: str = 'month'):
    """
    group_by: 'month' или 'day'
    """
    if start_date and end_date:
        start_dt = datetime.fromisoformat(start_date).date()
        end_dt = datetime.fromisoformat(end_date).date()
    else:
        end_dt = datetime.now().date()
        start_dt = end_dt - timedelta(days=days)

    # Определяем формат группировки
    if group_by == 'day':
        date_format = '%Y-%m-%d'  # 2025-01-15
    else:
        date_format = '%Y-%m'     # 2025-01

    with db_session() as conn:
        cursor = conn.execute(
            f"""
            SELECT 
                strftime('{date_format}', t.date) as period,
                s.analytic_type,
                ec.name as category_name,
                SUM(t.amount) as total
            FROM timeline t
            JOIN expense_categories ec ON t.category_id = ec.id
            LEFT JOIN analytics_settings s ON t.category_id = s.category_id
            WHERE t.type = 'expense' AND t.date >= ? AND t.date <= ?
            GROUP BY period, s.analytic_type, ec.name
            ORDER BY period DESC, s.analytic_type, ec.name
            """,
            (start_dt, end_dt),
        )

        rows = cursor.fetchall()

        pivot_data = {}
        for row in rows:
            period = row[0]
            analytic_type = row[1] or 'other'
            category = row[2]
            total = row[3]

            if period not in pivot_data:
                pivot_data[period] = {}
            if analytic_type not in pivot_data[period]:
                pivot_data[period][analytic_type] = {}
            pivot_data[period][analytic_type][category] = total
        
        print(f"Pivot data ({group_by}):", pivot_data)
        return pivot_data

# Эта функция не упоминалась в инструкции, поэтому она остается без изменений.
def get_trend_data(days: int = 30):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    with db_session() as conn:
        cursor = conn.execute(
            """
            SELECT 
                date,
                SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as revenue,
                SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as expenses
            FROM timeline
            WHERE date BETWEEN ? AND ?
            GROUP BY date
            ORDER BY date
            """,
            (start_date, end_date),
        )

        return [
            {
                "date": row["date"],
                "revenue": row["revenue"] or 0,
                "expenses": row["expenses"] or 0,
            }
            for row in cursor.fetchall()
        ]

def get_cell_details(period: str, category_name: str, group_by: str = 'month'):
    """
    Получить детали операций для конкретной ячейки таблицы
    
    period: '2024-11' или '2024-11-15' в зависимости от group_by
    category_name: название категории
    group_by: 'month' или 'day'
    """
    from datetime import datetime
    from calendar import monthrange
    
    # Определяем диапазон дат для периода
    if group_by == 'day':
        # Для дня: весь день
        start_dt = period
        end_dt = period
    else:
        # Для месяца: весь месяц
        year, month = period.split('-')
        last_day = monthrange(int(year), int(month))[1]
        start_dt = f"{year}-{month}-01"
        end_dt = f"{year}-{month}-{last_day:02d}"
    
    with db_session() as conn:
        cursor = conn.execute(
            """
            SELECT 
                t.id,
                t.date,
                t.type,
                t.amount,
                t.description,
                ec.name as category_name
            FROM timeline t
            JOIN expense_categories ec ON t.category_id = ec.id
            WHERE ec.name = ? 
                AND t.date >= ? 
                AND t.date <= ?
                AND t.type = 'expense'
            ORDER BY t.date DESC, t.id DESC
            """,
            (category_name, start_dt, end_dt),
        )
        
        rows = cursor.fetchall()
        
        operations = []
        for row in rows:
            operations.append({
                "id": row[0],
                "date": row[1],
                "type": row[2],
                "amount": row[3],
                "description": row[4] or "Без описания",
                "category_name": row[5]
            })
        
        return operations        