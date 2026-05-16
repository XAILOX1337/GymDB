from PyQt6.QtWidgets import QMainWindow, QTabWidget, QLabel, QStatusBar, QMessageBox
from PyQt6.QtCore import Qt
from core.services.backup_service import BackupService
from gui.tabs import AdminTab, ManagerTab, TrainerTab, ScheduleCreateTab, ReportsTab

class MainWindow(QMainWindow):
    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Спортклуб — {user['name']} ({user['position']})")
        self.setMinimumSize(1366, 768)
        self._build_ui()
        self._run_auto_backup()

        

    def _build_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        access = self.user.get("access_level", 0)

        # Согласно init.sql: Administrator=5, Manager=4, Trainer=3, Receptionist=2, Cleaner=1
        if access >= 5:
            self.tab_admin = AdminTab(self.user)
            self.tabs.addTab(self.tab_admin, "Администрирование")

        if access >= 4:
            self.tab_manager = ManagerTab(self.user)
            self.tabs.addTab(self.tab_manager, "Менеджер")
        
            # Менеджер может формировать отчёты
            self.tab_reports = ReportsTab(self.user)
            self.tabs.addTab(self.tab_reports, "Отчёты")

        if access >= 3:
            self.tab_trainer = TrainerTab(self.user)
            self.tabs.addTab(self.tab_trainer, "Тренер")
            # Тренер может создавать расписание
            self.tab_schedule_create = ScheduleCreateTab(self.user)
            self.tabs.addTab(self.tab_schedule_create, "Запись на занятие")

        if self.tabs.count() == 0:
            QMessageBox.critical(self, "Ошибка прав", "Нет доступных модулей для вашей роли.")
            self.close()

        self.status = QStatusBar()
        self.status.showMessage(f"Роль: {self.user['position']} | Уровень доступа: {access}")
        self.setStatusBar(self.status)

    def _run_auto_backup(self):
        try:
            bs = BackupService()
            path = bs.auto_backup()
            self.status.showMessage(f"Роль: {self.user['position']} | Последний бэкап: {path}", 5000)
        except Exception as e:
            print(f"Автобэкап пропущен: {e}")