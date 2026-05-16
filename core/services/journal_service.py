from datetime import datetime
from sqlalchemy import text
from db.connection import engine

class SystemJournal:
    @staticmethod
    def log(employee_id: int, operation: str, table_name: str, record_id: int, details: str):
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO dbo.SystemLog (EmployeeID, OperationTime, OperationType, TableName, RecordID, Description)
                VALUES (:eid, :time, :op, :tbl, :rid, :det)
            """), {
                "eid": employee_id, "time": datetime.now(),
                "op": operation, "tbl": table_name,
                "rid": record_id, "det": details
            })
            conn.commit()