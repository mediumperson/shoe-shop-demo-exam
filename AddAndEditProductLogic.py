import os
import shutil

from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap, QCloseEvent, QIcon
from PyQt6.QtWidgets import QDialog, QMessageBox, QFileDialog

from product_add_edit_ui import Ui_Dialog
IMAGE_FOLDER = 'C:\\Users\\nightmare\\PycharmProjects\\FinalProject\\images'

class AddProductWindow(QDialog, Ui_Dialog):

    product_added = QtCore.pyqtSignal()

    old_photo_path: str | None = None
    new_photo_path: str | None = None

    def __init__(self, database_manager, parent=None):
        super().__init__(parent)
        self.db_manager = database_manager
        self.is_editing = False
        self.current_article = None


        self.old_photo_path = None
        self.new_photo_path = None

        self.setupUi(self)
        self.connect_signals()

        self.setWindowTitle("Добавление нового товара")
        self.articul_input.setReadOnly(False)

    def connect_signals(self):
        self.save_button.clicked.connect(self.save_product_data)
        self.cancel_button.clicked.connect(self.close)
        self.download_photo.clicked.connect(self.download_photo_handler)

    def load_product_data(self, product_data):
        self.is_editing = True
        self.current_article = product_data.get('product_article')

        self.setWindowIcon(QIcon('C:\\Users\\nightmare\\PycharmProjects\\FinalProject\\images\\Icon.png'))
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

        # 💡 ЛОГИКА ФОТО: Сохраняем путь к старой фотографии
        # Мы используем 'product_photo' из данных БД, которая содержит только имя файла (например, 'shoe.png')
        photo_filename = product_data.get('product_photo')

        if photo_filename:
            # old_photo_path - это полный путь к файлу в папке проекта, например, 'images/shoe.png'
            self.old_photo_path = os.path.join(IMAGE_FOLDER, photo_filename)
            self.set_photo(self.old_photo_path)
        else:
            self.set_photo(None)  # Установить дефолтную заглушку

    def closeEvent(self, event: QCloseEvent):
        """Обрабатывает событие закрытия окна (нажатие на крестик)."""

        # 1. Проверяем, были ли внесены изменения
        # 💡 ВАЖНО: Вам нужно добавить логику проверки изменений (например, self.is_data_modified)
        # Если вы всегда хотите сохранять при закрытии, можете пропустить эту проверку.


    def set_photo(self, image_path):

        self.photo.clear()

        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)

            if pixmap.isNull():
                # Если файл найден, но загрузить не удалось (неверный формат)
                self.photo.setText("Ошибка: Неверный формат фото")
                return

            self.photo.setPixmap(pixmap)
            self.photo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        else:
            self.photo.setText("Нет фото")

    def download_photo_handler(self):

        temp_photo_path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать фотографию", "",
            "Файлы изображений (*.png *.jpg *.jpeg *.webp)"
        )

        # [cite_start]Проверяем, был ли файл выбран [cite: 4]
        if temp_photo_path:
            # Сохраняем путь к выбранному файлу (еще не скопирован)
            self.new_photo_path = temp_photo_path
            # Немедленно отображаем новое фото для превью
            self.set_photo(self.new_photo_path)
        else:
            return

    def _handle_photo_file(self) -> str | None:
        if not self.new_photo_path:
            if self.old_photo_path:
                return os.path.basename(self.old_photo_path)
            return None  # Нет ни нового, ни старого фото

        base_name = os.path.basename(self.new_photo_path)
        destination_path = os.path.join(IMAGE_FOLDER, base_name)

        if self.is_editing and self.old_photo_path and self.old_photo_path != destination_path:
            if os.path.exists(self.old_photo_path):
                os.remove(self.old_photo_path)
                    # Не блокируем операцию, так как копирование может быть успешным

        # 2. Копирование нового фото
        try:
            shutil.copy2(self.new_photo_path, destination_path)

            # Сбрасываем new_photo_path, чтобы при повторном сохранении не копировать файл снова
            self.new_photo_path = None

            return base_name  # Возвращаем имя файла для записи в БД

        except Exception as e:
            QMessageBox.critical(self, "Ошибка фото", f"Не удалось скопировать файл изображения: {e}")

            # Если копирование не удалось, возвращаем None, чтобы в БД не сохранилось неверное имя
            # Если это режим редактирования, можно вернуть старое имя:
            if self.is_editing and self.old_photo_path:
                return os.path.basename(self.old_photo_path)

            return None

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

        photo_filename = self._handle_photo_file()
        data['product_photo'] = photo_filename

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

