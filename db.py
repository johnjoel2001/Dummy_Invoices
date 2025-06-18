# import sqlite3
# from datetime import datetime

# def init_db():
#     conn = sqlite3.connect("orders.db")
#     c = conn.cursor()

#     c.execute('''CREATE TABLE IF NOT EXISTS orders (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         company TEXT,
#         amount REAL,
#         paid_amount REAL DEFAULT 0,
#         order_date TEXT,
#         payment_date TEXT
#     )''')

#     c.execute('''CREATE TABLE IF NOT EXISTS order_lines (
#         order_id INTEGER,
#         description TEXT,
#         quantity INTEGER,
#         rate REAL,
#         FOREIGN KEY(order_id) REFERENCES orders(id)
#     )''')

#     conn.commit()
#     conn.close()

# def add_order(company, orders):
#     total = sum(round(o['quantity'] * o['rate'], 2) for o in orders)
#     order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     conn = sqlite3.connect("orders.db")
#     c = conn.cursor()
#     c.execute("INSERT INTO orders (company, amount, order_date) VALUES (?, ?, ?)", (company.lower(), total, order_date))
#     order_id = c.lastrowid

#     for o in orders:
#         c.execute("INSERT INTO order_lines (order_id, description, quantity, rate) VALUES (?, ?, ?, ?)",
#                   (order_id, o['description'], o['quantity'], o['rate']))

#     conn.commit()
#     conn.close()
#     total_qty = sum(o['quantity'] for o in orders)
#     return total, order_id, total_qty

# def get_all_companies():
#     conn = sqlite3.connect("orders.db")
#     c = conn.cursor()
#     c.execute("SELECT DISTINCT company FROM orders")
#     rows = [row[0] for row in c.fetchall()]
#     conn.close()
#     return rows

# def get_pending_orders_with_items():
#     conn = sqlite3.connect("orders.db")
#     c = conn.cursor()
#     c.execute("SELECT id, company, amount, paid_amount, order_date FROM orders WHERE amount > paid_amount ORDER BY id")
#     orders = c.fetchall()

#     result = []
#     for order_id, company, amount, paid, order_date in orders:
#         c.execute("SELECT description, quantity, rate FROM order_lines WHERE order_id = ?", (order_id,))
#         items = c.fetchall()
#         item_total = sum(q * r for _, q, r in items)
#         shipping_fee = round(amount - item_total, 2)
#         result.append({
#             "order_id": order_id,
#             "company": company,
#             "amount": amount,
#             "paid_amount": paid,
#             "order_date": order_date.split(" ")[0],
#             "items": items,
#             "shipping_fee": shipping_fee if shipping_fee > 0 else None
#         })

#     conn.close()
#     return result

# def get_all_orders_with_items():
#     conn = sqlite3.connect("orders.db")
#     c = conn.cursor()

#     c.execute("SELECT id, company, amount, paid_amount, order_date, payment_date FROM orders ORDER BY id")
#     orders = c.fetchall()

#     result = []
#     for order_id, company, amount, paid, order_date, payment_date in orders:
#         c.execute("SELECT description, quantity, rate FROM order_lines WHERE order_id = ?", (order_id,))
#         items = c.fetchall()
#         item_total = sum(q * r for _, q, r in items)
#         shipping_fee = round(amount - item_total, 2)

#         result.append({
#             "order_id": order_id,
#             "company": company,
#             "amount": amount,
#             "paid_amount": paid,
#             "order_date": order_date.split(" ")[0],
#             "payment_date": payment_date.split(" ")[0] if payment_date else None,
#             "items": items,
#             "shipping_fee": shipping_fee if shipping_fee > 0 else None
#         })

#     conn.close()
#     return result

# def apply_payment(company, amount):
#     conn = sqlite3.connect("orders.db")
#     c = conn.cursor()
#     c.execute("SELECT id, paid_amount, amount FROM orders WHERE company = ? AND amount > paid_amount ORDER BY id",
#               (company.lower(),))
#     orders = c.fetchall()

#     if not orders:
#         conn.close()
#         return "No unpaid orders found."

