from sqlalchemy import text
from db.connection import engine
from core.validators import Validators, ValidationError

class ClientService:
    def register_client(
        self, last_name: str, first_name: str, middle_name: str | None,
        birth_date: str, phone: str, email: str | None, passport: str,
        employee_id: int
    ) -> int | None:
        Validators.validate_not_empty(last_name, "Фамилия")
        Validators.validate_not_empty(first_name, "Имя")
        Validators.validate_birth_date(birth_date)
        Validators.validate_phone(phone)
        Validators.validate_passport(passport)

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

    def search_clients(self, search_text: str | None = None) -> list[dict]:
        """Поиск клиентов по ФИО, телефону, email или паспорту.
        При пустом запросе возвращает всех активных клиентов (последние 100).
        """
        if search_text and search_text.strip():
            q = f"%{search_text.strip()}%"
            query = text("""
                SELECT TOP 100 ClientID, LastName, FirstName, MiddleName,
                       BirthDate, Phone, Email, PassportData
                FROM dbo.Clients
                WHERE DeletedAt IS NULL
                  AND (
                      LastName LIKE :q
                      OR FirstName LIKE :q
                      OR ISNULL(MiddleName, '') LIKE :q
                      OR Phone LIKE :q
                      OR Email LIKE :q
                      OR PassportData LIKE :q
                      OR (LastName + ' ' + FirstName + ' ' + ISNULL(MiddleName, '')) LIKE :q
                  )
                ORDER BY LastName, FirstName
            """)
            params = {"q": q}
        else:
            # Пустой поиск — все активные клиенты
            query = text("""
                SELECT TOP 100 ClientID, LastName, FirstName, MiddleName,
                       BirthDate, Phone, Email, PassportData
                FROM dbo.Clients
                WHERE DeletedAt IS NULL
                ORDER BY LastName, FirstName
            """)
            params = {}

        with engine.connect() as conn:
            res = conn.execute(query, params)
            return [dict(r._mapping) for r in res]

    def get_client_by_id(self, client_id: int) -> dict | None:
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT * FROM dbo.Clients WHERE ClientID = :cid AND DeletedAt IS NULL
            """), {"cid": client_id})
            row = res.fetchone()
            return dict(row._mapping) if row else None