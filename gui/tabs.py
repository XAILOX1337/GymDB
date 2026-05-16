from datetime import date
from types import NoneType

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateTimeEdit, QDateEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QFormLayout,
    QDateEdit, QSpinBox, QDoubleSpinBox, QGroupBox, QSplitter
)
from PyQt6.QtCore import QDateTime, Qt, QDate

from core.services.employee_service import EmployeeService
from core.services.client_service import ClientService
from core.services.subscription_service import SubscriptionService
from core.services.payment_service import PaymentService
from core.services.schedule_service import ScheduleService
from core.services.inventory_service import InventoryService
from core.services.attendance_service import AttendanceService
from core.services.report_service import ReportService
from core.services.report_export_service import ReportExportService
from core.validators import ValidationError

class AdminTab(QWidget):
    """Администратор: управление персоналом, доступом и справочниками."""
    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)
        self.user = current_user
        self.emp_svc = EmployeeService()
        self._build_ui()
        self.load_employees()
        self.load_positions()

    def _build_ui(self):
        main = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        form = QFormLayout(left)
        self.inp_emp_ln = QLineEdit()
        self.inp_emp_fn = QLineEdit()
        self.inp_emp_mn = QLineEdit()
        self.inp_emp_login = QLineEdit()
        self.inp_emp_pwd = QLineEdit()
        self.inp_emp_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_emp_phone = QLineEdit()
        self.cmb_position = QComboBox()
        form.addRow("Фамилия:", self.inp_emp_ln)
        form.addRow("Имя:", self.inp_emp_fn)
        form.addRow("Отчество:", self.inp_emp_mn)
        form.addRow("Логин:", self.inp_emp_login)
        form.addRow("Пароль:", self.inp_emp_pwd)
        form.addRow("Телефон:", self.inp_emp_phone)
        form.addRow("Должность:", self.cmb_position)

        btn_add = QPushButton("Добавить сотрудника")
        btn_add.clicked.connect(self.add_employee)
        btn_upd = QPushButton("Обновить выбранного")
        btn_upd.clicked.connect(self.update_employee)
        btn_del = QPushButton("Деактивировать")
        btn_del.clicked.connect(self.deactivate_employee)
        form.addRow(btn_add)
        form.addRow(btn_upd)
        form.addRow(btn_del)
        splitter.addWidget(left)

        right = QWidget()
        rlay = QVBoxLayout(right)
        self.tbl_employees = QTableWidget()
        self.tbl_employees.setColumnCount(6)
        self.tbl_employees.setHorizontalHeaderLabels(
            ["ID", "Фамилия", "Имя", "Должность", "Телефон", "Уровень доступа"]
        )
        self.tbl_employees.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        rlay.addWidget(self.tbl_employees)
        splitter.addWidget(right)
        splitter.setSizes([350, 650])
        main.addWidget(splitter)

    def load_positions(self):
        self.cmb_position.clear()
        for pos in self.emp_svc.get_positions():
            self.cmb_position.addItem(pos["Title"], pos["PositionID"])

    def load_employees(self):
        data = self.emp_svc.get_employees()
        self.tbl_employees.setRowCount(len(data))
        for i, row in enumerate(data):
            self.tbl_employees.setItem(i, 0, QTableWidgetItem(str(row.get("EmployeeID", ""))))
            self.tbl_employees.setItem(i, 1, QTableWidgetItem(row.get("LastName", "")))
            self.tbl_employees.setItem(i, 2, QTableWidgetItem(row.get("FirstName", "")))
            self.tbl_employees.setItem(i, 3, QTableWidgetItem(row.get("PositionTitle", "")))
            self.tbl_employees.setItem(i, 4, QTableWidgetItem(row.get("Phone", "")))
            self.tbl_employees.setItem(i, 5, QTableWidgetItem(str(row.get("AccessLevel", ""))))

    def add_employee(self):
        try:
            pid = self.cmb_position.currentData()
            new_id = self.emp_svc.add_employee(
                first_name=self.inp_emp_fn.text(),
                last_name=self.inp_emp_ln.text(),
                middle_name=self.inp_emp_mn.text() or None,
                login=self.inp_emp_login.text(),
                password=self.inp_emp_pwd.text(),
                phone=self.inp_emp_phone.text(),
                position_id=pid,
                log_employee_id=self.user["id"]
            )
            QMessageBox.information(self, "Успех", f"Сотрудник добавлен. ID: {new_id}")
            self.load_employees()
        except ValidationError as e:
            QMessageBox.warning(self, "Ошибка валидации", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def update_employee(self):
        row = self.tbl_employees.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите сотрудника в таблице.")
            return
        eid = int(self.tbl_employees.item(row, 0).text())
        try:
            self.emp_svc.update_employee(
                employee_id=eid,
                first_name=self.inp_emp_fn.text() or None,
                last_name=self.inp_emp_ln.text() or None,
                middle_name=self.inp_emp_mn.text() or None,
                phone=self.inp_emp_phone.text() or None,
                position_id=self.cmb_position.currentData(),
                log_employee_id=self.user["id"]
            )
            QMessageBox.information(self, "Успех", "Данные обновлены.")
            self.load_employees()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def deactivate_employee(self):
        row = self.tbl_employees.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите сотрудника.")
            return
        eid = int(self.tbl_employees.item(row, 0).text())
        if QMessageBox.question(self, "Подтверждение", "Деактивировать сотрудника?") == QMessageBox.StandardButton.Yes:
            if self.emp_svc.deactivate_employee(eid, self.user["id"]):
                QMessageBox.information(self, "Успех", "Сотрудник деактивирован.")
                self.load_employees()


class ManagerTab(QWidget):
    """Менеджер: клиенты, договоры, оплаты."""
    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)
        self.user = current_user
        self.client_svc = ClientService()
        self.sub_svc = SubscriptionService()
        self.pay_svc = PaymentService()
        self._build_ui()
        self.load_subscriptions()
        self.search_clients()  # Загрузить всех клиентов при старте

    def _build_ui(self):
        main = QVBoxLayout(self)

        grp_client = QGroupBox("Регистрация клиента")
        fl = QFormLayout(grp_client)
        self.inp_cl_ln = QLineEdit()
        self.inp_cl_fn = QLineEdit()
        self.inp_cl_mn = QLineEdit()
        self.inp_cl_bd = QDateEdit()
        self.inp_cl_bd.setCalendarPopup(True)
        self.inp_cl_bd.setDate(QDate.currentDate().addYears(-25))
        self.inp_cl_phone = QLineEdit()
        self.inp_cl_email = QLineEdit()
        self.inp_cl_passport = QLineEdit()
        fl.addRow("Фамилия:", self.inp_cl_ln)
        fl.addRow("Имя:", self.inp_cl_fn)
        fl.addRow("Отчество:", self.inp_cl_mn)
        fl.addRow("Дата рождения:", self.inp_cl_bd)
        fl.addRow("Телефон:", self.inp_cl_phone)
        fl.addRow("Email:", self.inp_cl_email)
        fl.addRow("Паспорт (10 цифр):", self.inp_cl_passport)
        btn_reg = QPushButton("Зарегистрировать")
        btn_reg.clicked.connect(self.register_client)
        fl.addRow(btn_reg)
        main.addWidget(grp_client)

        # --- Поиск клиентов ---
        grp_search = QGroupBox("Поиск клиентов (ФИО, телефон, email, паспорт)")
        h = QHBoxLayout(grp_search)
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Введите текст для поиска...")
        self.inp_search.returnPressed.connect(self.search_clients)
        btn_search = QPushButton("Найти")
        btn_search.clicked.connect(self.search_clients)
        btn_clear = QPushButton("Показать всех")
        btn_clear.clicked.connect(self.load_all_clients)
        h.addWidget(self.inp_search)
        h.addWidget(btn_search)
        h.addWidget(btn_clear)
        main.addWidget(grp_search)

        self.tbl_clients = QTableWidget()
        self.tbl_clients.setColumnCount(6)
        self.tbl_clients.setHorizontalHeaderLabels(["ID", "Фамилия", "Имя", "Телефон", "Email", "Паспорт"])
        self.tbl_clients.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_clients.itemSelectionChanged.connect(self.on_client_selected)
        self.tbl_clients.cellDoubleClicked.connect(self.on_client_double_clicked)
        main.addWidget(self.tbl_clients)

        # --- Оформление договора ---
        grp_contract = QGroupBox("Оформление договора и оплата")
        cfl = QFormLayout(grp_contract)
        self.lbl_selected_client = QLabel("Клиент не выбран")
        self.lbl_selected_client.setStyleSheet("color: gray;")
        self.inp_contract_client = QSpinBox()
        self.inp_contract_client.setRange(1, 999999)
        self.cmb_sub_type = QComboBox()
        self.inp_contract_amount = QDoubleSpinBox()
        self.inp_contract_amount.setRange(0, 999999)
        self.inp_contract_amount.setDecimals(2)
        self.inp_contract_amount.setValue(3500.00)
        self.cmb_pay_type = QComboBox()
        for pt in self.pay_svc.get_payment_types():
            self.cmb_pay_type.addItem(pt)
        cfl.addRow(self.lbl_selected_client)
        cfl.addRow("ID клиента:", self.inp_contract_client)
        cfl.addRow("Тип абонемента:", self.cmb_sub_type)
        cfl.addRow("Сумма:", self.inp_contract_amount)
        cfl.addRow("Способ оплаты:", self.cmb_pay_type)
        btn_contract = QPushButton("Оформить договор + оплату")
        btn_contract.clicked.connect(self.create_contract)
        cfl.addRow(btn_contract)
        main.addWidget(grp_contract)

    def load_subscriptions(self):
        self.cmb_sub_type.clear()
        for sub in self.sub_svc.get_subscription_types():
            text = f"{sub['Title']} ({sub['DurationDays']} дн.) — {sub['Price']} руб."
            self.cmb_sub_type.addItem(text, sub["SubscriptionTypeID"])

    def register_client(self):
        try:
            cid = self.client_svc.register_client(
                last_name=self.inp_cl_ln.text(),
                first_name=self.inp_cl_fn.text(),
                middle_name=self.inp_cl_mn.text() or None,
                birth_date=self.inp_cl_bd.date().toString("yyyy-MM-dd"),
                phone=self.inp_cl_phone.text(),
                email=self.inp_cl_email.text() or None,
                passport=self.inp_cl_passport.text(),
                employee_id=self.user["id"]
            )
            QMessageBox.information(self, "Успех", f"Клиент зарегистрирован. ID: {cid}")
            self.search_clients()  # Обновить список
        except ValidationError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def load_all_clients(self):
        """Показать всех активных клиентов."""
        self.inp_search.clear()
        self.search_clients()

    def search_clients(self):
        text = self.inp_search.text().strip()
        try:
            data = self.client_svc.search_clients(search_text=text)
            self.tbl_clients.setRowCount(len(data))
            for i, row in enumerate(data):
                self.tbl_clients.setItem(i, 0, QTableWidgetItem(str(row.get("ClientID", ""))))
                self.tbl_clients.setItem(i, 1, QTableWidgetItem(row.get("LastName", "")))
                self.tbl_clients.setItem(i, 2, QTableWidgetItem(row.get("FirstName", "")))
                self.tbl_clients.setItem(i, 3, QTableWidgetItem(row.get("Phone", "")))
                self.tbl_clients.setItem(i, 4, QTableWidgetItem(row.get("Email", "")))
                self.tbl_clients.setItem(i, 5, QTableWidgetItem(row.get("PassportData", "")))
            if not data:
                QMessageBox.information(self, "Поиск", "Клиенты не найдены.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка поиска", str(e))

    def on_client_selected(self):
        """При выборе строки в таблице клиентов подставляем ID в поле договора."""
        row = self.tbl_clients.currentRow()
        if row < 0:
            return
        client_id_item = self.tbl_clients.item(row, 0)
        last_name_item = self.tbl_clients.item(row, 1)
        first_name_item = self.tbl_clients.item(row, 2)
        if client_id_item:
            cid = int(client_id_item.text())
            self.inp_contract_client.setValue(cid)
            name = f"{last_name_item.text()} {first_name_item.text()}" if last_name_item and first_name_item else f"ID {cid}"
            self.lbl_selected_client.setText(f"Выбран клиент: {name} (ID: {cid})")
            self.lbl_selected_client.setStyleSheet("color: green; font-weight: bold;")

    def on_client_double_clicked(self, row, column):
        """Двойной клик — подтверждение выбора клиента."""
        self.on_client_selected()
        QMessageBox.information(self, "Клиент выбран", self.lbl_selected_client.text())

    def create_contract(self):
        client_id = self.inp_contract_client.value()
        # Проверим, что клиент существует
        client = self.client_svc.get_client_by_id(client_id)
        if not client:
            QMessageBox.warning(self, "Ошибка", f"Клиент с ID={client_id} не найден.\\nВыберите клиента из таблицы выше.")
            return
        try:
            sub_id = self.cmb_sub_type.currentData()
            amount = self.inp_contract_amount.value()
            pay_type = self.cmb_pay_type.currentText()

            contract_id = self.sub_svc.create_contract(
                client_id=client_id,
                subscription_type_id=sub_id,
                employee_id=self.user["id"],
                amount=amount,
                payment_type=pay_type
            )
            if contract_id:
                QMessageBox.information(self, "Успех", f"Договор ID={contract_id} оформлен.")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось создать договор.")
        except ValidationError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            err_msg = str(e)
            if "FK_SystemLog_Employee" in err_msg or "547" in err_msg:
                QMessageBox.critical(
                    self, "Ошибка базы данных",
                    "Не удалось создать договор из-за ошибки аудита (SystemLog).\\n\\n"
                    "Причина: в триггерах БД жёстко зашит EmployeeID=1, которого нет в таблице сотрудников.\\n\\n"
                    "Решение: выполните скрипт fix_triggers.sql в SSMS, чтобы триггеры брали EmployeeID из реальных данных."
                )
            else:
                QMessageBox.critical(self, "Ошибка", err_msg)


