import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

from database import Database
from LoginWindow import LoginWindow
from ProductListAdministrator import ProductListWindow


class ApplicationController:
    def __init__(self, database_manager):
        self.login_window = None
        self.db_manager = database_manager
        self.current_window = None

    def start_application(self):
        self.login_window = LoginWindow(self.db_manager, self)
        self.login_window.show()

    def open_product_list(self, user_role, username):
        if self.login_window:
            self.login_window.close()

        self.current_window = None

        if user_role == 4:
            self.current_window = ProductListWindow(self.db_manager)
        elif user_role in (3, 1, 2):
            self.current_window = ProductListWindow(self.db_manager)
        else:
            QMessageBox.critical(None, "Ошибка", "Неизвестная роль пользователя.")
            return

        if self.current_window:
            self.current_window.setWindowTitle(f"Список товаров (Пользователь: {username}, Роль: {user_role})")
            self.current_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
 #   app.setStyle('Fusion')
#    background-color: white;
#    color: black; для белой темы сунуть внутрь Qwidget
    app.setStyleSheet("""
    QWidget {
    font-family: "Times New Roman", Times, serif;
    font-size: 15px;
}

QPushButton {
    background-color: #7FFF00;
    border: 1.5px outset green;
    padding: 5px;
}

QPushButton:hover {
    background-color: #00FA9A;
}

QListWidget::item:selected {
    background: #00FA9A;
}

QLineEdit {
    border: 1px solid black;
    padding: 1.5px;
}

QLineEdit:focus {
    border-color: #00FA9A;
}

QComboBox {
    padding: 1.5px;
    border: 1.5px outset #7FFF00;
}

QComboBox:focus {
    border: 1.5px outset #00FA9A;
}

QListWidget {
    border: 3px outset green;
}

    """)

    DB_NAME = "shoes_shop"
    DB_USER = "postgres"
    DB_PASSWORD = "admin"

    db_manager = Database(
        dbname = DB_NAME,
        user = DB_USER,
        password = DB_PASSWORD,
        host = 'localhost',
        port = '5433'
    )

    db_manager.connect()

    controller = ApplicationController(db_manager)
    controller.start_application()

    sys.exit(app.exec())