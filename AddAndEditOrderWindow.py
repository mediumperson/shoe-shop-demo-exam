# AddAndEditOrderWindow.py

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtGui import QIntValidator, QDoubleValidator

# Импорт вашего сгенерированного UI-класса
# ⚠️ Убедитесь, что имя файла соответствует вашему сгенерированному файлу
from order_add_editui import Ui_order_edit


class AddEditOrderWindow(QDialog, Ui_order_edit):
    # Сигнал, который будет испускаться при успешном сохранении (для обновления списка)
    data_saved = QtCore.pyqtSignal()

    def __init__(self, database, mode='add', order_id=None, parent=None):
        super().__init__(parent)
        self.db_manager = database
        self.mode = mode  # 'add' или 'edit'
        self.order_id = order_id

        # ⚠️ Использование вашего сгенерированного класса
        self.setupUi(self)

        self.setup_window()
        self.connect_signals()

        # Загрузка справочников (статусы, адреса ПВЗ)
        self.load_reference_data()

        if self.mode == 'edit':
            self.load_order_data()

    def setup_window(self):
        """Настройка заголовка и ограничений ввода."""

        if self.mode == 'add':
            self.setWindowTitle("Добавить новый заказ")

            # 1. Получаем следующий ID из БД
            next_id = self.db_manager.get_next_order_id()

            # 2. АРТИКУЛ: Блокируем ввод и устанавливаем прогнозируемый ID
            self.articul_input.setReadOnly(True)
            if next_id is not None:
                self.articul_input.setText(str(next_id))
            else:
                self.articul_input.setText("Ошибка ID")

        else:
            self.setWindowTitle(f"Редактировать заказ #{self.order_id}")
            # АРТИКУЛ: Отображаем текущий ID, блокируем изменение
            self.articul_input.setReadOnly(True)
            self.articul_input.setText(str(self.order_id))

    def connect_signals(self):
        """Подключение кнопок сохранения и отмены."""
        self.save_button.clicked.connect(self.save_data)
        self.cancel_button.clicked.connect(self.reject)  # reject закрывает QDialog


    def load_reference_data(self):
        """Загрузка данных для QComboBox (Статусы, Адреса ПВЗ)"""

        self.status_input.clear()
        self.pvz_adress.clear()

        # 1. Загрузка статусов
        try:
            statuses = self.db_manager.get_all_statuses()
            for status in statuses:
                self.status_input.addItem(status['name'], status['id'])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось загрузить статусы: {e}")

        # 2. Загрузка адресов ПВЗ
        try:
            addresses = self.db_manager.get_all_pvz_addresses()
            for addr in addresses:
                self.pvz_adress.addItem(addr['address'], addr['id'])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось загрузить адреса ПВЗ: {e}")

    # --------------------------------------------------------------------
    # РЕДАКТИРОВАНИЕ (Загрузка)
    # --------------------------------------------------------------------

    def load_order_data(self):
        """Загрузка данных существующего заказа для режима 'edit'."""

        try:
            order_data = self.db_manager.get_order_by_id(self.order_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные заказа: {e}")
            self.close()
            return

        if not order_data:
            QMessageBox.warning(self, "Не найдено", f"Заказ с ID {self.order_id} не найден.")
            self.close()
            return

        # ⚠️ Заполнение полей:

        # QLineEdit: ИСПРАВЛЕНИЕ ОШИБКИ - Преобразование order_code в строку
        order_code_value = order_data.get('order_code')
        if order_code_value is not None:
            self.articul_input.setText(str(order_code_value))
        else:
            self.articul_input.setText('')

        # QDateEdit (Даты должны быть в формате 'yyyy-MM-dd' для корректного преобразования)
        order_date_str = order_data.get('order_date')
        if order_date_str:
            self.date_order.setDate(QtCore.QDate.fromString(order_date_str, "yyyy-MM-dd"))

        delivery_date_str = order_data.get('order_delivery_date')
        if delivery_date_str:
            self.delivery_date.setDate(QtCore.QDate.fromString(delivery_date_str, "yyyy-MM-dd"))

        # QComboBox (Статус)
        status_id = order_data.get('order_status_id')  # Используем 'order_status_id' из get_order_by_id
        if status_id:
            index = self.status_input.findData(status_id)
            if index >= 0:
                self.status_input.setCurrentIndex(index)

        # QComboBox (Адрес ПВЗ)
        pvz_id = order_data.get('pvz_id')
        if pvz_id:
            index = self.pvz_adress.findData(pvz_id)
            if index >= 0:
                self.pvz_adress.setCurrentIndex(index)

    # --------------------------------------------------------------------
    # СОХРАНЕНИЕ
    # --------------------------------------------------------------------

    def get_form_data(self):
        """Сбор данных из формы в словарь."""

        order_data = {
            # В режиме добавления (mode='add') 'order_code' не отправляем, т.к. БД присвоит ID
            # В режиме редактирования (mode='edit') 'order_code' не нужен, т.к. поиск по order_id

            # Получаем ID выбранного статуса
            'status_id': self.status_input.currentData(),
            # Получаем ID выбранного ПВЗ
            'pvz_id': self.pvz_adress.currentData(),

            # Преобразование QDate в строку для БД
            'order_date': self.date_order.date().toString("yyyy-MM-dd"),
            'order_delivery_date': self.delivery_date.date().toString("yyyy-MM-dd"),
        }
        return order_data

    def save_data(self):
        """Сохранение или обновление данных заказа."""

        data = self.get_form_data()

        # Проверка, что ComboBox заполнены
        if data['status_id'] is None or data['pvz_id'] is None:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, выберите Статус и Адрес ПВЗ.")
            return

        success = False
        try:
            if self.mode == 'add':
                # ⚠️ В add_new_order мы не передаем 'order_code'
                success = self.db_manager.add_new_order(data)
                if success:
                    QMessageBox.information(self, "Успех", "Заказ успешно добавлен!")
            else:  # mode == 'edit'
                # ⚠️ В update_order мы передаем order_id и данные
                success = self.db_manager.update_order(self.order_id, data)
                if success:
                    QMessageBox.information(self, "Успех", f"Заказ #{self.order_id} успешно обновлен!")

            # ... (пропуск обработки success и закрытия окна)
            if success:
                self.data_saved.emit()
                self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось сохранить данные: {e}")