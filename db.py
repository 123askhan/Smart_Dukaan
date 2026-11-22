
# import sqlite3

# DB_NAME = "smartdukaan.db"


# def get_connection():
#     conn = sqlite3.connect(DB_NAME)
#     conn.execute("PRAGMA foreign_keys = ON")
#     return conn


# def create_tables():
#     conn = get_connection()
#     cursor = conn.cursor()

#     # Products table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS products (
#             product_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             category TEXT,
#             price REAL NOT NULL,
#             quantity INTEGER NOT NULL DEFAULT 0,
#             low_stock_limit INTEGER DEFAULT 5
#         )
#     """)

#     # Customers table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS customers (
#             customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             phone TEXT
#         )
#     """)

#     # Sales table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS sales (
#             sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             customer_id INTEGER,
#             total_amount REAL NOT NULL,
#             sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (customer_id)
#                 REFERENCES customers(customer_id)
#         )
#     """)

#     # Sale items table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS sale_items (
#             item_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             sale_id INTEGER NOT NULL,
#             product_id INTEGER NOT NULL,
#             quantity INTEGER NOT NULL,
#             price REAL NOT NULL,
#             FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
#             FOREIGN KEY (product_id) REFERENCES products(product_id)
#         )
#     """)

#     # Expenses table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS expenses (
#             expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             description TEXT NOT NULL,
#             amount REAL NOT NULL,
#             expense_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)

#     # Customer credit table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS customer_credit (
#             credit_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             customer_id INTEGER NOT NULL,
#             amount REAL NOT NULL,
#             status TEXT DEFAULT 'Pending',
#             credit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (customer_id)
#                 REFERENCES customers(customer_id)
#         )
#     """)

#     conn.commit()
#     conn.close()

#     print("SmartDukaan database created successfully!")


# if __name__ == "__main__":
#     create_tables()




import sqlite3
import pandas as pd

DB_NAME = "smartdukaan.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            low_stock_limit INTEGER DEFAULT 5
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            total_amount REAL NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            expense_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("PRAGMA table_info(expenses)")
    columns = [row[1] for row in cursor.fetchall()]

    if "category" not in columns:
        cursor.execute("""
            ALTER TABLE expenses
            ADD COLUMN category TEXT DEFAULT 'Other'
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_credit (
            credit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            credit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        )
    """)

    conn.commit()
    conn.close()





def add_product(name, category, price, quantity, low_stock_limit):

    name = name.strip()
    category = category.strip()

    print("\n--- ADD PRODUCT DEBUG ---")
    print("Name:", repr(name))
    print("Category:", repr(category))
    print("Price:", repr(price))
    print("Quantity:", repr(quantity))
    print("Low Stock Limit:", repr(low_stock_limit))

    if not name:
        return False

    if price <= 0 or quantity < 0 or low_stock_limit < 0:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT product_id
        FROM products
        WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
    """, (name,))

    if cursor.fetchone():
        conn.close()
        return False

    values = (name, category, price, quantity, low_stock_limit)

    print("Values being inserted:", values)

    cursor.execute("""
        INSERT INTO products
        (name, category, price, quantity, low_stock_limit)
        VALUES (?, ?, ?, ?, ?)
    """, values)

    conn.commit()

    print("Inserted record:",
          cursor.execute("""
              SELECT * FROM products
              WHERE product_id = ?
          """, (cursor.lastrowid,)).fetchone())

    conn.close()

    return True





def get_products():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM products ORDER BY product_id DESC", conn
    )
    conn.close()
    return df


def set_stock(product_id, new_quantity):

    if new_quantity < 0:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET quantity = ?
        WHERE product_id = ?
    """, (new_quantity, product_id))

    success = cursor.rowcount == 1

    conn.commit()
    conn.close()

    return success



def update_product(product_id, name, category, price, low_stock_limit):
    conn = get_connection()
    conn.execute("""
        UPDATE products
        SET name=?, category=?, price=?, low_stock_limit=?
        WHERE product_id=?
    """, (name, category, price, low_stock_limit, product_id))
    conn.commit()
    conn.close()


def update_stock(product_id, quantity_change):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET quantity = quantity + ?
        WHERE product_id = ?
        AND quantity + ? >= 0
    """, (quantity_change, product_id, quantity_change))

    success = cursor.rowcount == 1
    conn.commit()
    conn.close()
    return success


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM products WHERE product_id=?",
        (product_id,)
    )

    success = cursor.rowcount == 1
    conn.commit()
    conn.close()
    return success


def record_sale(product_id, quantity_sold):
    if quantity_sold <= 0:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT price, quantity FROM products WHERE product_id = ?",
        (product_id,)
    )

    product = cursor.fetchone()

    if product is None:
        conn.close()
        return False

    price, available_quantity = product

    if quantity_sold > available_quantity:
        conn.close()
        return False

    total_amount = price * quantity_sold

    cursor.execute("""
        INSERT INTO sales (total_amount)
        VALUES (?)
    """, (total_amount,))

    sale_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO sale_items
        (sale_id, product_id, quantity, price)
        VALUES (?, ?, ?, ?)
    """, (sale_id, product_id, quantity_sold, price))

    cursor.execute("""
        UPDATE products
        SET quantity = quantity - ?
        WHERE product_id = ?
    """, (quantity_sold, product_id))

    conn.commit()
    conn.close()

    return True