class TrainerTab(QWidget):
    """Тренер: расписание и залы."""
    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)
        self.user = current_user
        self.sch_svc = ScheduleService()
        self.inv_svc = InventoryService()
        self.att_svc = AttendanceService()
        self._build_ui()
        self.load_halls()
        self.load_schedule()
        self.load_equipment()
        self.load_visits()

    def _build_ui(self):
        main = QVBoxLayout(self)

        grp_sch = QGroupBox("Моё расписание")
        v = QVBoxLayout(grp_sch)
        self.tbl_schedule = QTableWidget()
        self.tbl_schedule.setColumnCount(5)
        self.tbl_schedule.setHorizontalHeaderLabels(["ID", "Клиент", "Занятие", "Зал", "Дата/время"])
        v.addWidget(self.tbl_schedule)
        
        btn_load = QPushButton("Обновить расписание")
        # FIX: lambda блокирует передачу bool-аргумента от сигнала clicked
        btn_load.clicked.connect(lambda: self.load_schedule())
        v.addWidget(btn_load)
        main.addWidget(grp_sch)

        grp_hall = QGroupBox("Залы")
        h = QHBoxLayout(grp_hall)
        self.cmb_hall = QComboBox()
        h.addWidget(QLabel("Зал:"))
        h.addWidget(self.cmb_hall)
        main.addWidget(grp_hall)

        grp_equip = QGroupBox("Инвентарь клуба")
        eq = QVBoxLayout(grp_equip)
        self.tbl_equip = QTableWidget()
        self.tbl_equip.setColumnCount(4)
        self.tbl_equip.setHorizontalHeaderLabels(["ID", "Название", "Тип", "Статус"])
        eq.addWidget(self.tbl_equip)
        btn_eq = QPushButton("Обновить инвентарь")
        btn_eq.clicked.connect(self.load_equipment)
        eq.addWidget(btn_eq)
        main.addWidget(grp_equip)

        grp_visits = QGroupBox("Посещаемость на сегодня")
        vv = QVBoxLayout(grp_visits)
        self.tbl_visits = QTableWidget()
        self.tbl_visits.setColumnCount(3)
        self.tbl_visits.setHorizontalHeaderLabels(["Клиент", "Вход", "Выход"])
        vv.addWidget(self.tbl_visits)
        btn_vis = QPushButton("Обновить посещаемость")
        btn_vis.clicked.connect(self.load_visits)
        vv.addWidget(btn_vis)
        main.addWidget(grp_visits)


    def load_schedule(self):
        try:
            # Убрана фильтрация по today(). Теперь показывает все актуальные записи тренера.
            data = self.sch_svc.get_schedule(trainer_id=self.user["id"], date=None)
            self.tbl_schedule.setRowCount(len(data))
            for i, row in enumerate(data):
                self.tbl_schedule.setItem(i, 0, QTableWidgetItem(str(row.get("TrainingID", ""))))
                self.tbl_schedule.setItem(i, 1, QTableWidgetItem(row.get("ClientName", "")))
                self.tbl_schedule.setItem(i, 2, QTableWidgetItem(row.get("TrainingName", "")))
                self.tbl_schedule.setItem(i, 3, QTableWidgetItem(row.get("HallName", "")))
                # Безопасное преобразование datetime в строку
                dt_val = row.get("TrainingDateTime")
                dt_str = dt_val.strftime("%Y-%m-%d %H:%M") if dt_val else ""
                self.tbl_schedule.setItem(i, 4, QTableWidgetItem(dt_str))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка загрузки расписания", str(e))

    def load_halls(self):
        try:
            self.cmb_hall.clear()
            for hall in self.inv_svc.get_halls():
                self.cmb_hall.addItem(hall["Title"], hall["HallID"])
        except Exception as e:
            QMessageBox.warning(self, "Ошибка загрузки залов", str(e))

    def load_schedule(self):
        try:
            data = self.sch_svc.get_schedule(trainer_id=self.user["id"], date=None)
            
            self.tbl_schedule.setRowCount(len(data))
            for i, row in enumerate(data):
                self.tbl_schedule.setItem(i, 0, QTableWidgetItem(str(row.get("TrainingID", ""))))
                self.tbl_schedule.setItem(i, 1, QTableWidgetItem(row.get("ClientName", "")))
                self.tbl_schedule.setItem(i, 2, QTableWidgetItem(row.get("TrainingName", "")))
                self.tbl_schedule.setItem(i, 3, QTableWidgetItem(row.get("HallName", "")))
                
                # FIX: Безопасный рендер datetime-объекта из SQLAlchemy/pyodbc
                dt_val = row.get("TrainingDateTime")
                dt_str = dt_val.strftime("%Y-%m-%d %H:%M") if dt_val else ""
                self.tbl_schedule.setItem(i, 4, QTableWidgetItem(dt_str))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка загрузки расписания", str(e))

    def load_equipment(self):
        try:
            data = self.inv_svc.get_equipment()
            self.tbl_equip.setRowCount(len(data))
            for i, row in enumerate(data):
                self.tbl_equip.setItem(i, 0, QTableWidgetItem(str(row.get("EquipmentID", ""))))
                self.tbl_equip.setItem(i, 1, QTableWidgetItem(row.get("Title", "")))
                self.tbl_equip.setItem(i, 2, QTableWidgetItem(row.get("Type", "")))
                self.tbl_equip.setItem(i, 3, QTableWidgetItem(row.get("Status", "")))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка загрузки инвентаря", str(e))
            self.tbl_equip.setRowCount(0)

    def load_visits(self):
        try:
            data = self.att_svc.get_daily_visits(date.today().isoformat())
            self.tbl_visits.setRowCount(len(data))
            for i, row in enumerate(data):
                self.tbl_visits.setItem(i, 0, QTableWidgetItem(row.get("ClientFullName", "")))
                self.tbl_visits.setItem(i, 1, QTableWidgetItem(str(row.get("CheckInTime", ""))))
                self.tbl_visits.setItem(i, 2, QTableWidgetItem(str(row.get("CheckOutTime", ""))))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка загрузки посещаемости", str(e))



