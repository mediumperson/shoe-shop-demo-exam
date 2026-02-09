from PyQt6 import QtCore
from PyQt6.QtWidgets import QMainWindow, QWidget, QMessageBox
from PyQt6.QtGui import QColor, QIcon
from Ui_python.product_list_administrator import Ui_ProductListAdministratorWindow
from Logic.AddAndEditProductLogic import AddProductWindow
from Logic.ProductCardWidget import ProductCardWidget
from Logic.OrderListWindow import OrderListWindow
from Logic.TestLogic import Test

IMAGE_FOLDER = 'C:\\Users\\nightmare\\PycharmProjects\\FinalProject\\images'

class ProductListWindow(QMainWindow, Ui_ProductListAdministratorWindow):
    product_selection_changed = QtCore.pyqtSignal(str)
    logout_requested = QtCore.pyqtSignal()
    COLOR_OUT_OF_STOCK = QColor(173, 216, 230)
    SELECTION_STYLE_COLOR = "'#00FA9A'"

    selected_card_widget: QWidget | None = None
    selected_card_article: str | None = None

    def __init__(self, database, user_role, username, parent=None):
        super().__init__(parent)
        self.db_manager = database
        self.edit_window = None
        self.add_window = None
        self.test_window = None
        self.selected_card_widget = None
        self.selected_card_article = None
        self.current_user_role = user_role
        self.setWindowTitle(f"Каталог товаров")
        self.setWindowIcon(QIcon('C:\\Users\\nightmare\\PycharmProjects\\FinalProject\\images\\Icon.png'))
        self.setupUi(self)
        self.load_suppliers()
        self.verticalLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.clear_product_list()
        self.connect_signals()
        self.load_products()

        self.search.hide()
        self.label.hide()
        self.dillers.hide()
        self.label_4.hide()
        self.storage.hide()
        self.orders.hide()
        self.remove_product.hide()
        self.add_product.hide()
        self.test.hide()
        self.label_2.setText(username)

        if self.current_user_role == 1 or 4:
            self.search.show()
            self.label.show()
            self.dillers.show()
            self.label_4.show()
            self.storage.show()
            self.orders.show()
            self.test.show()
            self.remove_product.show()
            self.add_product.show()
        elif self.current_user_role == 2:
            self.search.show()
            self.label.show()
            self.dillers.show()
            self.label_4.show()
            self.storage.show()
            self.orders.show()

    def execute_silent_test(self):
        self.tester = Test(self.db_manager)
        self.tester.positive_test()
        self.load_products()
        QMessageBox.information(self, "Успех", "Тестовый товар добавлен в базу данных!")

    def handle_product_card_click(self, article: str, clicked_widget: ProductCardWidget):
        if clicked_widget == self.selected_card_widget:
            clicked_widget.set_selected(False)
            self.selected_card_widget = None
            self.selected_card_article = None
            self.open_edit_product_screen(article)
        else:
            if self.selected_card_widget:
                self.selected_card_widget.set_selected(False)
            clicked_widget.set_selected(True)
            self.selected_card_widget = clicked_widget
            self.selected_card_article = article

    def open_add_product_screen(self):
        if self.add_window:
            self.add_window.product_added.disconnect()
            self.add_window.close()
            self.add_window.deleteLater()
            self.add_window = None
        self.add_window = AddProductWindow(self.db_manager)
        try:
            self.add_window.product_added.connect(self.load_products)
            self.add_window.product_added.connect(self.load_suppliers)
        except Exception as e:
            print(f"Ошибка подключения сигнала (add_product): {e}")
        self.add_window.setWindowFlag(QtCore.Qt.WindowType.Window)
        self.add_window.setParent(None)
        self.add_window.setWindowIcon(QIcon('/images/Icon.png'))
        self.add_window.setWindowTitle("Добавление товара")
        self.add_window.show()
        self.add_window.activateWindow()

    def get_search_params(self):
        params = {}
        search_term = self.search.text().strip()
        if search_term:
            params['search_term'] = search_term
        supplier = self.dillers.currentText()
        if supplier and supplier.strip() != "Все поставщики":
            params['supplier_name'] = supplier
        stock_option = self.storage.currentText().strip()
        params['stock_filter'] = stock_option
        return params

    def handle_delete_product(self):
        if not self.selected_card_article:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите товар для удаления.")
            return
        article_to_delete = self.selected_card_article
        reply = QMessageBox.question(self, 'Подтверждение',
                                     f"Вы уверены, что хотите удалить товар с артикулом {article_to_delete}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.db_manager.delete_product_by_article(article_to_delete):
                QMessageBox.information(self, "Успех", f"Товар {article_to_delete} успешно удален!")
                self.load_products()

    def request_logout(self):
        self.logout_requested.emit()
        self.close()

    def open_edit_product_screen(self, article: str):
        if self.current_user_role == 1:
            product_data = self.db_manager.get_product_by_article(article)
            if not product_data:
                QMessageBox.critical(self, "Ошибка", f"Товар с артикулом {article} не найден в базе данных.")
                return
            if self.edit_window:
                self.edit_window.product_added.disconnect()
                self.edit_window.close()
                self.edit_window.deleteLater()
                self.edit_window = None
            self.edit_window = AddProductWindow(self.db_manager)
            self.edit_window.load_product_data(product_data)
            try:
                self.edit_window.product_added.connect(self.load_products)
            except Exception as e:
                print(f"Ошибка подключения сигнала (edit_product): {e}")
            self.edit_window.setWindowFlag(QtCore.Qt.WindowType.Window)
            self.edit_window.setParent(None)
            self.edit_window.show()
            self.edit_window.activateWindow()

    def connect_signals(self):
        self.exit_product_list.clicked.connect(self.logout_requested)
        self.add_product.clicked.connect(self.open_add_product_screen)
        self.remove_product.clicked.connect(self.handle_delete_product)
        self.orders.clicked.connect(self.open_orders_screen)

        self.test.clicked.connect(self.open_test_screen)

        self.search.textChanged.connect(self.load_products)
        self.dillers.currentIndexChanged.connect(self.load_products)
        self.storage.currentIndexChanged.connect(self.load_products)

    def open_test_screen(self):
        self.test_window = Test(self.db_manager)
        self.test_window.product_added.connect(self.load_products)
        self.test_window.show()


    def clear_product_list(self):
        self.selected_card_article = None
        self.selected_card_widget = None
        while self.verticalLayout.count():
            item = self.verticalLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self._clear_layout_recursively(item.layout())

    def _clear_layout_recursively(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self._clear_layout_recursively(item.layout())

    def load_products(self):
        self.clear_product_list()
        search_params = self.get_search_params()
        try:
            products = self.db_manager.get_products_by_filter(search_params)
        except Exception as e:
            print(f"Ошибка при получении списка товаров из БД: {e}")
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось загрузить товары: {e}")
            products = []
        if products:
            self.display_products(products)

    def load_suppliers(self):
        self.dillers.clear()
        self.dillers.addItem("Все поставщики")
        suppliers = self.db_manager.get_all_suppliers()
        for supplier in suppliers:
            self.dillers.addItem(supplier)
        self.dillers.setCurrentIndex(0)

    def display_products(self, products):
        for product in products:
            card = ProductCardWidget(product)
            card.product_clicked.connect(self.handle_product_card_click)
            self.verticalLayout.addWidget(card)
        self.verticalLayout.addStretch(1)

    def open_orders_screen(self):
        user_data = {'role': self.current_user_role}
        if not hasattr(self, 'orders_window') or self.orders_window is None:
            self.orders_window = OrderListWindow(
                database=self.db_manager,
                user_data=user_data,
                parent=self
            )
        self.orders_window.show()
        self.orders_window.activateWindow()