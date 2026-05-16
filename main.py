from db.connection import engine
from core.services.auth_service import AuthService
from core.services.client_service import ClientService
from core.services.subscription_service import SubscriptionService
from core.services.report_service import ReportService
from core.services.employee_service import EmployeeService
from core.services.payment_service import PaymentService
from core.services.schedule_service import ScheduleService
from core.services.inventory_service import InventoryService
from core.services.attendance_service import AttendanceService
from core.services.backup_service import BackupService
from datetime import date

def bootstrap():
    if engine is None:
        print("База данных недоступна. Проверьте настройки подключения.")
        return

    auth = AuthService()
    user = auth.authenticate("oleg", "admin123")
    
    if not user:
        print("Доступ запрещен или учетная запись не найдена.")
        return

    print(f"Авторизован: {user['name']} ({user['position']}) — уровень {user['access_level']}")

    # 1. Управление персоналом
    emp_svc = EmployeeService()
    print("\\n--- Управление персоналом ---")
    employees = emp_svc.get_employees()
    print(f"Активных сотрудников: {len(employees)}")
    for e in employees[:3]:
        print(f"  {e['EmployeeID']}: {e['LastName']} {e['FirstName']} — {e['PositionTitle']}")

    # 2. Регистрация клиента с валидацией
    client_svc = ClientService()
    print("\\n--- Регистрация клиента ---")
    try:
        new_id = client_svc.register_client(
            last_name="Тестов", first_name="Иван", middle_name="Петрович",
            birth_date="1990-01-01", phone="+79054133233", email="test@gym.com",
            passport="1234123890", employee_id=user['id']
        )
        print(f"Клиент зарегистрирован. ID: {new_id}")
    except Exception as e:
        print(f"Ошибка регистрации: {e}")

    # 3. Поиск клиентов
    print("\\n--- Поиск клиентов ---")
    found = client_svc.search_clients(search_text="Тестов")
    print(f"Найдено по ФИО: {len(found)}")
    found_phone = client_svc.search_clients(search_text="7905")
    print(f"Найдено по телефону: {len(found_phone)}")

    # 4. Абонементы и договоры
    sub_svc = SubscriptionService()
    print("\\n--- Типы абонементов ---")
    for sub in sub_svc.get_subscription_types():
        print(f"  {sub['Title']}: {sub['DurationDays']} дн. — {sub['Price']} руб.")

    # 5. Оплаты
    pay_svc = PaymentService()
    print("\\n--- Оплаты ---")
    print(f"Доступные способы: {', '.join(pay_svc.get_payment_types())}")

    # 6. Посещаемость
    att_svc = AttendanceService()
    print("\\n--- Посещаемость ---")
    status = att_svc.check_subscription_status(1)
    print(f"Статус абонемента клиента #1: {status}")

    # 7. Расписание
    sch_svc = ScheduleService()
    print("\\n--- Залы ---")
    for hall in sch_svc.get_halls():
        print(f"  {hall['HallID']}: {hall['Title']} (вместимость {hall['Capacity']})")

    # 8. Инвентарь (без HallID — схема БД не содержит связи)
    inv_svc = InventoryService()
    print("\\n--- Инвентарь ---")
    equip = inv_svc.get_equipment(status="InUse")
    print(f"Оборудования в использовании: {len(equip)}")
    for e in equip[:3]:
        print(f"  {e['EquipmentID']}: {e['Title']} ({e['Type']}) — {e['Status']}")

    # 9. Отчёты
    rep_svc = ReportService()
    today = date.today().isoformat()
    revenue = rep_svc.get_revenue(today, today)
    print(f"\\n--- Отчёты ---")
    print(f"Выручка за {today}: {revenue} руб.")
    active = rep_svc.get_active_clients()
    print(f"Активных клиентов: {len(active)}")

    # 10. Резервное копирование
    print("\\n--- Резервное копирование ---")
    bs = BackupService()
    backup_path = bs.auto_backup()
    print(f"Бэкап создан: {backup_path}")

    print("\\n=== Bootstrap завершён успешно ===")

if __name__ == "__main__":
    bootstrap()