class ScheduleCreateTab(QWidget):
    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)
        self.user = current_user
        self.sch_svc = ScheduleService()
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        main = QVBoxLayout(self)

        grp = QGroupBox("Новая запись на тренировку")
        fl = QFormLayout(grp)

        self.cmb_client = QComboBox()
        self.cmb_trainer = QComboBox()
        self.cmb_hall = QComboBox()
        self.inp_training_name = QLineEdit()
        self.inp_training_name.setPlaceholderText("Например: Персональная тренировка")
        
        self.inp_datetime = QDateTimeEdit()
        self.inp_datetime.setCalendarPopup(True)
        self.inp_datetime.setDateTime(QDateTime.currentDateTime().addDays(1))
        self.inp_datetime.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.inp_datetime.setMinimumDateTime(QDateTime.currentDateTime())
        
        self.inp_amount = QDoubleSpinBox()
        self.inp_amount.setRange(0, 999999)
        self.inp_amount.setDecimals(2)
        self.inp_amount.setValue(2500.00)

        fl.addRow("Клиент: ", self.cmb_client)
        fl.addRow("Тренер: ", self.cmb_trainer)
        fl.addRow("Зал: ", self.cmb_hall)
        fl.addRow("Название занятия: ", self.inp_training_name)
        fl.addRow("Дата и время: ", self.inp_datetime)
        fl.addRow("Стоимость: ", self.inp_amount)

        btn_create = QPushButton("Создать запись")
        btn_create.clicked.connect(self.create_training)
        fl.addRow(btn_create)
        main.addWidget(grp)

        grp_list = QGroupBox("Текущее расписание")
        v = QVBoxLayout(grp_list)
        self.tbl_schedule = QTableWidget()
        self.tbl_schedule.setColumnCount(6)
        self.tbl_schedule.setHorizontalHeaderLabels(["ID", "Клиент", "Тренер", "Зал", "Занятие", "Дата/время"])
        v.addWidget(self.tbl_schedule)
        
        btn_refresh = QPushButton("Обновить")
        # FIX: lambda блокирует передачу boolean-аргумента от сигнала clicked
        btn_refresh.clicked.connect(lambda: self.load_schedule())
        v.addWidget(btn_refresh)
        main.addWidget(grp_list)

    def load_data(self):
        try:
            self.cmb_client.clear()
            for c in self.sch_svc.get_clients_for_schedule():
                self.cmb_client.addItem(f"{c['FullName']} (ID: {c['ClientID']})", c["ClientID"])

            self.cmb_trainer.clear()
            trainers = self.sch_svc.get_trainers()
            if not trainers:
                from core.services.employee_service import EmployeeService
                emp_svc = EmployeeService()
                trainers = emp_svc.get_employees()
                for t in trainers:
                    self.cmb_trainer.addItem(f"{t['LastName']} {t['FirstName']} — {t['PositionTitle']}", t["EmployeeID"])
            else:
                for t in trainers:
                    self.cmb_trainer.addItem(t["FullName"], t["EmployeeID"])

            self.cmb_hall.clear()
            for h in self.sch_svc.get_halls():
                self.cmb_hall.addItem(f"{h['Title']} (вместимость {h['Capacity']})", h["HallID"])

            self.load_schedule()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка загрузки данных", str(e))

    def load_schedule(self, trainer_id: int | None = None):
        try:
            # FIX: Убрана жесткая фильтрация по today(). Теперь загружаются все записи.
            data = self.sch_svc.get_schedule(trainer_id=trainer_id, date=None)
            self.tbl_schedule.setRowCount(len(data))
            for i, row in enumerate(data):
                self.tbl_schedule.setItem(i, 0, QTableWidgetItem(str(row.get("TrainingID", ""))))
                self.tbl_schedule.setItem(i, 1, QTableWidgetItem(row.get("ClientFullName", "")))
                self.tbl_schedule.setItem(i, 2, QTableWidgetItem(row.get("TrainerFullName", "")))
                self.tbl_schedule.setItem(i, 3, QTableWidgetItem(row.get("Hall", "")))
                self.tbl_schedule.setItem(i, 4, QTableWidgetItem(row.get("TrainingName", "")))
                
                dt_val = row.get("TrainingDateTime")
                # FIX: Безопасное преобразование datetime-объекта из SQLAlchemy
                dt_str = dt_val.strftime("%Y-%m-%d %H:%M") if dt_val else ""
                self.tbl_schedule.setItem(i, 5, QTableWidgetItem(dt_str))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка загрузки расписания", str(e))

    def create_training(self):
        try:
            client_id = self.cmb_client.currentData()
            trainer_id = self.cmb_trainer.currentData()
            hall_id = self.cmb_hall.currentData()
            name = self.inp_training_name.text()
            
            # FIX: Зависимый от локали text() заменен на стабильный формат QDateTime
            dt = self.inp_datetime.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            amount = self.inp_amount.value()

            if not name or not dt:
                QMessageBox.warning(self, "Ошибка", "Заполните название и дату/время.")
                return

            tid = self.sch_svc.create_training(
                client_id=client_id,
                trainer_id=trainer_id,
                hall_id=hall_id,
                training_name=name,
                training_datetime=dt,
                amount=amount,
                log_employee_id=self.user["id"]
            )
            QMessageBox.information(self, "Успех", f"Запись создана. ID: {tid}")
            self.load_schedule()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


