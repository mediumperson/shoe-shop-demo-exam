from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QWidget, QMessageBox
from PyQt6.QtGui import QColor
from product_list_administrator_ui import ProductListAdministratorWindow
from AddAndEditProductLogic import AddProductWindow
from ProductCardWidget import ProductCardWidget

IMAGE_FOLDER = 'C:\\Users\\nightmare\\PycharmProjects\\FinalProject\\images'



class ProductListWindow(QMainWindow, ProductListAdministratorWindow):
    product_selection_changed = QtCore.pyqtSignal(str)
    COLOR_OUT_OF_STOCK = QColor(173, 216, 230)
    SELECTION_STYLE_COLOR = "'#00FA9A'"

    selected_card_widget: QWidget | None = None
    selected_card_article: str | None = None

    def __init__(self, database, user_role, username, parent=None):
        super().__init__(parent)
        self.db_manager = database
        self.edit_window = None
        self.add_window = None
        self.selected_card_widget = None
        self.selected_card_article = None
        self.current_user_role = user_role
        print(self.current_user_role)
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
        self.label_2.setText(username)

        if self.current_user_role == 1 or 4:
            self.search.show()
            self.label.show()
            self.dillers.show()
            self.label_4.show()
            self.storage.show()
            self.orders.show()
            self.remove_product.show()
            self.add_product.show()
        elif self.current_user_role == 2:
            self.search.show()
            self.label.show()
            self.dillers.show()
            self.label_4.show()
            self.storage.show()
            self.orders.show()



    def handle_product_card_click(self, article: str, clicked_widget: ProductCardWidget):
        """
        Обрабатывает клик:
        1. Если кликнута выделенная карточка (повторный клик) -> Редактирование.
        2. Если кликнута новая карточка -> Выделение (снятие выделения с предыдущей).
        """

        # 1. ПОВТОРНЫЙ КЛИК (Редактирование)
        # Проверяем, совпадает ли кликнутый виджет с текущим выделенным
        if clicked_widget == self.selected_card_widget:
            print(f"Повторный клик по {article}: Открываем редактирование.")

            # Снимаем выделение
            clicked_widget.set_selected(False)
            self.selected_card_widget = None
            self.selected_card_article = None

            # 💡 Вызываем метод открытия окна редактирования
            self.open_edit_product_screen(article)

        # 2. ОДИНОЧНЫЙ/НОВЫЙ КЛИК (Выделение)
        else:
            print(f"Новый клик по {article}: Выделяем.")

            # Снимаем выделение с предыдущей карточки (если она была)
            if self.selected_card_widget:
                self.selected_card_widget.set_selected(False)

            # Выделяем новую карточку
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

        # 4. Настройка и отображение окна
        self.add_window.setWindowFlag(QtCore.Qt.WindowType.Window)
        self.add_window.setParent(None)
        self.add_window.setWindowTitle("Добавление нового товара")
        self.add_window.show()
        self.add_window.activateWindow()

    def get_search_params(self):
        params = {}

        # 1. Поиск (self.search - QLineEdit)
        search_term = self.search.text().strip()
        # Проверка гарантирует, что при пустом поле ввода, ключ 'search_term' не попадает в params
        if search_term:
            params['search_term'] = search_term

        # 2. Поставщик (self.dillers - QComboBox)
        supplier = self.dillers.currentText()
        if supplier and supplier.strip() != "Все поставщики":
            params['supplier_name'] = supplier

        # 3. Количество на складе (self.storage - QComboBox)
        stock_option = self.storage.currentText().strip()
        params['stock_filter'] = stock_option

        # Если все поля пустые, возвращается {} — это сбрасывает поиск
        return params

    def handle_delete_product(self):
        # ... (код остается без изменений)
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
        # 1. Получаем данные товара из БД
        product_data = self.db_manager.get_product_by_article(article)

        if not product_data:
            QMessageBox.critical(self, "Ошибка", f"Товар с артикулом {article} не найден в базе данных.")
            return

        if self.edit_window:
            self.edit_window.product_added.disconnect()
            self.edit_window.close()
            self.edit_window.deleteLater()
            self.edit_window = None

        # 3. Создание окна редактирования
        self.edit_window = AddProductWindow(self.db_manager)

        # 4. Загрузка данных в форму (ключевой шаг)
        self.edit_window.load_product_data(product_data)

        # 5. Подключение сигнала для обновления списка после сохранения
        try:
            self.edit_window.product_added.connect(self.load_products)
        except Exception as e:
            print(f"Ошибка подключения сигнала (edit_product): {e}")

        try:
            self.edit_window.finished.connect(self.handle_edit_window_close_unselect)

        except Exception as e:
            print(f"Ошибка подключения finished: {e}")
        # 6. Настройка и отображение окна
        self.edit_window.setWindowFlag(QtCore.Qt.WindowType.Window)
        self.edit_window.setParent(None)
        self.edit_window.show()
        self.edit_window.activateWindow()

    def connect_signals(self):
        self.exit_product_list.clicked.connect(self.close)
        self.add_product.clicked.connect(self.open_add_product_screen)
        self.remove_product.clicked.connect(self.handle_delete_product)
        self.orders.clicked.connect(lambda: QMessageBox.information(self, "Действие", "Окно заказов"))

        self.search.textChanged.connect(self.load_products)

        self.dillers.currentIndexChanged.connect(self.load_products)

        self.storage.currentIndexChanged.connect(self.load_products)


    def clear_product_list(self):
        # ... (код остается без изменений)
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
        # ... (код остается без изменений)
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
        """
        Загружает список поставщиков из БД и заполняет self.dillers.
        """
        self.dillers.clear()

        # 1. Добавляем нейтральный элемент
        self.dillers.addItem("Все поставщики")

        # 2. Получаем актуальный список из БД
        suppliers = self.db_manager.get_all_suppliers()

        # 3. Добавляем поставщиков
        for supplier in suppliers:
            self.dillers.addItem(supplier)

        # Устанавливаем нейтральный элемент как текущий
        self.dillers.setCurrentIndex(0)

    def display_products(self, products):
        # ... (код остается без изменений)
        for product in products:
            card = ProductCardWidget(product)
            card.product_clicked.connect(self.handle_product_card_click)
            self.verticalLayout.addWidget(card)
        self.verticalLayout.addStretch(1)

