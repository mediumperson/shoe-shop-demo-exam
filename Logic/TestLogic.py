from PyQt6 import QtCore
from PyQt6.QtWidgets import QDialog, QMessageBox
from Ui_python.test import Ui_Test
from Logic.AddAndEditProductLogic import AddProductWindow
from PyQt6.QtGui import QIcon


class Test(QDialog, Ui_Test):
    product_added = QtCore.pyqtSignal()

    def __init__(self, database_manager, parent=None):
        super().__init__(parent)
        self.db_manager = database_manager
        # 1. Инициализируем наш интерфейс (кнопки positive/negative)
        self.setupUi(self)
        # 2. Создаем "невидимый" экземпляр родительского класса для логики
        self.logic_worker = AddProductWindow(self.db_manager)
        # Подменяем метод получения данных в воркере на наш
        self.logic_worker.get_form_data = self.get_test_data
        # Пробрасываем сигнал успеха наружу
        self.logic_worker.product_added.connect(self.product_added.emit)

        self.current_test_data = {}
        self.connect_signals()
        self.setWindowTitle(f"Тестирование")
        self.setWindowIcon(QIcon('C:\\Users\\nightmare\\PycharmProjects\\FinalProject\\images\\test.jpg'))

    def connect_signals(self):
        self.positive.clicked.connect(self.run_positive_test)
        self.negative.clicked.connect(self.run_negative_test)

    def get_test_data(self):
        return self.current_test_data

    def run_positive_test(self):
        self.current_test_data = {
            'product_article': 'POS_001',
            'product_name': 'Тест Позитив',
            'product_description': 'Корректные данные',
            'category_name': 'Тест',
            'manufacturer_name': 'Тест',
            'supplier_name': 'Тест',
            'product_cost': '1000',
            'unit_name': 'шт',
            'product_quantity_stock': '10',
            'product_discount_amount': '0',
        }
        # Запускаем сохранение через воркер
        self.logic_worker.save_product_data()

    def run_negative_test(self):
        self.current_test_data = {
            'product_article': 'NEG_001',
            'product_name': 'негативный тест',
            'product_description': 'Тест Негатив',
            'category_name': 'Тест',
            'manufacturer_name': 'Тест',
            'supplier_name': 'Тест',
            'product_cost': '-100',
            'unit_name': 'шт',
            'product_quantity_stock': '-5',
            'product_discount_amount': '999',
        }
        self.logic_worker.save_product_data()