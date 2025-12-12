# main.py (Обновленный ApplicationController)

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

from database import Database
from LoginWindow import LoginWindow
from ProductListWindow import ProductListWindow


class ApplicationController:
    def __init__(self, database_manager):
        self.current_user_role = None
        self.current_user_name = None
        self.login_window = None
        self.db_manager = database_manager
        self.current_window = None

    def start_application(self):
        self.login_window = LoginWindow(self.db_manager, self)
        self.login_window.show()

    def open_product_list(self, user_role, username):
        if self.login_window:
            self.login_window.close()  # Закрываем окно логина при успешном входе

        if self.current_window:
            self.current_window.close()

        self.current_window = None
        self.current_user_role = user_role
        self.current_user_name = username

        # 1. Создаем новое окно ProductListWindow
        self.current_window = ProductListWindow(self.db_manager, self.current_user_role, self.current_user_name)

        self.current_window.logout_requested.connect(self.return_to_login)

        if self.current_window:
            self.current_window.setWindowTitle(f"Список товаров (Пользователь: {username}, Роль: {user_role})")
            self.current_window.show()

    def return_to_login(self):

        # 1. Очищаем текущие данные пользователя и окно
        self.current_user_role = None
        self.current_user_name = None
        self.current_window = None

        # 2. Создаем/показываем новое окно логина
        self.login_window = LoginWindow(self.db_manager, self)
        self.login_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    #    background-color: white;
    #    color: black; для белой темы сунуть внутрь Qwidget
    app.setStyleSheet("""
    QWidget {
    background-color: white;
    color: black; /* Убрал комментарий, так как он не должен быть внутри строки */
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