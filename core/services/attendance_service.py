from datetime import datetime
from sqlalchemy import text
from db.connection import engine

class AttendanceService:
    def get_active_contract_id(self, client_id: int) -> int | None:
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT TOP 1 ContractID FROM dbo.Contracts
                WHERE ClientID = :cid AND Status = 'Active' AND EndDate >= CAST(GETDATE() AS DATE)
            """), {"cid": client_id})
            row = res.fetchone()
            return row[0] if row else None

    def check_subscription_status(self, client_id: int) -> dict:
        """Проверка статуса абонемента при входе (активен/просрочен/отсутствует)."""
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT TOP 1 c.ContractID, c.Status, c.EndDate, st.Title as SubscriptionTitle
                FROM dbo.Contracts c
                JOIN dbo.SubscriptionTypes st ON c.SubscriptionTypeID = st.SubscriptionTypeID
                WHERE c.ClientID = :cid
                ORDER BY c.StartDate DESC
            """), {"cid": client_id})
            row = res.fetchone()
            if not row:
                return {"status": "missing", "message": "Договор не найден"}
            if row.Status != "Active":
                return {"status": "inactive", "message": f"Договор не активен ({row.Status})"}
            if row.EndDate < datetime.now().date():
                return {"status": "expired", "message": f"Абонемент просрочен (до {row.EndDate})"}
            return {
                "status": "active",
                "contract_id": row.ContractID,
                "subscription": row.SubscriptionTitle,
                "end_date": row.EndDate
            }

    def check_in(self, client_id: int) -> bool:
        contract_id = self.get_active_contract_id(client_id)
        if not contract_id:
            return False

        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO dbo.Visits (ContractID, ClientID, CheckInTime)
                VALUES (:cid, :clid, :now)
            """), {"cid": contract_id, "clid": client_id, "now": datetime.now()})
        return True

    def check_out(self, client_id: int) -> bool:
        with engine.begin() as conn:
            res = conn.execute(text("""
                UPDATE dbo.Visits SET CheckOutTime = :now
                WHERE ClientID = :clid AND CheckOutTime IS NULL
            """), {"clid": client_id, "now": datetime.now()})
            return res.rowcount > 0

    def get_daily_visits(self, target_date: str) -> list[dict]:
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT * FROM dbo.vw_VisitLog
                WHERE CAST(CheckInTime AS DATE) = :date
                ORDER BY CheckInTime DESC
            """), {"date": target_date})
            return [dict(r._mapping) for r in res]