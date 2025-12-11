import os
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6 import QtCore, QtGui, QtWidgets
from widget2 import Ui_Form  # Предположительно, это ваш UI-файл

# ВАЖНО: Путь должен быть правильным
IMAGE_FOLDER = 'C:\\Users\\nightmare\\PycharmProjects\\FinalProject\\images'


class ProductCardWidget(QWidget, Ui_Form):
    product_clicked = QtCore.pyqtSignal(str, object)

    def __init__(self, product_data, parent=None):
        super().__init__(parent)
        self.selected_style = 'border: 2px solid #00FA9A;'
        self.default_style = 'border: 1px solid black;'
        self.setupUi(self)
        self.product_data = product_data
        self.article = product_data.get('product_article')
        self.original_style = self.widget_7.styleSheet()

        # 💡 КЛЮЧЕВАЯ НАСТРОЙКА: Гарантируем, что виджет фото масштабирует контент
        self.photo_10.setScaledContents(True)
        self.photo_10.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.load_data_to_card()
        self.widget_7.mousePressEvent = self.card_click_handler
        self.widget_7.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.clickable_container = self.widget_7

    def load_data_to_card(self):
        data = self.product_data
        discount = data.get('product_discount_amount', 0)

        category_name = data.get('category_name') or 'Н/Д'
        product_name = data.get('product_name') or 'Наименование не указано'

        self.label_15.setText(f"<b>{category_name}</b> | {product_name}")

        description = data.get('product_description') or 'Нет описания'
        self.label_27.setText(f"Описание товара: {description}")

        self.label_28.setText(f"Производитель: {data.get('manufacturer_name') or 'Н/Д'}")
        self.label_46.setText(f"Поставщик: {data.get('supplier_name') or 'Н/Д'}")
        unit_name = data.get('unit_name') or 'шт.'
        self.label_48.setText(f"Ед. измерения: {unit_name}")
        cost = data.get('product_cost')
        cost = float(cost) if cost is not None else 0.0

        cost_after_sale = cost - (cost * discount / 100)
        price_html = f"Цена: <span style='text-decoration: line-through; color: #FF0000;'>{cost:.2f}</span> <span>  {cost_after_sale:.2f} руб.</span>"
        self.label_47.setText(price_html)
        quantity = data.get('product_quantity_stock')
        quantity = int(quantity) if quantity is not None else 0

        quantity_text = f"Количество на складе: {quantity}"
        self.label_49.setText(quantity_text)


        self.load_product_photo(data.get('product_photo'))

        if quantity == 0:
            self.label_49.setStyleSheet("color: #0000FF; border: 0px solid black;")

        discount_text = f"Скидка:\n{int(discount)}%"
        self.sale_11.setText(discount_text)

        if discount >= 15:
            self.sale_11.setStyleSheet("border: 1px solid black; background-color:#2E8B57;")
        else:
            self.sale_11.setStyleSheet("border: 1px solid black; background-color:#7FFF00;")


    def load_product_photo(self, photo_filename):
        self.photo_10.clear()  # Очищаем, чтобы убрать текст "Нет фото"


        if photo_filename:
            full_path = os.path.join(IMAGE_FOLDER, photo_filename)

            if os.path.exists(full_path):
                pixmap = QtGui.QPixmap(full_path)

                if not pixmap.isNull():
                    # 💡 КРИТИЧЕСКИЙ ШАГ 2: Только устанавливаем pixmap
                    self.photo_10.setPixmap(pixmap)
                    self.photo_10.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    return

        default_path = os.path.join(IMAGE_FOLDER, "picture.png")
        if os.path.exists(default_path):
            pixmap_default = QtGui.QPixmap(default_path)

            if not pixmap_default.isNull():
                # 💡 КРИТИЧЕСКИЙ ШАГ 2: Только устанавливаем pixmap
                self.photo_10.setPixmap(pixmap_default)
                self.photo_10.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                return

        # 3. Если ничего не найдено
        self.photo_10.setText("Нет фото")
        self.photo_10.setPixmap(QtGui.QPixmap())
        self.photo_10.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def card_click_handler(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.product_clicked.emit(self.article, self)

            # 1. Обработка ДВОЙНОГО КЛИКА
            if event.type() == QtCore.QEvent.Type.MouseButtonDblClick:
                print(f"ДВОЙНОЙ КЛИК: Редактирование товара {self.article}")
                self.product_clicked.emit(self.article, self)

            # 2. Обработка ОДИНОЧНОГО КЛИКА
            elif event.type() == QtCore.QEvent.Type.MouseButtonPress:
                self.highlight_card()


    def highlight_card(self):
        current_style = self.widget_7.styleSheet()

        if "border: 3px solid" in current_style:
            # Снимаем выделение (возвращаем исходный стиль)
            self.widget_7.setStyleSheet(self.original_style)
        else:
            # Выделяем (можно использовать другой цвет, например, желтый)
            self.widget_7.setStyleSheet(current_style + "border: 2px solid #00FA9A")  # Золотой цвет

    def set_selected(self, state: bool):
        """Устанавливает или снимает визуальное выделение карточки."""
        self.is_selected = state

        if state:
            # Применяем стиль выделения (золотая рамка)
            self.widget_7.setStyleSheet(self.selected_style)
        else:
            # Применяем базовый стиль (черная рамка с эффектом hover)
            self.widget_7.setStyleSheet(self.default_style)