#     if len(orders) == 1:
#         order_id, paid, total = orders[0]
#         new_paid = paid + amount
#         payment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         if new_paid > total:
#             conn.close()
#             return "⚠️ Payment exceeds invoice total."
#         c.execute("UPDATE orders SET paid_amount = ?, payment_date = ? WHERE id = ?", (new_paid, payment_date, order_id))
#         conn.commit()
#         conn.close()
#         return f"✅ ₹{amount} applied to invoice. Remaining balance: ₹{round(total - new_paid, 2)}"
#     else:
#         conn.close()
#         return {
#             "multiple": True,
#             "invoices": orders,
#             "amount": amount
#         }

# def apply_partial_to_invoice(order_id, amount):
#     conn = sqlite3.connect("orders.db")
#     c = conn.cursor()
#     c.execute("SELECT paid_amount, amount FROM orders WHERE id = ?", (order_id,))
#     row = c.fetchone()
#     if not row:
#         conn.close()
#         return "Invoice not found."
#     paid, total = row
#     new_paid = paid + amount
#     if new_paid > total:
#         conn.close()
#         return "⚠️ Payment exceeds invoice total."
#     payment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     c.execute("UPDATE orders SET paid_amount = ?, payment_date = ? WHERE id = ?", (new_paid, payment_date, order_id))
#     conn.commit()
#     conn.close()
#     return f"✅ ₹{amount} applied to invoice #{order_id}. Remaining: ₹{round(total - new_paid, 2)}"

# def delete_order_by_serial(serial_number):
#     conn = sqlite3.connect("orders.db")
#     c = conn.cursor()
#     c.execute("SELECT id FROM orders ORDER BY id")
#     rows = c.fetchall()
#     if serial_number < 1 or serial_number > len(rows):
#         conn.close()
#         return False
#     order_id = rows[serial_number - 1][0]
#     c.execute("DELETE FROM order_lines WHERE order_id = ?", (order_id,))
#     c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
#     conn.commit()
#     conn.close()
#     return True


# def delete_order_by_id(order_id):
#     conn = sqlite3.connect("orders.db")
#     c = conn.cursor()
#     c.execute("DELETE FROM order_lines WHERE order_id = ?", (order_id,))
#     c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
#     conn.commit()
#     conn.close()
#     return True

# def find_unpaid_orders_by_company(company):
#     conn = sqlite3.connect("orders.db")
#     c = conn.cursor()
#     c.execute("SELECT id, amount, paid_amount FROM orders WHERE company = ? AND paid_amount < amount ORDER BY id",
#               (company.lower(),))
#     rows = c.fetchall()
#     conn.close()
#     return rows

# def get_total_quantity(order_id):
#     conn = sqlite3.connect("orders.db")
#     c = conn.cursor()
#     c.execute("SELECT SUM(quantity) FROM order_lines WHERE order_id = ?", (order_id,))
#     qty = c.fetchone()[0]
#     conn.close()
#     return qty or 0

# def add_shipping_fee(order_id, shipping_amount):
#     conn = sqlite3.connect("orders.db")
#     c = conn.cursor()
#     c.execute("SELECT amount FROM orders WHERE id = ?", (order_id,))
#     original_total = c.fetchone()[0]
#     new_total = original_total + shipping_amount
#     c.execute("UPDATE orders SET amount = ? WHERE id = ?", (new_total, order_id))
#     conn.commit()
#     conn.close()
#     return new_total

# def find_orders_with_shipping(company):
#     conn = sqlite3.connect("orders.db")
#     c = conn.cursor()
#     c.execute("""
#         SELECT o.id, o.amount, SUM(l.quantity * l.rate) as item_total
#         FROM orders o
#         JOIN order_lines l ON o.id = l.order_id
#         WHERE o.company = ? AND o.amount > o.paid_amount
#         GROUP BY o.id
#         HAVING o.amount > item_total
#         ORDER BY o.id
#     """, (company.lower(),))
#     results = c.fetchall()
#     conn.close()
#     return results

