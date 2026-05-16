import sys
from PyQt6.QtWidgets import QApplication
from gui.login_dialog import LoginDialog
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    login = LoginDialog()
    if login.exec() != LoginDialog.DialogCode.Accepted:
        sys.exit(0)

    user = login.user
    window = MainWindow(user)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()