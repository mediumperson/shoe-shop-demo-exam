from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6 import QtCore, QtGui, QtWidgets
import os
from widget2 import Ui_Form

IMAGE_FOLDER = 'C:\\Users\\nightmare\\PycharmProjects\\FinalProject\\images'


class ProductCardWidget(QWidget, Ui_Form):
    product_clicked = QtCore.pyqtSignal(str, object)

    def __init__(self, product_data, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.product_data = product_data
        self.article = product_data.get('product_article')
        self.original_style = self.widget_7.styleSheet()

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

        if quantity == 0:
            self.label_49.setStyleSheet("color: #0000FF; border: 0px solid black;")

        discount_text = f"Скидка:\n{int(discount)}%"
        self.sale_11.setText(discount_text)

        if discount >= 15:
            self.sale_11.setStyleSheet("border: 1px solid black; background-color:#2E8B57;")
        else:
            self.sale_11.setStyleSheet("border: 1px solid black; background-color:#7FFF00;")

        self.load_product_photo(data.get('product_photo'))

    def load_product_photo(self, photo_filename):

        if photo_filename:
            full_path = os.path.join(IMAGE_FOLDER, photo_filename)

            if os.path.exists(full_path):
                pixmap = QtGui.QPixmap(full_path)

                if not pixmap.isNull():
                    self.photo_10.setPixmap(pixmap.scaled(self.photo_10.size(),
                                                          QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                                          QtCore.Qt.TransformationMode.SmoothTransformation))
                    return

        default_path = os.path.join(IMAGE_FOLDER, "picture.png")
        if os.path.exists(default_path):
            pixmap_default = QtGui.QPixmap(default_path)
            if not pixmap_default.isNull():
                self.photo_10.setPixmap(pixmap_default.scaled(self.photo_10.size(),
                                                              QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                                              QtCore.Qt.TransformationMode.SmoothTransformation))
                return

        self.photo_10.setText("Нет фото")
        self.photo_10.setPixmap(QtGui.QPixmap())
        self.photo_10.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def card_click_handler(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            # Выпускаем сигнал, передавая артикул и сам виджет
            self.product_clicked.emit(self.article, self)