# def remove_shipping_fee_by_order(order_id):
#     conn = sqlite3.connect("orders.db")
#     c = conn.cursor()
#     c.execute("SELECT SUM(quantity * rate) FROM order_lines WHERE order_id = ?", (order_id,))
#     item_total = c.fetchone()[0]
#     c.execute("UPDATE orders SET amount = ? WHERE id = ?", (item_total, order_id))
#     conn.commit()
#     conn.close()
#     return item_total



# import psycopg2
# import os
# from urllib.parse import urlparse
# from datetime import datetime

# # def get_db_connection():
# #     result = urlparse(os.getenv("DATABASE_URL"))
# #     return psycopg2.connect(
# #         database=result.path[1:],
# #         user=result.username,
# #         password=result.password,
# #         host=result.hostname,
# #         port=result.port
# #     )


   
# def init_db():
#     conn = get_db_connection()
#     c = conn.cursor()

#     c.execute('''CREATE TABLE IF NOT EXISTS orders (
#         id SERIAL PRIMARY KEY,
#         company TEXT,
#         amount REAL,
#         paid_amount REAL DEFAULT 0,
#         order_date TEXT,
#         payment_date TEXT
#     )''')

#     c.execute('''CREATE TABLE IF NOT EXISTS order_lines (
#         order_id INTEGER,
#         description TEXT,
#         quantity INTEGER,
#         rate REAL
#     )''')

#     conn.commit()
#     conn.close()

# def add_order(company, orders):
#     total = sum(round(o['quantity'] * o['rate'], 2) for o in orders)
#     order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("INSERT INTO orders (company, amount, order_date) VALUES (%s, %s, %s)", (company.lower(), total, order_date))
#     conn.commit()
#     c.execute("SELECT MAX(id) FROM orders")
#     order_id = c.fetchone()[0]

#     for o in orders:
#         c.execute("INSERT INTO order_lines (order_id, description, quantity, rate) VALUES (%s, %s, %s, %s)",
#                   (order_id, o['description'], o['quantity'], o['rate']))

#     conn.commit()
#     conn.close()
#     total_qty = sum(o['quantity'] for o in orders)
#     return total, order_id, total_qty

# def get_all_companies():
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT DISTINCT company FROM orders")
#     rows = [row[0] for row in c.fetchall()]
#     conn.close()
#     return rows

# def get_pending_orders_with_items():
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT id, company, amount, paid_amount, order_date FROM orders WHERE amount > paid_amount ORDER BY id")
#     orders = c.fetchall()

#     result = []
#     for order_id, company, amount, paid, order_date in orders:
#         c.execute("SELECT description, quantity, rate FROM order_lines WHERE order_id = %s", (order_id,))
#         items = c.fetchall()
#         item_total = sum(q * r for _, q, r in items)
#         shipping_fee = round(amount - item_total, 2)
#         result.append({
#             "order_id": order_id,
#             "company": company,
#             "amount": amount,
#             "paid_amount": paid,
#             "order_date": order_date.split(" ")[0],
#             "items": items,
#             "shipping_fee": shipping_fee if shipping_fee > 0 else None
#         })

#     conn.close()
#     return result

# def get_all_orders_with_items():
#     conn = get_db_connection()
#     c = conn.cursor()

#     c.execute("SELECT id, company, amount, paid_amount, order_date, payment_date FROM orders ORDER BY id")
#     orders = c.fetchall()

#     result = []
#     for order_id, company, amount, paid, order_date, payment_date in orders:
#         c.execute("SELECT description, quantity, rate FROM order_lines WHERE order_id = %s", (order_id,))
#         items = c.fetchall()
#         item_total = sum(q * r for _, q, r in items)
#         shipping_fee = round(amount - item_total, 2)

#         result.append({
#             "order_id": order_id,
#             "company": company,
#             "amount": amount,
#             "paid_amount": paid,
#             "order_date": order_date.split(" ")[0],
#             "payment_date": payment_date.split(" ")[0] if payment_date else None,
#             "items": items,
#             "shipping_fee": shipping_fee if shipping_fee > 0 else None
#         })

#     conn.close()
#     return result

