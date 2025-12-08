from PyQt6.QtWidgets import QMainWindow, QMessageBox


from login_window import Ui_Login


class LoginWindow(QMainWindow, Ui_Login):

    def __init__(self, db_manager, app_controller, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.db_manager = db_manager
        self.app_controller = app_controller
        self.initial_status_text = self.label_3.text()
        self.login_button.clicked.connect(self.handle_login)
        self.guest_button.clicked.connect(self.handle_guest_login)

    def handle_login(self):
        login = self.login_input.text()
        password = self.password_input.text()

        self.label_3.setText("Проверка...")
        self.label_3.setStyleSheet("")

        user_result = self.db_manager.get_user(login, password)
        user_role, message = user_result if isinstance(user_result, tuple) else (None, "Неизвестная ошибка БД.")

        if user_role:
            self.app_controller.open_product_list(user_role, login)
        else:
            self.label_3.setText(f"Ошибка: {message}")
            self.label_3.setStyleSheet("color: red; font-weight: bold;")
            self.password_input.clear()
            QMessageBox.critical(self, "Ошибка входа", message)

    def handle_guest_login(self):
        guest_role = 2
        guest_username = "Гость"

        self.app_controller.open_product_list(guest_role, guest_username)