class ReportsTab(QWidget):
    """Формирование и экспорт отчётов."""
    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)
        self.user = current_user
        self.rep_svc = ReportService()
        self.exp_svc = ReportExportService()
        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout(self)

        # --- Отчёт по активным клиентам ---
        grp_active = QGroupBox("Активные клиенты")
        v1 = QVBoxLayout(grp_active)
        self.tbl_active = QTableWidget()
        self.tbl_active.setColumnCount(6)
        self.tbl_active.setHorizontalHeaderLabels(["Клиент", "Телефон", "Абонемент", "Начало", "Окончание", "Статус"])
        v1.addWidget(self.tbl_active)
        h1 = QHBoxLayout()
        btn_load_active = QPushButton("Загрузить")
        btn_load_active.clicked.connect(self.load_active_clients)
        btn_pdf_active = QPushButton("Экспорт в PDF")
        btn_pdf_active.clicked.connect(lambda: self.export_pdf("active"))
        btn_xlsx_active = QPushButton("Экспорт в Excel")
        btn_xlsx_active.clicked.connect(lambda: self.export_excel("active"))
        h1.addWidget(btn_load_active)
        h1.addWidget(btn_pdf_active)
        h1.addWidget(btn_xlsx_active)
        v1.addLayout(h1)
        main.addWidget(grp_active)

        # --- Отчёт по выручке ---
        grp_rev = QGroupBox("Выручка за период")
        v2 = QVBoxLayout(grp_rev)
        h_dates = QHBoxLayout()
        self.inp_start = QDateEdit()
        self.inp_start.setCalendarPopup(True)
        self.inp_start.setDate(QDate.currentDate().addMonths(-1))
        self.inp_start.setDisplayFormat("yyyy-MM-dd")
        self.inp_end = QDateEdit()
        self.inp_end.setCalendarPopup(True)
        self.inp_end.setDate(QDate.currentDate())
        self.inp_end.setDisplayFormat("yyyy-MM-dd")
        h_dates.addWidget(QLabel("С:"))
        h_dates.addWidget(self.inp_start)
        h_dates.addWidget(QLabel("По:"))
        h_dates.addWidget(self.inp_end)
        v2.addLayout(h_dates)

        self.lbl_revenue = QLabel("Выручка: —")
        self.lbl_revenue.setStyleSheet("font-size: 14px; font-weight: bold;")
        v2.addWidget(self.lbl_revenue)

        h2 = QHBoxLayout()
        btn_calc = QPushButton("Рассчитать")
        btn_calc.clicked.connect(self.calc_revenue)
        btn_pdf_rev = QPushButton("Экспорт в PDF")
        btn_pdf_rev.clicked.connect(lambda: self.export_pdf("revenue"))
        btn_xlsx_rev = QPushButton("Экспорт в Excel")
        btn_xlsx_rev.clicked.connect(lambda: self.export_excel("revenue"))
        h2.addWidget(btn_calc)
        h2.addWidget(btn_pdf_rev)
        h2.addWidget(btn_xlsx_rev)
        v2.addLayout(h2)
        main.addWidget(grp_rev)

        # --- Журнал посещений ---
        grp_visits = QGroupBox("Журнал посещений")
        v3 = QVBoxLayout(grp_visits)
        self.tbl_visits_rep = QTableWidget()
        self.tbl_visits_rep.setColumnCount(4)
        self.tbl_visits_rep.setHorizontalHeaderLabels(["Клиент", "Вход", "Выход", "Длительность (мин)"])
        v3.addWidget(self.tbl_visits_rep)
        h3 = QHBoxLayout()
        btn_load_visits = QPushButton("Загрузить")
        btn_load_visits.clicked.connect(self.load_visit_log)
        btn_pdf_visits = QPushButton("Экспорт в PDF")
        btn_pdf_visits.clicked.connect(lambda: self.export_pdf("visits"))
        btn_xlsx_visits = QPushButton("Экспорт в Excel")
        btn_xlsx_visits.clicked.connect(lambda: self.export_excel("visits"))
        h3.addWidget(btn_load_visits)
        h3.addWidget(btn_pdf_visits)
        h3.addWidget(btn_xlsx_visits)
        v3.addLayout(h3)
        main.addWidget(grp_visits)

        # Статусная строка
        self.lbl_status = QLabel("Готов к работе")
        main.addWidget(self.lbl_status)

    def load_active_clients(self):
        try:
            data = self.rep_svc.get_active_clients()
            self.tbl_active.setRowCount(len(data))
            for i, row in enumerate(data):
                self.tbl_active.setItem(i, 0, QTableWidgetItem(row.get("ClientFullName", "")))
                self.tbl_active.setItem(i, 1, QTableWidgetItem(row.get("ClientPhone", "")))
                self.tbl_active.setItem(i, 2, QTableWidgetItem(row.get("SubscriptionType", "")))
                self.tbl_active.setItem(i, 3, QTableWidgetItem(str(row.get("StartDate", ""))))
                self.tbl_active.setItem(i, 4, QTableWidgetItem(str(row.get("EndDate", ""))))
                self.tbl_active.setItem(i, 5, QTableWidgetItem(row.get("ContractStatus", "")))
            self.lbl_status.setText(f"Активных клиентов: {len(data)}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def calc_revenue(self):
        try:
            start = self.inp_start.text()
            end = self.inp_end.text()
            rev = self.rep_svc.get_revenue(start, end)
            self.lbl_revenue.setText(f"Выручка за {start} — {end}: {rev:,.2f} руб.")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def load_visit_log(self):
        try:
            start = self.inp_start.text()
            end = self.inp_end.text()
            data = self.rep_svc.get_visit_log(start, end)
            self.tbl_visits_rep.setRowCount(len(data))
            for i, row in enumerate(data):
                self.tbl_visits_rep.setItem(i, 0, QTableWidgetItem(row.get("ClientFullName", "")))
                self.tbl_visits_rep.setItem(i, 1, QTableWidgetItem(str(row.get("CheckInTime", ""))))
                self.tbl_visits_rep.setItem(i, 2, QTableWidgetItem(str(row.get("CheckOutTime", ""))))
                self.tbl_visits_rep.setItem(i, 3, QTableWidgetItem(str(row.get("DurationMinutes", ""))))
            self.lbl_status.setText(f"Посещений за период: {len(data)}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def export_pdf(self, report_type: str):
        try:
            if report_type == "active":
                data = self.rep_svc.get_active_clients()
                title = "Список активных клиентов"
            elif report_type == "revenue":
                start = self.inp_start.text()
                end = self.inp_end.text()
                data = [{"Период": f"{start} — {end}", "Выручка": self.rep_svc.get_revenue(start, end)}]
                title = f"Отчёт по выручке ({start} — {end})"
            else:  # visits
                start = self.inp_start.text()
                end = self.inp_end.text()
                data = self.rep_svc.get_visit_log(start, end)
                title = f"Журнал посещений ({start} — {end})"

            path = self.exp_svc.export_pdf(data, title)
            QMessageBox.information(self, "Успех", f"PDF сохранён:\n{path}")
            self.lbl_status.setText(f"PDF: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", str(e))

    def export_excel(self, report_type: str):
        try:
            if report_type == "active":
                data = self.rep_svc.get_active_clients()
                title = "Список активных клиентов"
            elif report_type == "revenue":
                start = self.inp_start.text()
                end = self.inp_end.text()
                data = [{"Период": f"{start} — {end}", "Выручка": self.rep_svc.get_revenue(start, end)}]
                title = f"Отчёт по выручке ({start} — {end})"
            else:  # visits
                start = self.inp_start.text()
                end = self.inp_end.text()
                data = self.rep_svc.get_visit_log(start, end)
                title = f"Журнал посещений ({start} — {end})"

            path = self.exp_svc.export_excel(data, title)
            QMessageBox.information(self, "Успех", f"Excel сохранён:\n{path}")
            self.lbl_status.setText(f"Excel: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", str(e))