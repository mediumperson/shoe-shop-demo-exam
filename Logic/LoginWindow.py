from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtGui import QIcon


from Ui_python.login_window_ui import Ui_Login



class LoginWindow(QMainWindow, Ui_Login):

    def __init__(self, db_manager, app_controller, parent=None):
        super().__init__(parent)
        self.username = None
        self.setupUi(self)
        self.user_role = None
        self.db_manager = db_manager
        self.app_controller = app_controller
        self.initial_status_text = self.label_3.text()
        self.login_button.clicked.connect(self.handle_login)
        self.guest_button.clicked.connect(self.handle_guest_login)
        self.setWindowTitle(f"Авторизация")
        self.setWindowIcon(QIcon('C:\\Users\\nightmare\\PycharmProjects\\FinalProject\\images\\Icon.png'))

    def handle_login(self):
        login = self.login_input.text()
        password = self.password_input.text()

        self.user_role, self.username = self.db_manager.get_user(login, password)


        if self.user_role:
            self.app_controller.open_product_list(self.user_role, self.username)
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль")
            self.login_input.clear()
            self.password_input.clear()

    def handle_guest_login(self):
        guest_role = 4
        guest_username = "Гость"

        self.app_controller.open_product_list(guest_role, guest_username)