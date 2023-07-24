from datetime import datetime
import pymysql


class DB:
    def __init__(self, host, user, password, db_name):
        self.connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        self.create_tables()

    def create_tables(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS aph_users (
                full_name VARCHAR(100) NOT NULL,
                chat_id INT NOT NULL,
                username VARCHAR(50) NOT NULL,
                join_date DATETIME NOT NULL,
                number_of_ratings INT DEFAULT 0,
                sum_of_ratings INT DEFAULT 0,
                orders_as_seller INT DEFAULT 0,
                orders_as_buyer INT DEFAULT 0,
                feedbacks JSON DEFAULT NULL,
                PRIMARY KEY (chat_id)
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS aph_things (
                order_token VARCHAR(50) NOT NULL,
                item_type ENUM('clothes', 'cosmetics', 'toys', 'electronics', 'other') NOT NULL,
                item_name VARCHAR(100) NOT NULL,
                manufacturer VARCHAR(100) NOT NULL,
                average_price FLOAT NOT NULL,
                delivery_markup FLOAT NOT NULL,
                chat_id INT NOT NULL,
                username VARCHAR(50) NOT NULL,
                item_link VARCHAR(255) NOT NULL,
                salesman_username TEXT,
                description TEXT,
                add_date DATETIME NOT NULL,
                finish_date TEXT,
                status INT DEFAULT 0,
                PRIMARY KEY (order_token, item_name)
            )
            """)

        self.connection.commit()

    def add_user(self, full_name, chat_id, username):
        with self.connection.cursor() as cursor:
            cursor.execute("""
            INSERT INTO aph_users (full_name, chat_id, username, join_date)
            VALUES (%s, %s, %s, %s)
            """, (full_name, chat_id, username, datetime.now()))
        self.connection.commit()

    def add_thing(self, order_token, item_type, item_name, manufacturer, average_price, delivery_markup, chat_id, username, item_link, salesman_username, description=None):
        with self.connection.cursor() as cursor:
            cursor.execute("""
            INSERT INTO aph_things (order_token, item_type, item_name, manufacturer, average_price, delivery_markup, chat_id, username, item_link, salesman_username, description, add_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (order_token, item_type, item_name, manufacturer, average_price, delivery_markup, chat_id, username, item_link, salesman_username, description, datetime.now()))
        self.connection.commit()

    def get_order_by_token(self, order_token):
        with self.connection.cursor() as cursor:
            cursor.execute("""
            SELECT * FROM aph_things
            WHERE order_token = %s
            """, (order_token,))
            return cursor.fetchall()

    def get_orders(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
            SELECT * FROM aph_things
            WHERE status = 0
            ORDER BY add_date 
            """)
            return cursor.fetchall()

    def get_user_by_param(self, param, value):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT * FROM aph_users
            WHERE {param} = %s
            """, (value,))
            return cursor.fetchone()

    def get_orders_by_username(self, username):
        with self.connection.cursor() as cursor:
            cursor.execute("""
            SELECT * FROM aph_things
            WHERE username = %s
            """, (username,))
            return cursor.fetchall()

    def update_user_param(self, chat_id, param, new_value):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
            UPDATE aph_users
            SET {param} = %s
            WHERE chat_id = %s
            """, (new_value, chat_id))
        self.connection.commit()

    def update_thing_param(self, order_token, item_name, param, new_value):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
            UPDATE aph_things
            SET {param} = %s
            WHERE order_token = %s AND item_name = %s
            """, (new_value, order_token, item_name))
        self.connection.commit()

    def delete_thing(self, order_token, item_name):
        with self.connection.cursor() as cursor:
            cursor.execute("""
            DELETE FROM aph_things
            WHERE order_token = %s AND item_name = %s
            """, (order_token, item_name))
        self.connection.commit()

    def delete_order(self, order_token):
        with self.connection.cursor() as cursor:
            cursor.execute("""
            DELETE FROM aph_things
            WHERE order_token = %s
            """, (order_token,))
        self.connection.commit()

    def sort_users_by_param(self, param):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT * FROM aph_users
            ORDER BY {param}
            """)
            return cursor.fetchall()

    def get_order_by_customer(self, username):
        with self.connection.cursor() as cursor:
            cursor.execute("""
            SELECT * FROM aph_things
            WHERE username = %s
            """, (username,))
            return cursor.fetchall()

    def get_order_by_salesman_username(self, salesman_username):
        with self.connection.cursor() as cursor:
            cursor.execute("""
            SELECT * FROM aph_things
            WHERE salesman_username = %s
            """, (salesman_username,))
            return cursor.fetchall()

    def get_thing_by_customer(self, username, item_name):
        with self.connection.cursor() as cursor:
            cursor.execute("""
            SELECT * FROM aph_things
            WHERE username = %s AND item_name = %s
            """, (username, item_name))
            return cursor.fetchone()

    def update_status_in_order(self, status, token):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
            UPDATE aph_things
            SET status = %s
            WHERE order_token = %s
            """, (status, token))
        self.connection.commit()

    def update_rating_in_user(self, chat_id, rating):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
            UPDATE aph_users
            SET number_of_ratings = number_of_ratings + 1, sum_of_ratings = sum_of_ratings + %s
            WHERE chat_id = %s
            """, (rating, chat_id))
        self.connection.commit()

    def update_salesman_username_in_order(self, salesman_username, token):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
            UPDATE aph_things
            SET salesman_username = %s
            WHERE order_token = %s
            """, (salesman_username, token))
        self.connection.commit()

    def update_percent_and_date_in_order(self, percent, date, token):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
            UPDATE aph_things
            SET delivery_markup = %s, finish_date = %s
            WHERE order_token = %s
            """, (percent, date, token))
        self.connection.commit()

    def update_number_oreders_in_param(self, param, chat_id):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
            UPDATE aph_users
            SET {param} = {param} + 1
            WHERE chat_id = %s
            """, (chat_id))
        self.connection.commit()
