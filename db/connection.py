# db/connection.py
import os
import urllib
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

driver = os.getenv("driver", "ODBC Driver 18 for SQL Server")
server = os.getenv("server", "localhost")
database = os.getenv("database", "SportClubDB")


params = urllib.parse.quote_plus(
    f"DRIVER={{{driver}}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={params}",
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False  
)

__all__ = ["engine"]


if __name__ == "__main__":
    
    if engine:
        print("all ok")
    else: 
        print("unluck")