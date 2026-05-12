from sqlalchemy import text
from db.connection import engine

class ClientService:
    def register_client(
        self, last_name: str, first_name: str, middle_name: str | None,
        birth_date: str, phone: str, email: str | None, passport: str,
        employee_id: int
    ) -> int | None:
        query = text("""
            EXEC dbo.sp_RegisterClient
                @LastName = :ln,
                @FirstName = :fn,
                @MiddleName = :mn,
                @BirthDate = :bd,
                @Phone = :ph,
                @Email = :em,
                @PassportData = :ps,
                @EmployeeID = :eid
        """)
        params = {
            "ln": last_name, "fn": first_name, "mn": middle_name,
            "bd": birth_date, "ph": phone, "em": email,
            "ps": passport, "eid": employee_id
        }

        try:
            with engine.begin() as conn:
                result = conn.execute(query, params)
                row = result.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"Ошибка при регистрации клиента: {e}")
            raise