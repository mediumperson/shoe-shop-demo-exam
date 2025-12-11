from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QDialog, QMessageBox, QWidget, QVBoxLayout
from PyQt6.QtGui import QColor

from dialog_order_ui import Ui_MainWindow
from OrderCardWidget import OrderCardWidget


class OrderListWindow(QMainWindow, Ui_MainWindow):
    order_data_changed = QtCore.pyqtSignal()

    # Переменные для отслеживания выбранного заказа
    selected_order_widget: QWidget | None = None
    selected_order_id: int | None = None

    def __init__(self, database, user_data: dict, parent=None):
        # ⚠️ Наследуемся от QMainWindow, чтобы соответствовать UI
        super().__init__(parent)
        self.db_manager = database
        self.user_data = user_data
        self.add_edit_order_window = None

        self.setupUi(self)

        # ⚠️ Устанавливаем QVBoxLayout, куда будут добавляться карточки
        # Это verticalLayout_11, который находится внутри scrollAreaWidgetContents_2
        self.orders_vbox_layout = self.verticalLayout_11
        self.orders_vbox_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        # 1. Очистка статических шаблонов и сброс выбора
        self.clear_template_widgets()

        # 2. Подключение сигналов кнопок
        self.connect_signals()

        # 3. Загрузка данных при старте
        self.load_orders()

    # ----------------------------------------------------
    # ИНИЦИАЛИЗАЦИЯ И ОЧИСТКА
    # ----------------------------------------------------

    def connect_signals(self):
        """Подключение всех сигналов UI к функциям-обработчикам."""
        self.order_button_back.clicked.connect(self.close)
        self.order_button_add.clicked.connect(self.open_add_order_screen)
        self.order_button_remove.clicked.connect(self.handle_remove_order)

    def clear_template_widgets(self):
        """
        Удаление статических шаблонных виджетов (widget_order, widget_order_2, ...) из UI.
        """
        self.selected_order_id = None
        self.selected_order_widget = None

        template_widgets = [
            self.widget_order,
            self.widget_order_2,
            self.widget_order_3,
            self.widget_order_4
        ]

        for widget in template_widgets:
            if widget:
                # Удаляем виджет из компоновщика и из памяти
                self.orders_vbox_layout.removeWidget(widget)
                widget.deleteLater()

        self.clear_order_list()

    def clear_order_list(self):
        """Очищает динамическое содержимое QVBoxLayout (список заказов)."""

        # Удаление всех динамически добавленных элементов
        while self.orders_vbox_layout.count():
            item = self.orders_vbox_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    # ----------------------------------------------------
    # ЗАГРУЗКА И ОТОБРАЖЕНИЕ
    # ----------------------------------------------------

    def load_orders(self):
        """Загружает список заказов из БД и отображает их."""
        self.clear_order_list()

        try:
            # Предполагается, что get_all_orders возвращает список словарей
            orders = self.db_manager.get_all_orders()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось загрузить заказы: {e}")
            orders = []

        if orders:
            self.display_orders(orders)

        # Добавляем растяжку в конце списка, чтобы виджеты прилипали к верху
        self.orders_vbox_layout.addStretch(1)

    def display_orders(self, orders: list):
        """Динамически создает и добавляет виджеты заказов в список."""

        for order in orders:
            # Используем кастомный виджет OrderCardWidget
            order_card_widget = OrderCardWidget(order)

            # Подключаем сигнал клика к обработчику
            order_card_widget.order_clicked.connect(self.handle_order_card_click)

            self.orders_vbox_layout.addWidget(order_card_widget)

    # ----------------------------------------------------
    # ОБРАБОТЧИКИ КНОПОК И КЛИКОВ
    # ----------------------------------------------------

    def handle_order_card_click(self, order_id: int, clicked_widget: OrderCardWidget):
        """
        Обрабатывает клик по виджету заказа: выделение или открытие деталей.
        """

        # 1. Проверка на повторный клик (открытие редактирования / снятие выделения)
        if clicked_widget == self.selected_order_widget:
            clicked_widget.set_selected(False)
            self.selected_order_widget = None
            self.selected_order_id = None

            # Открытие окна редактирования по двойному клику
            self.open_edit_order_screen(order_id)
            return

        # 2. Если клик на новом виджете:

        # Снятие выделения с предыдущего, если он был
        if self.selected_order_widget:
            self.selected_order_widget.set_selected(False)

        # Выделение нового виджета
        clicked_widget.set_selected(True)
        self.selected_order_widget = clicked_widget
        self.selected_order_id = order_id

    def open_add_order_screen(self):
        """Открытие окна для создания нового заказа."""
        # ⚠️ Здесь должна быть логика открытия окна AddOrderWindow
        QMessageBox.information(self, "Функционал", "Открытие окна добавления заказа.")
        # if self.add_edit_order_window is None:
        #     self.add_edit_order_window = AddEditOrderWindow(self.db_manager, mode='add')
        #     self.add_edit_order_window.data_saved.connect(self.load_orders)
        # self.add_edit_order_window.show()

    def open_edit_order_screen(self, order_id: int):
        """Открытие окна для редактирования существующего заказа."""
        # ⚠️ Здесь должна быть логика открытия окна AddEditOrderWindow
        QMessageBox.information(self, "Функционал", f"Открытие окна редактирования заказа #{order_id}.")
        # if self.add_edit_order_window is None:
        #     self.add_edit_order_window = AddEditOrderWindow(self.db_manager, mode='edit', order_id=order_id)
        #     self.add_edit_order_window.data_saved.connect(self.load_orders)
        # self.add_edit_order_window.show()

    def handle_remove_order(self):
        """Удаление выбранного заказа."""
        if not self.selected_order_id:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите заказ для удаления.")
            return

        reply = QMessageBox.question(self, 'Подтверждение',
                                     f"Вы уверены, что хотите удалить заказ #{self.selected_order_id}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.db_manager.delete_order_by_id(self.selected_order_id):
                    QMessageBox.information(self, "Успех", f"Заказ #{self.selected_order_id} успешно удален!")
                    self.load_orders()  # Перезагрузка списка
                else:
                    QMessageBox.warning(self, "Предупреждение",
                                        "Заказ не был удален. Возможно, он не существует или произошла ошибка в БД.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", f"Не удалось удалить заказ: {e}")