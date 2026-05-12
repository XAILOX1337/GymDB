from datetime import date
from db.connection import engine
from core.services.auth_service import AuthService
from core.services.client_service import ClientService
from core.services.subscription_service import SubscriptionService
from core.services.report_service import ReportService

def bootstrap():
    if engine is None:
        print("База данных недоступна. Проверьте настройки подключения.")
        return

    auth = AuthService()
    user = auth.authenticate("oleg", "admin123")
    
    if not user:
        print("Доступ запрещен или учетная запись не найдена.")
        return

    print(f"Авторизован: {user['name']} ({user['position']})")

    # Пример регистрации клиента
    client_svc = ClientService()
    try:
        new_id = client_svc.register_client(
            last_name="Тестов", first_name="Иван", middle_name="Петрович",
            birth_date="1990-01-01", phone="+79054133233", email="test@gym.com",
            passport="1234123890", employee_id=user['id']
        )
        print(f"Клиент зарегистрирован. ID: {new_id}")
    except Exception as e:
        print(f"Ошибка регистрации: {e}")

    # Пример формирования отчета
    rep_svc = ReportService()
    today = date.today().isoformat()
    revenue = rep_svc.get_revenue(today, today)
    print(f"Выручка за {today}: {revenue} руб.")

if __name__ == "__main__":
    bootstrap()