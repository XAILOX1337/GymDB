from sqlalchemy import text
from db.connection import engine

class InventoryService:
    def get_equipment(self, status: str | None = None) -> list[dict]:
        query = "SELECT EquipmentID, Title, Type, Status, PurchaseDate, Description FROM dbo.Equipment WHERE 1=1"
        params = {}
        if status:
            query += " AND Status = :st"
            params["st"] = status

        with engine.connect() as conn:
            res = conn.execute(text(query), params)
            return [dict(r._mapping) for r in res]

    def update_equipment_status(self, equipment_id: int, new_status: str) -> bool:
        with engine.begin() as conn:
            res = conn.execute(text("""
                UPDATE dbo.Equipment SET Status = :st WHERE EquipmentID = :eid
            """), {"st": new_status, "eid": equipment_id})
            return res.rowcount > 0