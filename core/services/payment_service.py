from datetime import datetime
from sqlalchemy import text
from db.connection import engine
from core.services.journal_service import SystemJournal
from core.validators import Validators, ValidationError

class PaymentService:
    def register_payment(self, contract_id: int, amount: float, payment_type: str,
                         employee_id: int, status: str = "Completed",
                         payment_date: str | None = None) -> int | None:
        Validators.validate_positive_amount(amount, "Сумма оплаты")

        if payment_date is None:
            payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        query = text("""
            INSERT INTO dbo.Payments (Amount, PaymentDate, Status, PaymentType)
            OUTPUT INSERTED.PaymentID
            VALUES (:amt, :pdate, :st, :ptype)
        """)
        params = {
            "amt": amount, "pdate": payment_date,
            "st": status, "ptype": payment_type
        }

        with engine.begin() as conn:
            res = conn.execute(query, params)
            row = res.fetchone()
            payment_id = row[0] if row else None
            if payment_id:
                SystemJournal.log(employee_id, "INSERT", "Payments", payment_id,
                                  f"Оплата ID={payment_id}, договор={contract_id}, сумма={amount}")
            return payment_id

    def get_payments_by_contract(self, contract_id: int) -> list[dict]:
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT PaymentID, Amount, PaymentDate, Status, PaymentType
                FROM dbo.Payments
                WHERE PaymentID IN (
                    SELECT PaymentID FROM dbo.Contracts WHERE ContractID = :cid
                )
                ORDER BY PaymentDate DESC
            """), {"cid": contract_id})
            return [dict(r._mapping) for r in res]

    def update_payment_status(self, payment_id: int, new_status: str, employee_id: int) -> bool:
        with engine.begin() as conn:
            res = conn.execute(text("""
                UPDATE dbo.Payments SET Status = :st WHERE PaymentID = :pid
            """), {"st": new_status, "pid": payment_id})
            if res.rowcount > 0:
                SystemJournal.log(employee_id, "UPDATE", "Payments", payment_id,
                                  f"Статус оплаты ID={payment_id} изменен на '{new_status}'")
            return res.rowcount > 0

    def get_payment_types(self) -> list[str]:
        return ["Cash", "Cashless", "Card", "Online"]