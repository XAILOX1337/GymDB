from datetime import date, datetime

class ValidationError(Exception):
    pass

class Validators:
    @staticmethod
    def validate_positive_amount(value: float, field_name: str = "Сумма"):
        if value is None:
            return
        if value < 0:
            raise ValidationError(f"{field_name} не может быть отрицательной.")

    @staticmethod
    def validate_birth_date(birth_date: str | date):
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
        if birth_date > date.today():
            raise ValidationError("Дата рождения не может превышать текущую дату.")

    @staticmethod
    def validate_phone(phone: str):
        cleaned = phone.replace("+", "").replace("-", "").replace(" ", "")
        if not cleaned.isdigit() or len(cleaned) < 10:
            raise ValidationError("Некорректный номер телефона.")

    @staticmethod
    def validate_passport(passport: str):
        cleaned = passport.replace(" ", "").replace("-", "")
        if not cleaned.isdigit() or len(cleaned) != 10:
            raise ValidationError("Паспортные данные должны содержать 10 цифр (серия + номер).")

    @staticmethod
    def validate_not_empty(value: str, field_name: str):
        if not value or not value.strip():
            raise ValidationError(f"Поле '{field_name}' обязательно для заполнения.")