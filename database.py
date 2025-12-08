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

    # --- МЕТОДЫ ЧТЕНИЯ ДАННЫХ (R) ---

    def get_all_products(self):
        if self.cursor is None:
            QMessageBox.critical(None, "Ошибка БД", "Курсор базы данных не инициализирован.")
            return []

        query = """
        SELECT 
                p.product_photo,
                p.product_description,
                p.product_article, 
                p.product_name, 
                p.product_cost, 
                p.product_discount_amount, 
                p.product_quantity_stock, 
                c.category_name,
                m.manufacturer_name,
                s.supplier_name,
                u.unit_name
            FROM product p
            LEFT JOIN category c ON p.product_category_id = c.category_id
            LEFT JOIN manufacturer m ON p.product_manufacturer_id = m.manufacturer_id
            LEFT JOIN supplier s ON p.product_supplier_id = s.supplier_id
            LEFT JOIN unit u ON p.product_unit_id = u.unit_id
            WHERE 1=1
        """
        try:
            self.cursor.execute(query)

            column_names = [desc[0] for desc in self.cursor.description]
            products = [dict(zip(column_names, row)) for row in self.cursor.fetchall()]
            print(f"DEBUG (Database): Запрос вернул товаров: {len(products)}")
            return products

        except Exception as e:
            QMessageBox.critical(None, "Ошибка SQL", f"Ошибка выполнения запроса: {e}")
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
                    product_unit_id          
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                data_with_ids.get('provider_id', None),  # provider_id - это supplier_id
                data_with_ids.get('unit_id', None)
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
                            product_unit_id = %s          
                        WHERE product_article = %s
                    """

            params = (
                data['name'],
                data['description'],
                data['cost'],
                data['discount'],
                data['quantity'],
                data.get('category_id', None),
                data.get('manufacturer_id', None),
                data.get('provider_id', None),
                data.get('unit_id', None),
                data['article']
            )

            self.cursor.execute(query, params)
            self.conn.commit()
            return True

        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при обновлении: {e}")
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

        safe_name_value = str(name_value)

        query = f"SELECT {id_column} FROM {table_name} WHERE {name_column} = %s"

        try:
            self.cursor.execute(query, (safe_name_value,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
            self.conn.rollback() # Откат при ошибке
            print(f"Ошибка получения ID из {table_name}: {e}")
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

    def close(self):
        if self.conn:
            try:
                self.cursor.close()
                self.conn.close()
            except Exception as e:
                print(f"Ошибка при закрытии соединения: {e}")