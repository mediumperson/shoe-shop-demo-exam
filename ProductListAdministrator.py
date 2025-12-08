from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QWidget, QMessageBox
from PyQt6.QtGui import QColor
from product_list_administrator import ProductListAdministratorWindow
from add_and_edit_product_logic import AddProductWindow  # 👈 Импортируем окно добавления
from product_card_widget import ProductCardWidget

IMAGE_FOLDER = 'C:\\Users\\nightmare\\PycharmProjects\\FinalProject\\images'


class ProductListWindow(QMainWindow, ProductListAdministratorWindow):
    product_selection_changed = QtCore.pyqtSignal(str)
    COLOR_OUT_OF_STOCK = QColor(173, 216, 230)
    SELECTION_STYLE_COLOR = "'#00FA9A'"

    selected_card_widget: QWidget | None = None
    selected_card_article: str | None = None

    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.db_manager = database
        self.edit_window = None
        self.add_window = None

        self.selected_card_widget = None
        self.selected_card_article = None

        self.setupUi(self)
        self.verticalLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.clear_product_list()
        self.connect_signals()
        self.load_products()

    def handle_product_card_click(self, article: str, clicked_widget: ProductCardWidget):
        if article == self.selected_card_article:
            self.open_edit_product_screen(article)
            return

        if self.selected_card_widget:
            try:
                self.selected_card_widget.clickable_container.setStyleSheet(
                    self.selected_card_widget.original_style
                )
            except Exception:
                pass

        self.selected_card_article = article
        self.selected_card_widget = clicked_widget
        selection_style = f"background-color: {self.SELECTION_STYLE_COLOR}; border: 1px solid blue;"
        clicked_widget.clickable_container.setStyleSheet(selection_style)

    def open_add_product_screen(self):

        if self.add_window:
            try:
                self.add_window.product_added.disconnect()
            except Exception:
                pass

            self.add_window.close()
            self.add_window.deleteLater()
            self.add_window = None

        self.add_window = AddProductWindow(self.db_manager)

        try:
            self.add_window.product_added.connect(self.load_products)
        except Exception as e:
            print(f"Ошибка подключения сигнала (add_product): {e}")

        # 4. Настройка и отображение окна
        self.add_window.setWindowFlag(QtCore.Qt.WindowType.Window)
        self.add_window.setParent(None)
        self.add_window.setWindowTitle("Добавление нового товара")
        self.add_window.show()
        self.add_window.activateWindow()

    def handle_delete_product(self):

        # 1. Проверяем, выбран ли товар
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
            else:
                pass

    def open_edit_product_screen(self, article: str):
        QMessageBox.information(self, "Действие", f"Заглушка: Открытие окна редактирования товара: {article}")


    def connect_signals(self):
        self.exit_product_list.clicked.connect(self.close)
        self.add_product.clicked.connect(self.open_add_product_screen)  # 👈 Подключение
        self.remove_product.clicked.connect(self.handle_delete_product)
        self.orders.clicked.connect(lambda: QMessageBox.information(self, "Действие", "Окно заказов"))

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
        try:
            products = self.db_manager.get_all_products()
        except Exception as e:
            print(f"Ошибка при получении списка товаров из БД: {e}")
            products = []
        if products:
            self.display_products(products)

    def display_products(self, products):
        for product in products:
            card = ProductCardWidget(product)
            card.product_clicked.connect(self.handle_product_card_click)
            self.verticalLayout.addWidget(card)
        self.verticalLayout.addStretch(1)