import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = Path("/Users/alisheryusupov2002/Desktop/finance_system_v5/finance_v5.db")
DB_PATH = Path(os.getenv("FINANCE_DB_PATH", DEFAULT_DB_PATH))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_session() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

