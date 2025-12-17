# order_card_widget.py

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel



class Ui_OrderCard(object):
    """Сгенерированный класс, содержащий элементы дизайна карточки."""

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(603, 164)

        # Основной горизонтальный компоновщик для всего виджета
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Сам контейнер заказа (widget_order)
        self.widget_order = QtWidgets.QWidget(parent=Form)
        self.widget_order.setStyleSheet("QWidget#widget_order {\n"
                                        "    border: 1px solid #000; \n"
                                        "}\n"
                                        "QWidget#widget_order:hover {\n"
                                        "    border: 2px solid #00FA9A;\n"
                                        "}")
        self.widget_order.setObjectName("widget_order")

        # Внутренние компоновщики и виджеты
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_order)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")

        self.widget_order_name = QtWidgets.QWidget(parent=self.widget_order)
        self.widget_order_name.setMinimumSize(QtCore.QSize(400, 0))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        self.widget_order_name.setFont(font)
        self.widget_order_name.setStyleSheet("QWidget#widget_order_name {\n"
                                             "    border: 1px solid #000; \n"
                                             "}")
        self.widget_order_name.setObjectName("widget_order_name")

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget_order_name)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        # Метки, которые будут заполняться данными
        self.label_art = QtWidgets.QLabel(parent=self.widget_order_name)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        self.label_art.setFont(font)
        self.label_art.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.label_art.setObjectName("label_art")
        self.verticalLayout_4.addWidget(self.label_art)

        self.label_status = QtWidgets.QLabel(parent=self.widget_order_name)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        self.label_status.setFont(font)
        self.label_status.setObjectName("label_status")
        self.verticalLayout_4.addWidget(self.label_status)

        self.label_adress = QtWidgets.QLabel(parent=self.widget_order_name)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        self.label_adress.setFont(font)
        self.label_adress.setObjectName("label_adress")
        self.verticalLayout_4.addWidget(self.label_adress)

        self.label_order_date = QtWidgets.QLabel(parent=self.widget_order_name)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        self.label_order_date.setFont(font)
        self.label_order_date.setObjectName("label_order_date")
        self.verticalLayout_4.addWidget(self.label_order_date)

        self.verticalLayout_2.addLayout(self.verticalLayout_4)
        self.horizontalLayout_4.addWidget(self.widget_order_name)

        self.label_delivery_date = QtWidgets.QLabel(parent=self.widget_order)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        self.label_delivery_date.setFont(font)
        self.label_delivery_date.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.label_delivery_date.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_delivery_date.setObjectName("label_delivery_date")
        self.horizontalLayout_4.addWidget(self.label_delivery_date)

        # Установка stretch-факторов для правильного растяжения
        self.horizontalLayout_4.setStretch(0, 4)  # Инфо занимает 4 части
        self.horizontalLayout_4.setStretch(1, 1)  # Дата доставки занимает 1 часть

        self.horizontalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout.addWidget(self.widget_order)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Карточка заказа"))
        self.label_art.setText(_translate("Form", "Артикул заказа"))
        self.label_status.setText(_translate("Form", "Статус заказа"))
        self.label_adress.setText(_translate("Form", "Адрес пункта выдачи"))
        self.label_order_date.setText(_translate("Form", "Дата заказа"))
        self.label_delivery_date.setText(_translate("Form", "Дата доставки"))



class OrderCardWidget(QWidget, Ui_OrderCard):
    order_clicked = QtCore.pyqtSignal(int, QWidget)

    def __init__(self, order_data: dict, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        # Сохраняем реальный числовой ID для базы данных
        self.db_id = int(order_data.get('order_id', 0))
        # Сгенерированный артикул (товары + кол-во)
        self.generated_articul = order_data.get('product_details', 'Нет данных')
        self.fill_data(order_data)
        self.setWindowIcon(QIcon('C:\\Users\\nightmare\\PycharmProjects\\FinalProject\\images\\Icon.png'))

    def fill_data(self, data: dict):
        self.label_art.setText(f"<b>Артикул: {self.generated_articul}</b>")
        self.label_status.setText(f"Статус: {data.get('status_name', 'Н/Д')}")
        self.label_adress.setText(f"Пункт выдачи: {data.get('pickup_address', 'Не указан')}")
        self.label_order_date.setText(f"Заказано: {data.get('order_date', 'Н/Д')}")
        self.label_delivery_date.setText(f"Доставка:\n{data.get('order_delivery_date', 'Н/Д')}")

    def set_selected(self, is_selected: bool):
        style = "border: 3px solid #00FA9A;" if is_selected else "border: 1px solid #000;"
        self.widget_order.setStyleSheet(f"QWidget#widget_order {{ {style} }}")

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            # Испускаем ЧИСЛОВОЙ ID (int)
            self.order_clicked.emit(self.db_id, self)
        super().mousePressEvent(event)