def get_sales():
    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            s.sale_id,
            p.name AS product_name,
            si.quantity,
            si.price,
            s.total_amount,
            s.sale_date
        FROM sales s
        JOIN sale_items si ON s.sale_id = si.sale_id
        JOIN products p ON si.product_id = p.product_id
        ORDER BY s.sale_id DESC
    """, conn)

    conn.close()
    return df



# ---------------- EXPENSE MANAGEMENT ----------------


def add_expense(category, description, amount, expense_date):

    print("\n========== ADD EXPENSE DEBUG ==========")
    print("Function called!")
    print("Category:", category)
    print("Description:", description)
    print("Amount:", amount)
    print("Date:", expense_date)

    category = category.strip()
    description = description.strip()

    if not category or not description or amount <= 0:
        return False

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses
        (category, description, amount, expense_date)
        VALUES (?, ?, ?, ?)
    """, (category, description, amount, expense_date))

    print("Inserted expense ID:", cursor.lastrowid)

    conn.commit()
    conn.close()

    print("========== INSERT COMPLETE ==========\n")

    return True



def get_expenses():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM expenses
        ORDER BY expense_id DESC
    """, conn)

    conn.close()

    return df


def update_expense(expense_id, category, description, amount, expense_date):

    category = category.strip()
    description = description.strip()

    if not category or not description or amount <= 0:
        return False

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE expenses
        SET category=?, description=?, amount=?, expense_date=?
        WHERE expense_id=?
    """, (category, description, amount, expense_date, expense_id))

    success = cursor.rowcount == 1

    conn.commit()
    conn.close()

    return success


def delete_expense(expense_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM expenses
        WHERE expense_id=?
    """, (expense_id,))

    success = cursor.rowcount == 1

    conn.commit()
    conn.close()

    return success


# ---------------- CUSTOMER MANAGEMENT ----------------

def add_customer(name, phone):

    name = name.strip()
    phone = phone.strip()

    if not name:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO customers (name, phone)
        VALUES (?, ?)
    """, (name, phone))

    conn.commit()
    conn.close()

    return True


def get_customers():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM customers
        ORDER BY customer_id DESC
    """, conn)

    conn.close()
    return df


def update_customer(customer_id, name, phone):

    name = name.strip()
    phone = phone.strip()

    if not name:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE customers
        SET name = ?, phone = ?
        WHERE customer_id = ?
    """, (name, phone, customer_id))

    success = cursor.rowcount == 1

    conn.commit()
    conn.close()

    return success


def delete_customer(customer_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM customer_credit
        WHERE customer_id = ?
    """, (customer_id,))

    credit_count = cursor.fetchone()[0]

    if credit_count > 0:
        conn.close()
        return False

    cursor.execute("""
        DELETE FROM customers
        WHERE customer_id = ?
    """, (customer_id,))

    success = cursor.rowcount == 1

    conn.commit()
    conn.close()

    return success



# ---------------- CUSTOMER CREDIT MANAGEMENT ----------------

def add_customer_credit(customer_id, amount):

    if amount <= 0:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO customer_credit
        (customer_id, amount, status)
        VALUES (?, ?, 'Pending')
    """, (customer_id, amount))

    success = cursor.rowcount == 1

    conn.commit()
    conn.close()

    return success


def get_customer_credits():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            cc.credit_id,
            c.name AS customer_name,
            c.phone,
            cc.customer_id,
            cc.amount,
            cc.status,
            cc.credit_date
        FROM customer_credit cc
        JOIN customers c
            ON cc.customer_id = c.customer_id
        ORDER BY cc.credit_id DESC
    """, conn)

    conn.close()
    return df


def update_credit_status(credit_id, status):

    if status not in ["Pending", "Paid"]:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE customer_credit
        SET status = ?
        WHERE credit_id = ?
    """, (status, credit_id))

    success = cursor.rowcount == 1

    conn.commit()
    conn.close()

    return success


def delete_customer_credit(credit_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM customer_credit
        WHERE credit_id = ?
    """, (credit_id,))

    success = cursor.rowcount == 1

    conn.commit()
    conn.close()

    return success