# def apply_payment(company, amount):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT id, paid_amount, amount FROM orders WHERE company = %s AND amount > paid_amount ORDER BY id",
#               (company.lower(),))
#     orders = c.fetchall()

#     if not orders:
#         conn.close()
#         return "No unpaid orders found."

#     if len(orders) == 1:
#         order_id, paid, total = orders[0]
#         new_paid = paid + amount
#         payment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         if new_paid > total:
#             conn.close()
#             return "⚠️ Payment exceeds invoice total."
#         c.execute("UPDATE orders SET paid_amount = %s, payment_date = %s WHERE id = %s", (new_paid, payment_date, order_id))
#         conn.commit()
#         conn.close()
#         return f"✅ ₹{amount} applied to invoice. Remaining balance: ₹{round(total - new_paid, 2)}"
#     else:
#         conn.close()
#         return {
#             "multiple": True,
#             "invoices": orders,
#             "amount": amount
#         }

# def apply_partial_to_invoice(order_id, amount):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT paid_amount, amount FROM orders WHERE id = %s", (order_id,))
#     row = c.fetchone()
#     if not row:
#         conn.close()
#         return "Invoice not found."
#     paid, total = row
#     new_paid = paid + amount
#     if new_paid > total:
#         conn.close()
#         return "⚠️ Payment exceeds invoice total."
#     payment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     c.execute("UPDATE orders SET paid_amount = %s, payment_date = %s WHERE id = %s", (new_paid, payment_date, order_id))
#     conn.commit()
#     conn.close()
#     return f"✅ ₹{amount} applied to invoice #{order_id}. Remaining: ₹{round(total - new_paid, 2)}"

# def delete_order_by_serial(serial_number):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT id FROM orders ORDER BY id")
#     rows = c.fetchall()
#     if serial_number < 1 or serial_number > len(rows):
#         conn.close()
#         return False
#     order_id = rows[serial_number - 1][0]
#     c.execute("DELETE FROM order_lines WHERE order_id = %s", (order_id,))
#     c.execute("DELETE FROM orders WHERE id = %s", (order_id,))
#     conn.commit()
#     conn.close()
#     return True

# def delete_order_by_id(order_id):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("DELETE FROM order_lines WHERE order_id = %s", (order_id,))
#     c.execute("DELETE FROM orders WHERE id = %s", (order_id,))
#     conn.commit()
#     conn.close()
#     return True

# def find_unpaid_orders_by_company(company):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT id, amount, paid_amount FROM orders WHERE company = %s AND paid_amount < amount ORDER BY id",
#               (company.lower(),))
#     rows = c.fetchall()
#     conn.close()
#     return rows

# def get_total_quantity(order_id):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT SUM(quantity) FROM order_lines WHERE order_id = %s", (order_id,))
#     qty = c.fetchone()[0]
#     conn.close()
#     return qty or 0

# def add_shipping_fee(order_id, shipping_amount):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT amount FROM orders WHERE id = %s", (order_id,))
#     original_total = c.fetchone()[0]
#     new_total = original_total + shipping_amount
#     c.execute("UPDATE orders SET amount = %s WHERE id = %s", (new_total, order_id))
#     conn.commit()
#     conn.close()
#     return new_total

# def find_orders_with_shipping(company):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("""
#         SELECT o.id, o.amount, SUM(l.quantity * l.rate) as item_total
#         FROM orders o
#         JOIN order_lines l ON o.id = l.order_id
#         WHERE o.company = %s AND o.amount > o.paid_amount
#         GROUP BY o.id
#         HAVING o.amount > item_total
#         ORDER BY o.id
#     """, (company.lower(),))
#     results = c.fetchall()
#     conn.close()
#     return results

# def remove_shipping_fee_by_order(order_id):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT SUM(quantity * rate) FROM order_lines WHERE order_id = %s", (order_id,))
#     item_total = c.fetchone()[0]
#     c.execute("UPDATE orders SET amount = %s WHERE id = %s", (item_total, order_id))
#     conn.commit()
#     conn.close()
#     return item_total


