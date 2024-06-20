import sqlite3

class ExchangeDatabase:
    def __init__(self, db_name='exchange-project.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_funds (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            currency_amount REAL,
            currency_type TEXT,
            date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            currency_amount REAL,
            transaction_date TEXT,
            description TEXT,
            currency_type TEXT,
            currency_rate REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS exchange_rates (
            base_currency TEXT,
            target_currency TEXT,
            rate REAL,
            last_updated TIMESTAMP,
            PRIMARY KEY (base_currency, target_currency)
        )
        ''')

        self.conn.commit()

    def insert_user(self, username, password, email):
        self.cursor.execute('''
        INSERT INTO users (username, password, email) VALUES (?, ?, ?)
        ''', (username, password, email))
        self.conn.commit()

    def insert_user_fund(self, user_id, currency_amount, currency_type, date):
        self.cursor.execute('''
        INSERT INTO user_funds (user_id, currency_amount, currency_type, date) VALUES (?, ?, ?, ?)
        ''', (user_id, currency_amount, currency_type, date))
        self.conn.commit()

    def update_user_fund(self, user_id, currency_amount, currency_type, date):
        # Check if the user already has an entry for this currency_type
        self.cursor.execute('''
        SELECT * FROM user_funds WHERE user_id = ? AND currency_type = ?
        ''', (user_id, currency_type))
        fund = self.cursor.fetchone()

        if fund:
            # Update the existing fund amount
            new_amount = fund[2] + currency_amount
            self.cursor.execute('''
            UPDATE user_funds SET currency_amount = ?, date = ? WHERE user_id = ? AND currency_type = ?
            ''', (new_amount, date, user_id, currency_type))
        else:
            # Insert a new fund entry
            self.insert_user_fund(user_id, currency_amount, currency_type, date)

        self.conn.commit()

    def insert_transaction(self, user_id, currency_amount, transaction_date, description, currency_type):
        self.cursor.execute('''
        INSERT INTO transactions (user_id, currency_amount, transaction_date, description, currency_type) VALUES (?, ?, ?, ?, ?)
        ''', (user_id, currency_amount, transaction_date, description, currency_type))
        self.conn.commit()

        # Update the user's funds
        self.update_user_fund(user_id, currency_amount, currency_type, transaction_date)

    def query_users(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()

    def query_user_funds(self):
        self.cursor.execute('SELECT * FROM user_funds')
        return self.cursor.fetchall()

    def query_transactions(self):
        self.cursor.execute('SELECT * FROM transactions')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

db_instance = ExchangeDatabase()
db_cursor = db_instance.cursor
