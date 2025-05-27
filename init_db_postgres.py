from db import get_db_connection

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            company TEXT,
            amount REAL,
            paid_amount REAL DEFAULT 0,
            order_date TEXT,
            payment_date TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS order_lines (
            order_id INTEGER,
            description TEXT,
            quantity INTEGER,
            rate REAL
        )
    ''')

    conn.commit()
    conn.close()

init_db()
