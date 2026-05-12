import os
import urllib
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
server = os.getenv("DB_SERVER", "localhost")
database = os.getenv("DB_NAME", "GymDB")

params = urllib.parse.quote_plus(
    f"DRIVER={{{driver}}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)

try:
    engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={params}",
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=False
    )
    # Проверка соединения при инициализации
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
except Exception as e:
    print(f"Критическая ошибка подключения к БД: {e}")
    engine = None

__all__ = ["engine"]