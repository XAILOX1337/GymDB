from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from core.services.auth_service import AuthService

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация — Спортклуб")
        self.setFixedSize(400, 220)
        self.user = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        lbl_title = QLabel("Вход в систему управления спортклубом")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        self.inp_login = QLineEdit()
        self.inp_login.setPlaceholderText("Логин")
        layout.addWidget(self.inp_login)

        self.inp_password = QLineEdit()
        self.inp_password.setPlaceholderText("Пароль")
        self.inp_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.inp_password)

        btn_layout = QHBoxLayout()
        self.btn_login = QPushButton("Войти")
        self.btn_login.setDefault(True)
        self.btn_login.clicked.connect(self._do_login)
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_login)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def _do_login(self):
        auth = AuthService()
        user = auth.authenticate(self.inp_login.text(), self.inp_password.text())
        if user:
            self.user = user
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль.")