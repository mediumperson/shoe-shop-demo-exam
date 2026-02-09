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
        if self.cursor is None:
            QMessageBox.critical(None, "Ошибка БД", "Курсор не инициализирован.")
            return False

        if not article:
            return False

        try:
            # 1. Проверяем, есть ли товар в заказах
            check_query = "SELECT COUNT(*) FROM order_product WHERE product_article = %s"
            self.cursor.execute(check_query, (article,))
            count = self.cursor.fetchone()[0]

            if count > 0:
                QMessageBox.warning(
                    None,
                    "Запрет удаления",
                    f"Невозможно удалить товар {article}, так как он числится в {count} заказах.\n"
                    "Сначала удалите товар из заказов или удалите сами заказы."
                )
                return False

            # 2. Если товара нет в заказах, удаляем
            delete_query = "DELETE FROM product WHERE product_article = %s"
            self.cursor.execute(delete_query, (article,))
            self.conn.commit()
            return True

        except Exception as e:
            if self.conn:
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
        if self.cursor is None:
            return None

        query = """
            SELECT 
                o.order_id, 
                o.order_code, 
                o.order_status_id,       
                o.order_pickup_point_id AS pvz_id, 
                o.order_date, 
                o.order_delivery_date,
                -- Генерируем строку артикулов и количества для отображения в поле "Артикул"
                COALESCE(STRING_AGG(op.product_article || ', ' || op.count || '', ', '), 'Нет товаров') AS product_details
            FROM "order" o
            LEFT JOIN order_product op ON o.order_id = op.order_id
            WHERE o.order_id = %s
            GROUP BY o.order_id, o.order_code, o.order_status_id, o.order_pickup_point_id, o.order_date, o.order_delivery_date;
        """
        try:
            self.cursor.execute(query, (order_id,))
            row = self.cursor.fetchone()
            if row:
                columns = [desc[0] for desc in self.cursor.description]
                data = dict(zip(columns, row))

                for key in ['order_date', 'order_delivery_date']:
                    if data.get(key) and not isinstance(data[key], str):
                        data[key] = data[key].strftime('%Y-%m-%d')
                return data
            return None
        except Exception as e:
            print(f"Ошибка получения заказа по ID: {e}")
            return None

    def add_new_order(self, data: dict) -> bool:
        if self.cursor is None or self.conn is None:
            return False

        query_insert = """
            INSERT INTO "order" (
                order_status_id,
                order_pickup_point_id,
                order_date,
                order_delivery_date,
                order_client_id,
                order_code
            ) VALUES (%s, %s, %s, %s, 1, 0)
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

        sequence_name = 'order_order_id_seq'

        query = f"SELECT nextval('{sequence_name}');"

        try:
            # Сначала получаем nextval, чтобы увеличить счетчик
            self.cursor.execute(query)
            next_id = self.cursor.fetchone()[0]

            self.conn.rollback()

            return int(next_id)

        except Exception as e:
            # Если последовательность не найдена, или ошибка, можно вывести сообщение
            QMessageBox.warning(None, "Ошибка БД",
                                f"Не удалось получить следующий ID заказа из последовательности {sequence_name}: {e}")
            return None

    def update_order(self, order_id: int, data: dict) -> bool:
        if self.cursor is None: return False

        query = """
            UPDATE "order" SET
                order_status_id = %s,
                order_pickup_point_id = %s,
                order_date = %s,
                order_delivery_date = %s
            WHERE order_id = %s;
        """
        try:
            params = (
                data['status_id'], data['pvz_id'],
                data['order_date'], data['order_delivery_date'],
                order_id
            )
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            return False

    def delete_order_by_id(self, order_id: int) -> bool:
        """Удаляет заказ по ID."""
        if self.cursor is None or self.conn is None:
            return False


        query = "DELETE FROM \"order\" WHERE order_id = %s;"

        try:
            self.cursor.execute(query, (order_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0  # Проверяем, была ли удалена хотя бы одна строка
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(None, "Ошибка SQL", f"Ошибка при удалении заказа #{order_id}: {e}")
            return False

    def get_all_orders(self) -> list:
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
                ua.user_login AS client_name,
                -- Собираем строку формата: артикул, количество
                STRING_AGG(op.product_article || ', ' || op.count, ', ') AS product_details 
            FROM 
                "order" o
            JOIN 
                order_status os ON o.order_status_id = os.status_id 
            LEFT JOIN
                pickup_point pp ON o.order_pickup_point_id = pp.pickup_point_id
            LEFT JOIN  
                user_account ua ON o.order_client_id = ua.user_id 
            LEFT JOIN
                order_product op ON o.order_id = op.order_id
            GROUP BY 
                o.order_id, o.order_code, os.status_name, pp.pickup_point_address, ua.user_login
            ORDER BY 
                o.order_date DESC;
        """

        orders = []
        try:
            self.cursor.execute(query)
            columns = [desc[0] for desc in self.cursor.description]

            for row in self.cursor.fetchall():
                order_data = dict(zip(columns, row))

                # Форматирование дат
                for date_key in ['order_date', 'order_delivery_date']:
                    if order_data.get(date_key):
                        order_data[date_key] = order_data[date_key].strftime('%d.%m.%Y')

                # Если товаров нет, ставим заглушку
                if not order_data.get('product_details'):
                    order_data['product_details'] = "Без товаров"

                orders.append(order_data)
            return orders
        except Exception as e:
            print(f"Ошибка получения заказов: {e}")
            return []

    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()