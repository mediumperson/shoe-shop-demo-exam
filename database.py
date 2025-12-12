import psycopg2
from PyQt6.QtWidgets import QMessageBox
from datetime import datetime


class Database:
    def __init__(self, dbname, user, password, host, port):
        self.conn = None
        self.cursor = None

        self.conn_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }

    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            self.cursor = self.conn.cursor()
        except Exception as e:
            QMessageBox.critical(None, "Ошибка БД", f"Не удалось подключиться к базе данных: {e}")

    def get_user(self, login, password):
        if self.cursor is None:
            raise Exception("Курсор не инициализирован.")

        # Запрос к вашей таблице пользователей
        query = """
            SELECT
                u.user_role_id, u.user_fio
            FROM
                user_account u
            WHERE
                u.user_login = %s AND u.user_password = %s;
        """

        variables = (login, password)
        self.cursor.execute(query, variables)
        result = self.cursor.fetchone()

        if result:
            return result[0], result[1]
        return None, None

    # --------------------------------------------------------------------
    # МЕТОДЫ ДЛЯ ТОВАРОВ (Оставлены без изменений)
    # --------------------------------------------------------------------

    def get_all_products(self):
        return self.get_products_by_filter({})

    def get_products_by_filter(self, params: dict) -> list:
        """
        Получает список товаров, фильтруя их по заданным параметрам.
        (Опущен для краткости, остался без изменений)
        """
        if self.cursor is None:
            QMessageBox.critical(None, "Ошибка БД", "Курсор базы данных не инициализирован.")
            return []

        base_query = """
            SELECT 
                p.product_photo, p.product_description, p.product_article, 
                p.product_name, p.product_cost, p.product_discount_amount, 
                p.product_quantity_stock, 
                c.category_name, m.manufacturer_name, s.supplier_name, u.unit_name
            FROM product p
            LEFT JOIN category c ON p.product_category_id = c.category_id
            LEFT JOIN manufacturer m ON p.product_manufacturer_id = m.manufacturer_id
            LEFT JOIN supplier s ON p.product_supplier_id = s.supplier_id
            LEFT JOIN unit u ON p.product_unit_id = u.unit_id
            WHERE 1=1
        """
        conditions = []
        args = []

        if 'search_term' in params and params['search_term']:
            search_term = params['search_term']
            keywords = [
                kw.strip() for kw in search_term.replace(',', ' ').split() if kw.strip()
            ]
            if keywords:
                for keyword in keywords:
                    search_val = f"%{keyword}%"
                    conditions.append("(p.product_name ILIKE %s OR m.manufacturer_name ILIKE %s)")
                    args.extend([search_val, search_val])

        if 'supplier_name' in params and params['supplier_name']:
            conditions.append("s.supplier_name = %s")
            args.append(params['supplier_name'])

        if conditions:
            base_query += " AND " + " AND ".join(conditions)

        order_by_clause = "p.product_article ASC"

        if 'stock_filter' in params and params['stock_filter']:
            criteria = params['stock_filter']
            if criteria == "Больше":
                order_by_clause = "p.product_quantity_stock DESC, p.product_article ASC"
            elif criteria == "Меньше":
                order_by_clause = "p.product_quantity_stock ASC, p.product_article ASC"

        base_query += f" ORDER BY {order_by_clause}"

        try:
            self.cursor.execute(base_query, tuple(args))
            column_names = [desc[0] for desc in self.cursor.description]
            products = [dict(zip(column_names, row)) for row in self.cursor.fetchall()]
            return products

        except Exception as e:
            QMessageBox.critical(None, "Ошибка SQL", f"Ошибка выполнения запроса фильтрации: {e}")
            return []

    def get_all_suppliers(self):
        # (Опущен для краткости, остался без изменений)
        if self.cursor is None:
            return []

        query = "SELECT supplier_name FROM supplier ORDER BY supplier_name ASC"

        try:
            self.cursor.execute(query)
            suppliers = [row[0] for row in self.cursor.fetchall()]
            return suppliers

        except Exception as e:
            QMessageBox.critical(None, "Ошибка БД", f"Ошибка при получении списка поставщиков: {e}")
            return []

    def get_product_by_article(self, article):
        # (Опущен для краткости, остался без изменений)
        query = """
        SELECT
                p.product_photo, p.product_description, p.product_article, 
                p.product_name, p.product_cost, p.product_discount_amount, 
                p.product_quantity_stock, p.product_category_id,     
                p.product_manufacturer_id, p.product_supplier_id, p.product_unit_id,         
                c.category_name, m.manufacturer_name, s.supplier_name, u.unit_name
            FROM product p
            LEFT JOIN category c ON p.product_category_id = c.category_id
            LEFT JOIN manufacturer m ON p.product_manufacturer_id = m.manufacturer_id
            LEFT JOIN supplier s ON p.product_supplier_id = s.supplier_id
            LEFT JOIN unit u ON p.product_unit_id = u.unit_id
            WHERE p.product_article = %s
        """
        try:
            self.cursor.execute(query, (article,))
            row = self.cursor.fetchone()

            if row:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return None

    def add_product(self, data: dict) -> bool:
        # (Опущен для краткости, остался без изменений)
        if self.cursor is None:
            QMessageBox.critical(None, "Ошибка БД", "Курсор не инициализирован для записи.")
            return False

        data_with_ids = self.get_id_for_product_fields(data)

        required_keys = ['product_article', 'product_name', 'product_description', 'product_cost',
                         'product_discount_amount', 'product_quantity_stock']
        for key in required_keys:
            if key not in data_with_ids:
                return False

        try:
            query = """
                        INSERT INTO product (
                            product_article, product_name, product_description, product_cost, 
                            product_discount_amount, product_quantity_stock, product_category_id,     
                            product_manufacturer_id, product_supplier_id, product_unit_id, product_photo
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

            params = (
                data_with_ids['product_article'], data_with_ids['product_name'], data_with_ids['product_description'],
                data_with_ids['product_cost'], data_with_ids['product_discount_amount'],
                data_with_ids['product_quantity_stock'], data_with_ids.get('category_id', None),
                data_with_ids.get('manufacturer_id', None), data_with_ids.get('provider_id', None),
                data_with_ids.get('unit_id', None), data_with_ids.get('product_photo', None)
            )

            self.cursor.execute(query, params)
            self.conn.commit()
            return True

        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(None, "Ошибка SQL", f"Ошибка при добавлении товара: {e}")
            return False

    def update_product(self, data):
        # (Опущен для краткости, остался без изменений)
        if self.cursor is None:
            QMessageBox.critical(None, "Ошибка БД", "Курсор не инициализирован для записи.")
            return False

        data_with_ids = self.get_id_for_product_fields(data)

        try:
            query = """
                                UPDATE product SET 
                                    product_name = %s, product_description = %s, product_cost = %s, 
                                    product_discount_amount = %s, product_quantity_stock = %s,
                                    product_category_id = %s, product_manufacturer_id = %s, 
                                    product_supplier_id = %s, product_unit_id = %s,
                                    product_photo = %s          
                                WHERE product_article = %s
                            """

            params = (
                data_with_ids['product_name'], data_with_ids['product_description'],
                data_with_ids['product_cost'], data_with_ids['product_discount_amount'],
                data_with_ids['product_quantity_stock'], data_with_ids.get('category_id', None),
                data_with_ids.get('manufacturer_id', None), data_with_ids.get('provider_id', None),
                data_with_ids.get('unit_id', None), data_with_ids.get('product_photo', None),
                data_with_ids['product_article']
            )

            self.cursor.execute(query, params)
            self.conn.commit()

            return True

        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(None, "Ошибка SQL", f"Ошибка при обновлении товара: {e}")
            return False

    def delete_product_by_article(self, article: str) -> bool:
        # (Опущен для краткости, остался без изменений)
        if self.cursor is None:
            QMessageBox.critical(None, "Ошибка БД", "Курсор не инициализирован для записи.")
            return False

        if not article:
            return False

        query = "DELETE FROM product WHERE product_article = %s"

        try:
            self.cursor.execute(query, (article,))
            self.conn.commit()
            return True

        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(None, "Ошибка SQL", f"Ошибка при удалении товара: {e}")
            return False

    def get_id_by_name(self, table_name, name_column, name_value, id_column):
        # (Опущен для краткости, остался без изменений)
        if not name_value:
            return None

        safe_name_value = str(name_value).strip()
        if not safe_name_value:
            return None

        try:
            # 1. Поиск существующего ID
            search_query = f"SELECT {id_column} FROM {table_name} WHERE {name_column} = %s"
            self.cursor.execute(search_query, (safe_name_value,))
            result = self.cursor.fetchone()

            if result:
                return result[0]

            # 2. Если ID не найден, добавляем новую запись
            insert_query = f"INSERT INTO {table_name} ({name_column}) VALUES (%s) RETURNING {id_column}"
            self.cursor.execute(insert_query, (safe_name_value,))

            new_id = self.cursor.fetchone()[0]
            self.conn.commit()

            return new_id

        except Exception as e:
            self.conn.rollback()
            return None

    def get_id_for_product_fields(self, data):
        # (Опущен для краткости, остался без изменений)
        category_name = data.pop('category_name', None)
        manufacturer_name = data.pop('manufacturer_name', None)
        provider_name = data.pop('supplier_name', None)  # Ключ 'supplier_name' из формы
        unit_name = data.pop('unit_name', None)

        data['category_id'] = self.get_id_by_name('category', 'category_name', category_name, 'category_id')
        data['manufacturer_id'] = self.get_id_by_name('manufacturer', 'manufacturer_name', manufacturer_name,
                                                      'manufacturer_id')
        data['provider_id'] = self.get_id_by_name('supplier', 'supplier_name', provider_name,
                                                  'supplier_id')  # Provider -> Supplier
        data['unit_id'] = self.get_id_by_name('unit', 'unit_name', unit_name, 'unit_id')

        return data

    # --------------------------------------------------------------------
    # НОВЫЕ МЕТОДЫ ДЛЯ ЗАКАЗОВ (Order)
    # --------------------------------------------------------------------

    def get_all_statuses(self) -> list:
        """Получает список всех статусов заказа из таблицы order_status."""
        if self.cursor is None:
            return []

        query = "SELECT status_id, status_name FROM order_status ORDER BY status_id ASC"

        try:
            self.cursor.execute(query)

            statuses_list = []
            for row in self.cursor.fetchall():
                statuses_list.append({
                    'id': row[0],  # Соответствует status_id
                    'name': row[1]  # Соответствует status_name (ожидаемо в UI как 'name')
                })
            return statuses_list

        except Exception as e:
            QMessageBox.critical(None, "Ошибка БД", f"Ошибка при получении статусов: {e}")
            return []

    # --------------------------------------------------------------------
    # ИСПРАВЛЕННЫЙ МЕТОД ДЛЯ ПВЗ (Устраняет KeyError: 'address')
    # --------------------------------------------------------------------
    def get_all_pvz_addresses(self) -> list:
        """Получает список всех пунктов выдачи (адреса и ID)."""
        if self.cursor is None:
            return []

        query = "SELECT pickup_point_id, pickup_point_address FROM pickup_point ORDER BY pickup_point_address ASC"

        try:
            self.cursor.execute(query)

            pvz_list = []
            for row in self.cursor.fetchall():
                pvz_list.append({
                    'id': row[0],  # Соответствует pickup_point_id
                    'address': row[1]  # Соответствует pickup_point_address (ожидаемо в UI как 'address')
                })
            return pvz_list
        except Exception as e:
            QMessageBox.critical(None, "Ошибка БД", f"Ошибка при получении адресов ПВЗ: {e}")
            return []

    def get_order_by_id(self, order_id: int) -> dict | None:
        """Получает полные данные одного заказа по его ID."""
        if self.cursor is None:
            return None

        query = """
            SELECT 
                o.order_id, 
                o.order_id AS order_code,  -- ⚠️ ИСПОЛЬЗУЕМ order_id КАК order_code
                o.order_status_id,       
                o.order_pickup_point_id AS pvz_id, 
                o.order_date, 
                o.order_delivery_date
            FROM 
                "order" o
            WHERE
                o.order_id = %s;
        """
        try:
            self.cursor.execute(query, (order_id,))
            row = self.cursor.fetchone()

            if row:
                columns = [desc[0] for desc in self.cursor.description]
                data = dict(zip(columns, row))

                # Форматирование дат для корректного отображения в QDateEdit
                if data.get('order_date'):
                    # Преобразование datetime/date в строку 'yyyy-MM-dd'
                    data['order_date'] = data['order_date'].strftime('%Y-%m-%d')

                if data.get('order_delivery_date'):
                    data['order_delivery_date'] = data['order_delivery_date'].strftime('%Y-%m-%d')

                return data
            return None

        except Exception as e:
            QMessageBox.critical(None, "Ошибка БД", f"Ошибка при получении данных заказа #{order_id}: {e}")
            return None

    def add_new_order(self, data: dict) -> bool:
        """
        Добавляет новый заказ. order_code устанавливается равным order_id после вставки,
        но для обхода NOT NULL мы временно устанавливаем order_code равным 0,
        а затем обновляем его.

        ИЛИ (Предпочтительный вариант):
        Если order_code в БД можно временно сделать строкой, то можно было бы вставить
        'TEMP' и сразу обновить.

        Однако, лучший способ, не требующий изменения схемы, это:
        Вставить все данные, кроме order_code, получить ID, и СРАЗУ же обновить order_code
        в рамках ОДНОЙ транзакции.

        Но поскольку NOT NULL не позволяет пропустить order_code,
        мы должны передать временное значение, а потом его заменить.
        """
        if self.cursor is None or self.conn is None:
            return False

        # order_client_id=1 - заглушка

        # 1. Запрос на вставку (временно передаем NULL, если бы NOT NULL не было)
        # ⚠️ ПОСКОЛЬКУ order_code - NOT NULL, мы должны его включить в INSERT.
        # ВРЕМЕННО передадим ему значение, а затем обновим его в той же транзакции.

        query_insert = """
            INSERT INTO "order" (
                order_status_id,
                order_pickup_point_id,
                order_date,
                order_delivery_date,
                order_client_id,
                order_code                -- ⚠️ Добавляем order_code в INSERT
            ) VALUES (%s, %s, %s, %s, 1, 0) -- ⚠️ Временно присваиваем 0, чтобы обойти NOT NULL
            RETURNING order_id;
        """

        order_date_obj = datetime.strptime(data['order_date'], '%Y-%m-%d').date()
        delivery_date_obj = datetime.strptime(data['order_delivery_date'], '%Y-%m-%d').date()

        params_insert = (
            data['status_id'],
            data['pvz_id'],
            order_date_obj,
            delivery_date_obj,
        )

        try:
            self.cursor.execute(query_insert, params_insert)
            new_order_id = self.cursor.fetchone()[0]

            # 2. Обновляем order_code, присваивая ему значение order_id (числовое)
            # ⚠️ Теперь мы обновляем order_code, используя полученный order_id
            query_update_code = """
                UPDATE "order" SET order_code = %s WHERE order_id = %s;
            """
            self.cursor.execute(query_update_code, (new_order_id, new_order_id))

            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(None, "Ошибка SQL", f"Ошибка при добавлении заказа: {e}")
            return False

    def get_next_order_id(self) -> int | None:
        """Получает следующий доступный order_id из последовательности БД."""
        if self.cursor is None:
            return None

        # ⚠️ Название последовательности обычно формируется как: <table>_<column>_seq
        # В вашем случае это, вероятно, 'order_order_id_seq'
        sequence_name = 'order_order_id_seq'

        query = f"SELECT nextval('{sequence_name}');"

        try:
            # Сначала получаем nextval, чтобы увеличить счетчик
            self.cursor.execute(query)
            next_id = self.cursor.fetchone()[0]

            # Затем откатываем транзакцию, чтобы фактически не увеличивать счетчик,
            # но сохранить его значение, которое будет использовано при INSERT.
            self.conn.rollback()

            return int(next_id)

        except Exception as e:
            # Если последовательность не найдена, или ошибка, можно вывести сообщение
            QMessageBox.warning(None, "Ошибка БД",
                                f"Не удалось получить следующий ID заказа из последовательности {sequence_name}: {e}")
            return None

    def update_order(self, order_id: int, data: dict) -> bool:
        """Обновляет существующий заказ (за исключением order_code)."""
        if self.cursor is None or self.conn is None:
            return False

        # ⚠️ УБИРАЕМ order_code из списка полей для обновления
        query = """
            UPDATE "order" SET
                order_status_id = %s,
                order_pickup_point_id = %s,
                order_date = %s,
                order_delivery_date = %s
            WHERE order_id = %s;
        """

        order_date_obj = datetime.strptime(data['order_date'], '%Y-%m-%d').date()
        delivery_date_obj = datetime.strptime(data['order_delivery_date'], '%Y-%m-%d').date()

        params = (
            data['status_id'],
            data['pvz_id'],
            order_date_obj,
            delivery_date_obj,
            order_id  # WHERE clause
        )

        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(None, "Ошибка SQL", f"Ошибка при обновлении заказа #{order_id}: {e}")
            return False

    def delete_order_by_id(self, order_id: int) -> bool:
        """Удаляет заказ по ID."""
        if self.cursor is None or self.conn is None:
            return False

        # ⚠️ В реальной системе перед удалением самого заказа нужно удалить
        # все связанные с ним записи из таблицы "order_product" (если она есть)

        query = "DELETE FROM \"order\" WHERE order_id = %s;"

        try:
            self.cursor.execute(query, (order_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0  # Проверяем, была ли удалена хотя бы одна строка
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(None, "Ошибка SQL", f"Ошибка при удалении заказа #{order_id}: {e}")
            return False

    # --------------------------------------------------------------------
    # СУЩЕСТВУЮЩИЙ МЕТОД get_all_orders (обновлен для форматирования)
    # --------------------------------------------------------------------

    def get_all_orders(self) -> list:
        """
        Получает список всех заказов, используя точные названия таблиц из ER-диаграммы:
        order, order_status, pickup_point, user_account.
        """
        if self.cursor is None:
            return []

        query = """
            SELECT 
                o.order_id, 
                o.order_code,            
                os.status_name,          
                o.order_date, 
                o.order_delivery_date,   
                pp.pickup_point_address AS pickup_address, 
                ua.user_login AS client_name               
            FROM 
                "order" o
            JOIN 
                order_status os ON o.order_status_id = os.status_id 
            LEFT JOIN
                pickup_point pp ON o.order_pickup_point_id = pp.pickup_point_id
            LEFT JOIN  
                user_account ua ON o.order_client_id = ua.user_id 
            ORDER BY 
                o.order_date DESC;
        """

        orders = []
        try:
            self.cursor.execute(query)
            columns = [desc[0] for desc in self.cursor.description]

            for row in self.cursor.fetchall():
                order_data = dict(zip(columns, row))

                # Форматируем даты
                if order_data.get('order_date'):
                    # Преобразуем объект datetime в строку
                    order_data['order_date'] = order_data['order_date'].strftime('%d.%m.%Y %H:%M')

                delivery_date = order_data.get('order_delivery_date')
                if delivery_date:
                    order_data['order_delivery_date'] = delivery_date.strftime('%d.%m.%Y')
                else:
                    order_data['order_delivery_date'] = "Н/Д"

                orders.append(order_data)

            return orders

        except Exception as e:
            return []

    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()