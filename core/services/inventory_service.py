from sqlalchemy import text
from db.connection import engine

class InventoryService:
    def get_halls(self) -> list[dict]:
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT HallID, Title, Capacity FROM dbo.Halls ORDER BY Title
            """))
            return [dict(r._mapping) for r in res]

    def get_equipment(self, status: str | None = None, hall_id: int | None = None) -> list[dict]:
        # Пробуем расширенный запрос с HallID (по ТЗ)
        try:
            query = """
                SELECT e.EquipmentID, e.Title, e.Type, e.Status,
                       e.PurchaseDate, e.Description, h.Title as HallName, e.HallID
                FROM dbo.Equipment e
                LEFT JOIN dbo.Halls h ON e.HallID = h.HallID
                WHERE 1=1
            """
            params = {}
            if status:
                query += " AND e.Status = :st"
                params["st"] = status
            if hall_id is not None:
                query += " AND e.HallID = :hid"
                params["hid"] = hall_id
            query += " ORDER BY e.Title"

            with engine.connect() as conn:
                res = conn.execute(text(query), params)
                return [dict(r._mapping) for r in res]

        except Exception as e:
            # Fallback: если HallID нет в схеме — запрашиваем базовые поля
            err_msg = str(e).lower()
            if "hallid" in err_msg or "invalid column" in err_msg:
                query = """
                    SELECT EquipmentID, Title, Type, Status, PurchaseDate, Description
                    FROM dbo.Equipment
                    WHERE 1=1
                """
                params = {}
                if status:
                    query += " AND Status = :st"
                    params["st"] = status
                query += " ORDER BY Title"
                with engine.connect() as conn:
                    res = conn.execute(text(query), params)
                    rows = [dict(r._mapping) for r in res]
                    # Добавляем HallName и HallID = None для совместимости с GUI
                    for r in rows:
                        r["HallName"] = "—"
                        r["HallID"] = None
                    return rows
            else:
                raise

    def update_equipment_status(self, equipment_id: int, new_status: str) -> bool:
        with engine.begin() as conn:
            res = conn.execute(text("""
                UPDATE dbo.Equipment SET Status = :st WHERE EquipmentID = :eid
            """), {"st": new_status, "eid": equipment_id})
            return res.rowcount > 0

    def assign_to_hall(self, equipment_id: int, hall_id: int | None) -> bool:
        """Закрепление инвентаря за залом. Если HallID отсутствует в БД — вернёт False."""
        try:
            with engine.begin() as conn:
                res = conn.execute(text("""
                    UPDATE dbo.Equipment SET HallID = :hid WHERE EquipmentID = :eid
                """), {"hid": hall_id, "eid": equipment_id})
                return res.rowcount > 0
        except Exception as e:
            if "hallid" in str(e).lower():
                return False
            raise