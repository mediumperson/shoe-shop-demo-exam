import psycopg2
from PyQt6.QtWidgets import QMessageBox


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
            print("Соединение с БД установлено.")
        except Exception as e:
            QMessageBox.critical(None, "Ошибка БД", f"Не удалось подключиться к базе данных: {e}")

    def get_user(self, login, password):

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
        role_id, username = self.cursor.fetchone()

        return role_id, username

    def get_all_products(self):
        return self.get_products_by_filter({})

    def get_products_by_filter(self, params: dict) -> list:
        """
        Получает список товаров, фильтруя их по заданным параметрам.
        """
        if self.cursor is None:
            QMessageBox.critical(None, "Ошибка БД", "Курсор базы данных не инициализирован.")
            return []

        # base_query ДОЛЖЕН БЫТЬ ОПРЕДЕЛЕН ЗДЕСЬ, чтобы избежать ошибки
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

        # 1. Поиск по Наименованию ИЛИ Производителю (Реализация поиска по нескольким словам)
        if 'search_term' in params and params['search_term']:
            search_term = params['search_term']

            # Разделяем строку по пробелам или запятым, игнорируя лишние пробелы
            keywords = [
                kw.strip() for kw in search_term.replace(',', ' ').split() if kw.strip()
            ]

            if keywords:
                # Создаем условие, которое ДОЛЖНО быть выполнено для КАЖДОГО ключевого слова (AND-логика)
                # Например: (name ILIKE '%слово1%' OR manufacturer ILIKE '%слово1%') AND (name ILIKE '%слово2%' OR manufacturer ILIKE '%слово2%')

                for keyword in keywords:
                    search_val = f"%{keyword}%"

                    # Условие для одного ключевого слова
                    conditions.append("(p.product_name ILIKE %s OR m.manufacturer_name ILIKE %s)")
                    args.extend([search_val, search_val])


        # 2. Поставщик
        if 'supplier_name' in params and params['supplier_name']:
            conditions.append("s.supplier_name = %s")
            args.append(params['supplier_name'])

        # ... (остальная логика STOCK_THRESHOLD и stock_filter остается без изменений)

        # Добавляем все условия к запросу
        if conditions:
            base_query += " AND " + " AND ".join(conditions)

        order_by_clause = "p.product_article ASC"

        # Проверяем, есть ли в параметрах фильтр из QComboBox self.storage
        if 'stock_filter' in params and params['stock_filter']:
            criteria = params['stock_filter']

            if criteria == "Больше":
                # Сортировка по убыванию (от большого количества к меньшему)
                order_by_clause = "p.product_quantity_stock DESC, p.product_article ASC"
                print("DEBUG (Database): Сортировка: Количество (Макс -> Мин)")
            elif criteria == "Меньше":
                # Сортировка по возрастанию (от меньшего количества к большему)
                order_by_clause = "p.product_quantity_stock ASC, p.product_article ASC"
                print("DEBUG (Database): Сортировка: Количество (Мин -> Макс)")
            # Если criteria == "Любое количество" или другая опция,
            # используется значение order_by_clause по умолчанию.

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
        if self.cursor is None:
            return []

        query = "SELECT supplier_name FROM supplier ORDER BY supplier_name ASC"

        try:
            self.cursor.execute(query)
            # Извлекаем все строки и возвращаем список имен (первый элемент кортежа)
            suppliers = [row[0] for row in self.cursor.fetchall()]
            return suppliers

        except Exception as e:
            QMessageBox.critical(None, "Ошибка БД", f"Ошибка при получении списка поставщиков: {e}")
            return []

    def get_product_by_article(self, article):
        query = """
        SELECT
                p.product_photo,
                p.product_description,
                p.product_article, 
                p.product_name, 
                p.product_cost, 
                p.product_discount_amount, 
                p.product_quantity_stock,
                p.product_category_id,     
                p.product_manufacturer_id, 
                p.product_supplier_id,     
                p.product_unit_id,         
                c.category_name,           
                m.manufacturer_name,
                s.supplier_name,
                u.unit_name
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
            print(f"Ошибка поиска товара: {e}")
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
                print(f"Ошибка: Отсутствует ключ в данных: {key}")
                return False

        try:
            query = """
                        INSERT INTO product (
                            product_article, 
                            product_name, 
                            product_description, 
                            product_cost, 
                            product_discount_amount, 
                            product_quantity_stock,
                            product_category_id,     
                            product_manufacturer_id, 
                            product_supplier_id,     
                            product_unit_id,
                            product_photo
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

            params = (
                data_with_ids['product_article'],
                data_with_ids['product_name'],
                data_with_ids['product_description'],
                data_with_ids['product_cost'],
                data_with_ids['product_discount_amount'],
                data_with_ids['product_quantity_stock'],
                data_with_ids.get('category_id', None),
                data_with_ids.get('manufacturer_id', None),
                data_with_ids.get('provider_id', None),
                data_with_ids.get('unit_id', None),
                data_with_ids.get('product_photo', None)
            )

            self.cursor.execute(query, params)
            self.conn.commit()
            return True

        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при добавлении товара в БД: {e}")
            QMessageBox.critical(None, "Ошибка SQL", f"Ошибка при добавлении товара: {e}")
            return False

    def update_product(self, data):
        if self.cursor is None:
            QMessageBox.critical(None, "Ошибка БД", "Курсор не инициализирован для записи.")
            return False

            # 1. Получаем ID для вспомогательных таблиц
            # NOTE: data_with_ids содержит ключи из формы ('product_name' и т.д.)
        data_with_ids = self.get_id_for_product_fields(data)

        try:
            query = """
                                UPDATE product SET 
                                    product_name = %s, 
                                    product_description = %s, 
                                    product_cost = %s, 
                                    product_discount_amount = %s, 
                                    product_quantity_stock = %s,
                                    product_category_id = %s,     
                                    product_manufacturer_id = %s, 
                                    product_supplier_id = %s,     
                                    product_unit_id = %s,
                                    product_photo = %s          
                                WHERE product_article = %s
                            """

            # 2. ИСПОЛЬЗУЕМ КЛЮЧИ ИЗ ФОРМЫ (product_name, product_description и т.д.)
            params = (
                data_with_ids['product_name'],  # Было: data_with_ids['name']
                data_with_ids['product_description'],
                data_with_ids['product_cost'],
                data_with_ids['product_discount_amount'],
                data_with_ids['product_quantity_stock'],
                data_with_ids.get('category_id', None),
                data_with_ids.get('manufacturer_id', None),
                data_with_ids.get('provider_id', None),
                data_with_ids.get('unit_id', None),
                data_with_ids.get('product_photo', None),
                data_with_ids['product_article']  # Было: data_with_ids['article']
            )

            self.cursor.execute(query, params)
            self.conn.commit()

            if self.cursor.rowcount == 0:
                print(
                    f"Предупреждение: Обновление не затронуло ни одной строки (артикул {data_with_ids['product_article']} не найден).")

            return True

        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при обновлении товара в БД: {e}")
            QMessageBox.critical(None, "Ошибка SQL", f"Ошибка при обновлении товара: {e}")
            return False

    def delete_product_by_article(self, article: str) -> bool:
        if self.cursor is None:
            QMessageBox.critical(None, "Ошибка БД", "Курсор не инициализирован для записи.")
            return False

        if not article:
            return False

        query = "DELETE FROM product WHERE product_article = %s"

        try:
            self.cursor.execute(query, (article,))
            rows_deleted = self.cursor.rowcount
            self.conn.commit()

            return True

        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при удалении товара: {e}")
            QMessageBox.critical(None, "Ошибка SQL", f"Ошибка при удалении товара: {e}")
            return False

    def get_id_by_name(self, table_name, name_column, name_value, id_column):
        if not name_value:
            return None

        safe_name_value = str(name_value).strip()
        if not safe_name_value:
            return None

        # 1. Поиск существующего ID
        try:
            search_query = f"SELECT {id_column} FROM {table_name} WHERE {name_column} = %s"
            self.cursor.execute(search_query, (safe_name_value,))
            result = self.cursor.fetchone()

            if result:
                return result[0]

        except Exception as e:
            print(f"Ошибка поиска ID из {table_name}: {e}")
            self.conn.rollback()
            return None

        # 2. Если ID не найден, добавляем новую запись
        try:
            insert_query = f"INSERT INTO {table_name} ({name_column}) VALUES (%s) RETURNING {id_column}"
            self.cursor.execute(insert_query, (safe_name_value,))

            new_id = self.cursor.fetchone()[0]
            self.conn.commit()

            print(f"DEBUG: Добавлена новая запись в {table_name}: '{safe_name_value}', ID: {new_id}")
            return new_id

        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка добавления новой записи в {table_name}: {e}")
            return None

    def get_id_for_product_fields(self, data):
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
                o.order_code,            -- Код заказа (из таблицы order)
                os.status_name,          -- Название статуса
                o.order_date, 
                o.order_delivery_date,   
                pp.pickup_point_address AS pickup_address, -- Адрес пункта выдачи
                ua.user_login AS client_name               -- Логин клиента (предполагаем, что это имя)
            FROM 
                "order" o -- Таблица "order" взята в кавычки, т.к. 'order' - это ключевое слово SQL
            JOIN 
                order_status os ON o.order_status_id = os.status_id 
            LEFT JOIN
                pickup_point pp ON o.order_pickup_point_id = pp.pickup_point_id
            LEFT JOIN  
                user_account ua ON o.order_client_id = ua.user_id -- Связь с таблицей user_account
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

                # order_delivery_date может быть NULL, нужна проверка
                delivery_date = order_data.get('order_delivery_date')
                if delivery_date:
                    order_data['order_delivery_date'] = delivery_date.strftime('%d.%m.%Y')
                else:
                    order_data['order_delivery_date'] = "Н/Д"

                orders.append(order_data)

            return orders

        except Exception as e:
            # 💡 Если возникнут ошибки, они будут здесь
            print(f"DEBUG (Database): Критическая ошибка при получении списка заказов: {e}")
            return []

    def close(self):
        if self.conn:
            try:
                self.cursor.close()
                self.conn.close()
            except Exception as e:
                print(f"Ошибка при закрытии соединения: {e}")