from sqlalchemy import text
from db.connection import engine

class SubscriptionService:
    def get_subscription_types(self) -> list[dict]:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT SubscriptionTypeID, Title, DurationDays, Price FROM dbo.SubscriptionTypes"))
            return [dict(r._mapping) for r in res]

    def create_contract(self, client_id: int, subscription_type_id: int,
                        employee_id: int, amount: float,
                        payment_type: str = 'Cash', start_date: str | None = None) -> int | None:
        query = text("""
            EXEC dbo.sp_CreateContract
            @ClientID = :cid,
            @SubscriptionTypeID = :stid,
            @EmployeeID = :eid,
            @Amount = :amt,
            @PaymentType = :pt,
            @StartDate = :sd
        """)
        params = {"cid": client_id, "stid": subscription_type_id, "eid": employee_id,
                  "amt": amount, "pt": payment_type, "sd": start_date}
        with engine.begin() as conn:
            res = conn.execute(query, params)
            row = res.fetchone()
            return row[0] if row else None