# import os
# import sqlite3
# from datetime import datetime
# import sqlalchemy
# from sqlalchemy.engine.url import make_url

# def get_db_connection():
#     db_url = os.getenv("DATABASE_URL", "sqlite:///dev.db")
#     url = make_url(db_url)

#     if url.drivername.startswith("sqlite"):
#         conn = sqlite3.connect(url.database)
#         conn.row_factory = sqlite3.Row
#         return conn
#     elif url.drivername.startswith("postgresql"):
#         import psycopg2
#         return psycopg2.connect(
#             dbname=url.database,
#             user=url.username,
#             password=url.password,
#             host=url.host,
#             port=url.port
#         )
#     else:
#         raise ValueError("Unsupported database driver")

# def init_db():
#     conn = get_db_connection()
#     c = conn.cursor()

#     c.execute('''CREATE TABLE IF NOT EXISTS orders (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         company TEXT,
#         amount REAL,
#         paid_amount REAL DEFAULT 0,
#         order_date TEXT,
#         payment_date TEXT
#     )''')

#     c.execute('''CREATE TABLE IF NOT EXISTS order_lines (
#         order_id INTEGER,
#         description TEXT,
#         quantity INTEGER,
#         rate REAL
#     )''')

#     conn.commit()
#     conn.close()

# def add_order(company, orders):
#     total = sum(round(o['quantity'] * o['rate'], 2) for o in orders)
#     order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("INSERT INTO orders (company, amount, order_date) VALUES (?, ?, ?)",
#               (company.lower(), total, order_date))
#     conn.commit()
#     c.execute("SELECT MAX(id) FROM orders")
#     order_id = c.fetchone()[0]

#     for o in orders:
#         c.execute("INSERT INTO order_lines (order_id, description, quantity, rate) VALUES (?, ?, ?, ?)",
#                   (order_id, o['description'], o['quantity'], o['rate']))

#     conn.commit()
#     conn.close()
#     total_qty = sum(o['quantity'] for o in orders)
#     return total, order_id, total_qty

# def get_all_companies():
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT DISTINCT company FROM orders")
#     rows = [row[0] for row in c.fetchall()]
#     conn.close()
#     return rows

# def get_pending_orders_with_items():
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT id, company, amount, paid_amount, order_date FROM orders WHERE amount > paid_amount ORDER BY id")
#     orders = c.fetchall()

#     result = []
#     for order_id, company, amount, paid, order_date in orders:
#         c.execute("SELECT description, quantity, rate FROM order_lines WHERE order_id = ?", (order_id,))
#         items = c.fetchall()
#         item_total = sum(q * r for _, q, r in items)
#         shipping_fee = round(amount - item_total, 2)
#         result.append({
#             "order_id": order_id,
#             "company": company,
#             "amount": amount,
#             "paid_amount": paid,
#             "order_date": order_date.split(" ")[0],
#             "items": items,
#             "shipping_fee": shipping_fee if shipping_fee > 0 else None
#         })

#     conn.close()
#     return result

# def get_all_orders_with_items():
#     conn = get_db_connection()
#     c = conn.cursor()

#     c.execute("SELECT id, company, amount, paid_amount, order_date, payment_date FROM orders ORDER BY id")
#     orders = c.fetchall()

#     result = []
#     for order_id, company, amount, paid, order_date, payment_date in orders:
#         c.execute("SELECT description, quantity, rate FROM order_lines WHERE order_id = ?", (order_id,))
#         items = c.fetchall()
#         item_total = sum(q * r for _, q, r in items)
#         shipping_fee = round(amount - item_total, 2)

#         result.append({
#             "order_id": order_id,
#             "company": company,
#             "amount": amount,
#             "paid_amount": paid,
#             "order_date": order_date.split(" ")[0],
#             "payment_date": payment_date.split(" ")[0] if payment_date else None,
#             "items": items,
#             "shipping_fee": shipping_fee if shipping_fee > 0 else None
#         })

#     conn.close()
#     return result

# def apply_payment(company, amount):
#     conn = get_db_connection()
#     cur = conn.cursor()

