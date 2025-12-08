from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QDialog, QMessageBox, QLineEdit, QPushButton, QComboBox, QTextEdit

from product_add_edit import Ui_Dialog


class AddProductWindow(QDialog, Ui_Dialog):

    product_added = QtCore.pyqtSignal()

    def __init__(self, database_manager, parent=None):
        super().__init__(parent)
        self.db_manager = database_manager
        self.is_editing = False
        self.current_article = None

        self.setupUi(self)
        self.connect_signals()

        self.setWindowTitle("Добавление нового товара")
        self.articul_input.setReadOnly(False)

    def connect_signals(self):
        self.save_button.clicked.connect(self.save_product_data)
        self.cancel_button.clicked.connect(self.close)

    def load_product_data(self, product_data):
        self.is_editing = True
        self.current_article = product_data.get('product_article')

        self.setWindowTitle(f"Редактирование: {self.current_article}")

        self.articul_input.setText(self.current_article)
        self.articul_input.setReadOnly(True)
        self.name_input.setText(product_data.get('product_name', ''))
        self.description_input.setText(product_data.get('product_description', ''))
        self.provider_input.setText(product_data.get('supplier_name', ''))
        self.price_input.setText(str(product_data.get('product_cost', 0.0)))
        self.metric_input.setText(product_data.get('unit_name', ''))
        self.quantity_input.setText(str(product_data.get('product_quantity_stock', 0)))
        self.discount_input.setText(str(product_data.get('product_discount_amount', 0)))

    def get_form_data(self):
        data = {
            'product_article': self.articul_input.text().strip(),
            'product_name': self.name_input.text().strip(),
            'product_description': self.description_input.toPlainText().strip(),
            'category_name': self.category_input.currentText(),
            'manufacturer_name': self.maker_input.currentText(),
            'supplier_name': self.provider_input.text().strip(),

            'product_cost': self.price_input.text().strip(),
            'unit_name': self.metric_input.text().strip(),
            'product_quantity_stock': self.quantity_input.text().strip(),
            'product_discount_amount': self.discount_input.text().strip(),
        }
        return data

    def validate_data(self, data):
        if not data.get('product_name'):
            QMessageBox.warning(self, "Ошибка", "Необходимо указать наименование товара.")
            return False
        if not data.get('product_article'):
            QMessageBox.warning(self, "Ошибка", "Необходимо указать артикул товара.")
            return False

        try:
            float(data['product_cost'])
            int(data['product_quantity_stock'])
            int(data['product_discount_amount'])
        except ValueError:
            QMessageBox.critical(self, "Ошибка ввода", "Поля Цена, Количество и Скидка должны быть числами.")
            return False

        return True

    def save_product_data(self):
        data = self.get_form_data()

        if not self.validate_data(data):
            return

        try:
            data['product_cost'] = float(data['product_cost'])
            data['product_quantity_stock'] = int(data['product_quantity_stock'])
            data['product_discount_amount'] = int(data['product_discount_amount'])

            if self.is_editing:
                success = self.db_manager.update_product(data)
            else:
                success = self.db_manager.add_product(data)

            if success:
                QMessageBox.information(self, "Успех", "Товар успешно сохранен!")
                self.product_added.emit()
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось сохранить данные в базу.")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Критическая ошибка при сохранении: {e}")