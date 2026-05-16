from sqlalchemy import text
from db.connection import engine
from core.services.journal_service import SystemJournal

class ScheduleService:
    def book_training(self, client_id: int, trainer_id: int, hall_id: int,
                      training_name: str, training_datetime: str,
                      amount: float = 0.0, log_employee_id: int = 1) -> int | None:
        query = text("""
            EXEC dbo.sp_ScheduleTraining
            @ClientID = :cid,
            @EmployeeID = :tid,
            @HallID = :hid,
            @TrainingName = :tn,
            @TrainingDateTime = :tdt,
            @Amount = :amt,
            @LogEmployeeID = :leid
        """)
        params = {"cid": client_id, "tid": trainer_id, "hid": hall_id,
                  "tn": training_name, "tdt": training_datetime,
                  "amt": amount, "leid": log_employee_id}
        with engine.begin() as conn:
            res = conn.execute(query, params)
            row = res.fetchone()
            return row[0] if row else None

    def update_training(self, training_id: int, training_datetime: str | None = None,
                        hall_id: int | None = None, training_name: str | None = None,
                        log_employee_id: int = 7) -> bool:
        """Редактирование времени, зала или названия занятия."""
        fields = []
        params = {"tid": training_id}
        if training_datetime is not None:
            fields.append("TrainingDateTime = :tdt")
            params["tdt"] = training_datetime
        if hall_id is not None:
            fields.append("HallID = :hid")
            params["hid"] = hall_id
        if training_name is not None:
            fields.append("TrainingName = :tn")
            params["tn"] = training_name
        if not fields:
            return False

        query = text(f"""
            UPDATE dbo.TrainingSchedule
            SET {', '.join(fields)}
            WHERE TrainingID = :tid
        """)
        with engine.begin() as conn:
            res = conn.execute(query, params)
            if res.rowcount > 0:
                SystemJournal.log(log_employee_id, "UPDATE", "TrainingSchedule", training_id,
                                  f"Изменено занятие ID={training_id}")
            return res.rowcount > 0

    def cancel_training(self, training_id: int, log_employee_id: int = 1) -> bool:
        """Отмена (удаление) индивидального занятия."""
        with engine.begin() as conn:
            res = conn.execute(text("""
                DELETE FROM dbo.TrainingSchedule WHERE TrainingID = :tid
            """), {"tid": training_id})
            if res.rowcount > 0:
                SystemJournal.log(log_employee_id, "DELETE", "TrainingSchedule", training_id,
                                  f"Отменено занятие ID={training_id}")
            return res.rowcount > 0

    def get_schedule(self, trainer_id: int | None = None, date: str | None = None) -> list[dict]:
        if trainer_id is not None:
            # Прямой запрос, т.к. vw_TrainingSchedule не содержит EmployeeID для фильтра
            query = """
                SELECT ts.TrainingID,
                       cl.LastName + ' ' + cl.FirstName as ClientName,
                       ts.TrainingName,
                       ts.TrainingDateTime,
                       h.Title as HallName,
                       ts.Status
                FROM dbo.TrainingSchedule ts
                JOIN dbo.Clients cl ON ts.ClientID = cl.ClientID
                JOIN dbo.Halls h ON ts.HallID = h.HallID
                WHERE ts.EmployeeID = :tid AND cl.DeletedAt IS NULL
            """
            params = {"tid": trainer_id}
            if date:
                query += " AND CAST(ts.TrainingDateTime AS DATE) = :dt"
                params["dt"] = date
            query += " ORDER BY ts.TrainingDateTime"
            with engine.connect() as conn:
                res = conn.execute(text(query), params)
                return [dict(r._mapping) for r in res]
        else:
            base_query = "SELECT * FROM dbo.vw_TrainingSchedule WHERE 1=1"
            params = {}
            if date:
                base_query += " AND CAST(TrainingDateTime AS DATE) = :dt"
                params["dt"] = date
            base_query += " ORDER BY TrainingDateTime"
            with engine.connect() as conn:
                res = conn.execute(text(base_query), params)
                return [dict(r._mapping) for r in res]

    def get_halls(self) -> list[dict]:
        """Список залов для назначения занятий."""
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT HallID, Title, Capacity FROM dbo.Halls ORDER BY Title
            """))
            return [dict(r._mapping) for r in res]

    def get_trainers(self) -> list[dict]:
        """Список тренеров (EmployeeID + ФИО)."""
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT e.EmployeeID, e.LastName + ' ' + e.FirstName AS FullName,
                       p.Title AS Position
                FROM dbo.Employees e
                JOIN dbo.Positions p ON e.PositionID = p.PositionID
                WHERE e.DeletedAt IS NULL
                  AND p.Title IN ('Trainer', 'Тренер')
                ORDER BY e.LastName
            """))
            return [dict(r._mapping) for r in res]

    def get_clients_for_schedule(self) -> list[dict]:
        """Список активных клиентов для записи на тренировку."""
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT c.ClientID, c.LastName + ' ' + c.FirstName AS FullName, c.Phone
                FROM dbo.Clients c
                WHERE c.DeletedAt IS NULL
                ORDER BY c.LastName
            """))
            return [dict(r._mapping) for r in res]

    def create_training(self, client_id: int, trainer_id: int, hall_id: int,
                        training_name: str, training_datetime: str,
                        amount: float = 0.0, log_employee_id: int = 1) -> int | None:
        """Создание записи на тренировку напрямую (без процедуры)."""
        from datetime import datetime
        # Парсим строку в datetime объект
        try:
            dt = datetime.strptime(training_datetime, "%Y-%m-%d %H:%M:%S")
            if dt < datetime.now():
                raise ValueError("Дата тренировки не может быть в прошлом.")
        except ValueError as e:
            raise ValueError(f"Некорректный формат даты. Ожидается YYYY-MM-DD HH:MM:SS. ({e})")

        with engine.begin() as conn:
            # Создаём оплату
            pay_res = conn.execute(text("""
                INSERT INTO dbo.Payments (Amount, PaymentType, Status)
                OUTPUT INSERTED.PaymentID
                VALUES (:amt, 'Cash', 'Completed')
            """), {"amt": amount})
            payment_id = pay_res.fetchone()[0]

            # Создаём запись в расписании — передаем datetime объект напрямую
            sch_res = conn.execute(text("""
                INSERT INTO dbo.TrainingSchedule
                    (ClientID, EmployeeID, HallID, PaymentID, TrainingDateTime, TrainingName, Status)
                OUTPUT INSERTED.TrainingID
                VALUES (:cid, :tid, :hid, :pid, :tdt, :tn, 'Scheduled')
            """), {
                "cid": client_id, "tid": trainer_id, "hid": hall_id,
                "pid": payment_id, "tdt": dt, "tn": training_name
            })
            training_id = sch_res.fetchone()[0]

            SystemJournal.log(log_employee_id, "INSERT", "TrainingSchedule", training_id,
                              f"Запись на тренировку ID={training_id}, клиент={client_id}")
            return training_id