#     cur.execute("""
#         SELECT id, paid_amount, amount, order_date
#         FROM orders
#         WHERE company = ? AND amount > paid_amount
#         ORDER BY order_date ASC, id ASC
#     """, (company,))

#     invoices = cur.fetchall()

#     if not invoices:
#         return "✅ No unpaid invoices for this customer."

#     if len(invoices) == 1:
#         order_id, paid, total, _ = invoices[0]
#         result = apply_partial_to_invoice(order_id, amount)
#         return result

#     # Multiple unpaid invoices — return for bot to decide
#     return {
#         "multiple": True,
#         "amount": amount,
#         "invoices": invoices  # Each is (order_id, paid, total, order_date)
#     }

# def apply_partial_to_invoice(order_id, amount):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT paid_amount, amount FROM orders WHERE id = ?", (order_id,))
#     row = c.fetchone()
#     if not row:
#         conn.close()
#         return "Invoice not found."
#     paid, total = row
#     new_paid = paid + amount
#     if new_paid > total:
#         conn.close()
#         return "⚠️ Payment exceeds invoice total."
#     payment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     c.execute("UPDATE orders SET paid_amount = ?, payment_date = ? WHERE id = ?", (new_paid, payment_date, order_id))
#     conn.commit()
#     conn.close()
#     return f"✅ ₹{amount} applied to invoice #{order_id}. Remaining: ₹{round(total - new_paid, 2)}"

# def delete_order_by_serial(serial_number):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT id FROM orders ORDER BY id")
#     rows = c.fetchall()
#     if serial_number < 1 or serial_number > len(rows):
#         conn.close()
#         return False
#     order_id = rows[serial_number - 1][0]
#     c.execute("DELETE FROM order_lines WHERE order_id = ?", (order_id,))
#     c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
#     conn.commit()
#     conn.close()
#     return True

# def delete_order_by_id(order_id):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("DELETE FROM order_lines WHERE order_id = ?", (order_id,))
#     c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
#     conn.commit()
#     conn.close()
#     return True

# def find_unpaid_orders_by_company(company):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT id, amount, paid_amount FROM orders WHERE company = ? AND paid_amount < amount ORDER BY id",
#               (company.lower(),))
#     rows = c.fetchall()
#     conn.close()
#     return rows

# def get_total_quantity(order_id):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT SUM(quantity) FROM order_lines WHERE order_id = ?", (order_id,))
#     qty = c.fetchone()[0]
#     conn.close()
#     return qty or 0

# def add_shipping_fee(order_id, shipping_amount):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT amount FROM orders WHERE id = ?", (order_id,))
#     original_total = c.fetchone()[0]
#     new_total = original_total + shipping_amount
#     c.execute("UPDATE orders SET amount = ? WHERE id = ?", (new_total, order_id))
#     conn.commit()
#     conn.close()
#     return new_total

# def find_orders_with_shipping(company):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("""
#         SELECT o.id, o.amount, SUM(l.quantity * l.rate) as item_total
#         FROM orders o
#         JOIN order_lines l ON o.id = l.order_id
#         WHERE o.company = ? AND o.amount > o.paid_amount
#         GROUP BY o.id
#         HAVING o.amount > item_total
#         ORDER BY o.id
#     """, (company.lower(),))
#     results = c.fetchall()
#     conn.close()
#     return results

# def remove_shipping_fee_by_order(order_id):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT SUM(quantity * rate) FROM order_lines WHERE order_id = ?", (order_id,))
#     item_total = c.fetchone()[0]
#     c.execute("UPDATE orders SET amount = ? WHERE id = ?", (item_total, order_id))
#     conn.commit()
#     conn.close()
#     return item_total

import os
import psycopg2
import urllib.parse
from datetime import datetime

