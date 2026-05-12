from sqlalchemy import text
from db.connection import engine

class ReportService:
    def get_active_clients(self) -> list[dict]:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT ClientFullName, ClientPhone, SubscriptionType, StartDate, EndDate, ContractStatus FROM dbo.vw_ActiveContracts"))
            return [dict(r._mapping) for r in res]

    def get_revenue(self, start_date: str, end_date: str) -> float:
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT SUM(Amount) FROM dbo.Payments
                WHERE Status = 'Completed'
                AND CAST(PaymentDate AS DATE) BETWEEN :start AND :end
            """), {"start": start_date, "end": end_date})
            val = res.scalar()
            return val if val else 0.0

    def get_visit_log(self, start_date: str, end_date: str) -> list[dict]:
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT * FROM dbo.vw_VisitLog
                WHERE CAST(CheckInTime AS DATE) BETWEEN :start AND :end
                ORDER BY CheckInTime DESC
            """), {"start": start_date, "end": end_date})
            return [dict(r._mapping) for r in res]