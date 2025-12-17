# AddAndEditOrderWindow.py
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QMessageBox

from Ui_python.order_add_editui import Ui_order_edit


class AddEditOrderWindow(QDialog, Ui_order_edit):
    data_saved = QtCore.pyqtSignal()

    def __init__(self, database, mode='add', order_id=None, parent=None):
        super().__init__(parent)
        self.db_manager = database
        self.mode = mode
        self.order_id = order_id  # Это ЧИСЛО (int) или None
        self.setupUi(self)
        if mode == "add":
            self.label_6.setText('Добавление заказа')

        self.articul_input.setReadOnly(True)
        self.load_reference_data()

        if self.mode == 'edit' and self.order_id is not None:
            self.load_order_data()
        else:
            self.articul_input.setReadOnly(False)

        self.save_button.clicked.connect(self.save_data)
        self.cancel_button.clicked.connect(self.reject)

    def load_order_data(self):
        # Получаем данные из БД по числовому ID
        data = self.db_manager.get_order_by_id(self.order_id)
        if data:
            # Отображаем сгенерированный артикул (из product_details) в поле ввода
            # Убедитесь, что get_order_by_id в database.py тоже возвращает это поле
            art_text = data.get('product_details', 'Артикул недоступен')
            self.articul_input.setText(str(art_text))

            # Установка статуса и адреса по ID
            idx_s = self.status_input.findData(data.get('order_status_id'))
            if idx_s >= 0: self.status_input.setCurrentIndex(idx_s)

            idx_p = self.pvz_adress.findData(data.get('pvz_id'))
            if idx_p >= 0: self.pvz_adress.setCurrentIndex(idx_p)

    def load_reference_data(self):
        self.status_input.clear()
        self.pvz_adress.clear()
        for s in self.db_manager.get_all_statuses():
            self.status_input.addItem(s['name'], s['id'])
        for a in self.db_manager.get_all_pvz_addresses():
            self.pvz_adress.addItem(a['address'], a['id'])

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
                success = self.db_manager.add_new_order(data)
                if success:
                    QMessageBox.information(self, "Успех", "Заказ успешно добавлен!")
            else:  # mode == 'edit'
                success = self.db_manager.update_order(self.order_id, data)
                if success:
                    QMessageBox.information(self, "Успех", f"Заказ #{self.order_id} успешно обновлен!")

            # ... (пропуск обработки success и закрытия окна)
            if success:
                self.data_saved.emit()
                self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось сохранить данные: {e}")