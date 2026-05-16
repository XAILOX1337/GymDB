from sqlalchemy import text
from db.connection import engine
from core.services.auth_service import AuthService
from core.services.journal_service import SystemJournal
from core.validators import Validators, ValidationError

class EmployeeService:
    def get_positions(self) -> list[dict]:
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT PositionID, Title, AccessLevel FROM dbo.Positions ORDER BY Title
            """))
            return [dict(r._mapping) for r in res]

    def get_employees(self, include_deleted: bool = False) -> list[dict]:
        query = """
            SELECT e.EmployeeID, e.FirstName, e.LastName, e.MiddleName,
                   e.Login, e.Phone, e.DeletedAt,
                   p.PositionID, p.Title as PositionTitle, p.AccessLevel
            FROM dbo.Employees e
            JOIN dbo.Positions p ON e.PositionID = p.PositionID
            WHERE 1=1
        """
        if not include_deleted:
            query += " AND e.DeletedAt IS NULL"
        query += " ORDER BY e.LastName, e.FirstName"

        with engine.connect() as conn:
            res = conn.execute(text(query))
            return [dict(r._mapping) for r in res]

    def add_employee(self, first_name: str, last_name: str, middle_name: str | None,
                     login: str, password: str, phone: str, position_id: int,
                     log_employee_id: int) -> int | None:
        Validators.validate_not_empty(first_name, "Имя")
        Validators.validate_not_empty(last_name, "Фамилия")
        Validators.validate_not_empty(login, "Логин")
        Validators.validate_not_empty(password, "Пароль")
        Validators.validate_phone(phone)

        pwd_hash = AuthService.hash_password(password)

        query = text("""
            INSERT INTO dbo.Employees (FirstName, LastName, MiddleName, Login, PasswordHash, Phone, PositionID)
            OUTPUT INSERTED.EmployeeID
            VALUES (:fn, :ln, :mn, :login, :pwd, :phone, :pid)
        """)
        params = {
            "fn": first_name, "ln": last_name, "mn": middle_name,
            "login": login, "pwd": pwd_hash, "phone": phone, "pid": position_id
        }

        with engine.begin() as conn:
            res = conn.execute(query, params)
            row = res.fetchone()
            new_id = row[0] if row else None
            if new_id:
                SystemJournal.log(log_employee_id, "INSERT", "Employees", new_id,
                                  f"Добавлен сотрудник ID={new_id}, логин={login}")
            return new_id

    def update_employee(self, employee_id: int, first_name: str | None = None,
                        last_name: str | None = None, middle_name: str | None = None,
                        phone: str | None = None, position_id: int | None = None,
                        password: str | None = None, log_employee_id: int = 1) -> bool:
        if phone:
            Validators.validate_phone(phone)

        fields = []
        params = {"eid": employee_id}

        if first_name is not None:
            fields.append("FirstName = :fn")
            params["fn"] = first_name
        if last_name is not None:
            fields.append("LastName = :ln")
            params["ln"] = last_name
        if middle_name is not None:
            fields.append("MiddleName = :mn")
            params["mn"] = middle_name
        if phone is not None:
            fields.append("Phone = :phone")
            params["phone"] = phone
        if position_id is not None:
            fields.append("PositionID = :pid")
            params["pid"] = position_id
        if password is not None:
            fields.append("PasswordHash = :pwd")
            params["pwd"] = AuthService.hash_password(password)

        if not fields:
            return False

        query = text(f"""
            UPDATE dbo.Employees SET {', '.join(fields)}
            WHERE EmployeeID = :eid AND DeletedAt IS NULL
        """)

        with engine.begin() as conn:
            res = conn.execute(query, params)
            if res.rowcount > 0:
                SystemJournal.log(log_employee_id, "UPDATE", "Employees", employee_id,
                                  f"Обновлен сотрудник ID={employee_id}")
            return res.rowcount > 0

    def deactivate_employee(self, employee_id: int, log_employee_id: int = 1) -> bool:
        """Мягкое удаление (деактивация) сотрудника."""
        with engine.begin() as conn:
            res = conn.execute(text("""
                UPDATE dbo.Employees SET DeletedAt = GETDATE()
                WHERE EmployeeID = :eid AND DeletedAt IS NULL
            """), {"eid": employee_id})
            if res.rowcount > 0:
                SystemJournal.log(log_employee_id, "DELETE", "Employees", employee_id,
                                  f"Деактивирован сотрудник ID={employee_id}")
            return res.rowcount > 0