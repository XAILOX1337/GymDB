from sqlalchemy import text
from db.connection import engine

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

    def get_schedule(self, trainer_id: int | None = None, date: str | None = None) -> list[dict]:
        base_query = "SELECT * FROM dbo.vw_TrainingSchedule WHERE 1=1"
        params = {}
        if trainer_id:
            base_query += " AND TrainerID = :tid"
            params["tid"] = trainer_id
        if date:
            base_query += " AND CAST(TrainingDateTime AS DATE) = :dt"
            params["dt"] = date
        base_query += " ORDER BY TrainingDateTime"

        with engine.connect() as conn:
            res = conn.execute(text(base_query), params)
            return [dict(r._mapping) for r in res]