def get_db_connection():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL not set in environment variables")

    parsed_url = urllib.parse.urlparse(url)

    return psycopg2.connect(
        dbname=parsed_url.path[1:],
        user=parsed_url.username,
        password=parsed_url.password,
        host=parsed_url.hostname,
        port=parsed_url.port,
        sslmode="require"
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            company TEXT NOT NULL,
            amount NUMERIC NOT NULL,
            paid_amount NUMERIC DEFAULT 0,
            shipping_fee NUMERIC DEFAULT 0,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            payment_date TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
            description TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            rate NUMERIC NOT NULL
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("\u2705 Database initialized.")

def add_order(company, items):
    conn = get_db_connection()
    cur = conn.cursor()

    total = sum(round(o['quantity'] * o['rate'], 2) for o in items)

    cur.execute("""
        INSERT INTO orders (company, amount)
        VALUES (%s, %s) RETURNING id;
    """, (company, total))
    order_id = cur.fetchone()[0]

    total_qty = 0
    for item in items:
        cur.execute("""
            INSERT INTO order_items (order_id, description, quantity, rate)
            VALUES (%s, %s, %s, %s);
        """, (order_id, item['description'], item['quantity'], item['rate']))
        total_qty += item['quantity']

    conn.commit()
    cur.close()
    conn.close()

    return total, order_id, total_qty

def get_all_companies():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT company FROM orders;")
    companies = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return companies

def get_all_orders_with_items():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT o.id, o.company, o.amount, o.paid_amount, o.order_date, o.payment_date, o.shipping_fee
        FROM orders o
        ORDER BY o.order_date DESC;
    """)
    orders = []
    for row in cur.fetchall():
        order_id, company, amount, paid, order_date, payment_date, shipping_fee = row
        cur.execute("SELECT description, quantity, rate FROM order_items WHERE order_id = %s", (order_id,))
        items = cur.fetchall()
        orders.append({
            "id": order_id,
            "company": company,
            "amount": float(amount),
            "paid_amount": float(paid),
            "order_date": order_date,
            "payment_date": payment_date,
            "shipping_fee": float(shipping_fee),
            "items": items
        })
    cur.close()
    conn.close()
    return orders

def get_pending_orders_with_items():
    all_orders = get_all_orders_with_items()
    return [o for o in all_orders if o["amount"] > o["paid_amount"]]

def delete_order_by_serial(order_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM orders WHERE id = %s RETURNING id", (order_id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return bool(result)

def apply_payment(company, amount):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, paid_amount, amount, order_date
        FROM orders
        WHERE company = %s AND amount > paid_amount
        ORDER BY order_date ASC, id ASC;
    """, (company,))
    invoices = cur.fetchall()

    if not invoices:
        return "\u2705 No unpaid invoices for this customer."

    if len(invoices) == 1:
        order_id = invoices[0][0]
        result = apply_partial_to_invoice(order_id, amount)
        return result

    return {
        "multiple": True,
        "amount": amount,
        "invoices": invoices
    }

def apply_partial_to_invoice(order_id, amount):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT paid_amount, amount FROM orders WHERE id = %s;", (order_id,))
    row = cur.fetchone()
    if not row:
        return "\u274C Invoice not found."

    paid, total = row
    new_paid = paid + amount
    if new_paid > total:
        return f"⚠️ Cannot apply ₹{amount}. Invoice already paid ₹{paid} of ₹{total}."

    cur.execute("""
        UPDATE orders SET paid_amount = %s, payment_date = %s WHERE id = %s;
    """, (new_paid, datetime.now(), order_id))
    conn.commit()
    cur.close()
    conn.close()

    balance = round(total - new_paid, 2)
    return f"✅ ₹{amount} applied to invoice #{order_id}. Remaining: ₹{balance}"

def find_orders_with_shipping(company):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, amount, (
            SELECT SUM(quantity * rate) FROM order_items WHERE order_id = orders.id
        ) AS items_total
        FROM orders
        WHERE company = %s AND shipping_fee > 0;
    """, (company,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def remove_shipping_fee_by_order(order_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET shipping_fee = 0 WHERE id = %s RETURNING amount, paid_amount;", (order_id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result[0] if result else 0

def add_shipping_fee(order_id, fee):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET shipping_fee = %s, amount = amount + %s WHERE id = %s RETURNING amount;", (fee, fee, order_id))
    new_total = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return new_total

