from typing import Optional

from fastapi import Depends, Header, HTTPException, status

from database import db_session


def get_user_id_by_telegram(telegram_id: str) -> Optional[int]:
    """
    Получить user_id по telegram_id
    """
    try:
        telegram_id_int = int(telegram_id)
    except (ValueError, TypeError):
        print(f"[AUTH] Невалидный telegram_id: {telegram_id}")
        return None
    
    with db_session() as conn:
        cursor = conn.execute(
            """
            SELECT id
            FROM users
            WHERE telegram_id = ? AND is_active = 1
            """,
            (telegram_id_int,),
        )
        row = cursor.fetchone()
        
        if row:
            user_id = row["id"]
            print(f"[AUTH] Найден пользователь: telegram_id={telegram_id_int} -> user_id={user_id}")
            return user_id
        else:
            print(f"[AUTH] Пользователь НЕ найден: telegram_id={telegram_id_int}")
            return None


async def get_current_user_id(
    x_telegram_id: Optional[str] = Header(None, alias="X-Telegram-Id"),
) -> int:
    """
    Зависимость для получения текущего user_id из заголовка
    """
    print(f"[AUTH] Получен заголовок X-Telegram-Id: {x_telegram_id}")
    
    if not x_telegram_id:
        print("[AUTH] ❌ Заголовок X-Telegram-Id отсутствует")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Telegram-Id header is required",
        )

    user_id = get_user_id_by_telegram(x_telegram_id)
    if user_id is None:
        print(f"[AUTH] ❌ Пользователь не авторизован: telegram_id={x_telegram_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized",
        )

    print(f"[AUTH] ✅ Пользователь авторизован: user_id={user_id}")
    return user_id 