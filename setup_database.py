import sqlite3
import os

print("Creating Pixel Haven database...")

# Database path
db_path = 'instance/pixel_haven.db'

# Remove old database if exists
if os.path.exists(db_path):
    os.remove(db_path)

# Create instance folder
if not os.path.exists('instance'):
    os.makedirs('instance')

conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("Creating tables...")

# Create tables
cur.execute("""
CREATE TABLE employee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE supplier (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_email TEXT,
    phone TEXT,
    address TEXT
)
""")

cur.execute("""
CREATE TABLE product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    stock_quantity INTEGER NOT NULL,
    category TEXT,
    supplier_id INTEGER NOT NULL
)
""")

cur.execute("""
CREATE TABLE customer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    address TEXT
)
""")

cur.execute("""
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    customer_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL
)
""")

cur.execute("""
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL
)
""")

print("📊 Inserting sample data...")

# ----- Employees (2 rows) -----
cur.execute("INSERT INTO employee (username, password_hash, role) VALUES ('admin', 'admin123', 'admin')")
cur.execute("INSERT INTO employee (username, password_hash, role) VALUES ('staff1', 'staff123', 'staff')")

# ----- Suppliers (10+ rows) -----
suppliers = [
    ('NVIDIA Corp', 'sales@nvidia.com', '1-800-NVIDIA', '2788 San Tomas Expressway, Santa Clara, CA'),
    ('Intel Corporation', 'orders@intel.com', '1-800-538-3373', '2200 Mission College Blvd, Santa Clara, CA'),
    ('AMD Inc', 'support@amd.com', '1-800-538-8450', '2485 Augustine Drive, Santa Clara, CA'),
    ('Corsair Memory', 'sales@corsair.com', '1-888-222-4346', '47100 Bayside Parkway, Fremont, CA'),
    ('Samsung Electronics', 'orders@samsung.com', '1-800-726-7864', '3655 N First St, San Jose, CA'),
    ('Western Digital', 'support@wdc.com', '1-800-275-4932', '5601 Great Oaks Parkway, San Jose, CA'),
    ('Logitech', 'sales@logitech.com', '1-646-454-3200', '7700 Gateway Blvd, Newark, CA'),
    ('ASUS', 'orders@asus.com', '1-812-282-2787', '800 Corporate Way, Fremont, CA'),
    ('MSI', 'support@msi.com', '1-626-271-1004', '901 Canada Court, City of Industry, CA'),
    ('Cooler Master', 'sales@coolermaster.com', '1-909-595-7676', '17170 Rowland St, City of Industry, CA'),
    ('Gigabyte', 'sales@gigabyte.com', '1-626-854-9338', 'City of Industry, CA'),
    ('EVGA', 'support@evga.com', '1-888-881-3842', 'Brea, CA')
]
cur.executemany("INSERT INTO supplier (name, contact_email, phone, address) VALUES (?, ?, ?, ?)", suppliers)

# ----- Products (12+ rows) -----
products = [
    ('NVIDIA RTX 4090', 'Flagship gaming GPU with 24GB GDDR6X', 1599.99, 15, 'GPU', 1),
    ('NVIDIA RTX 4080', 'High-end gaming GPU with 16GB GDDR6X', 1199.99, 25, 'GPU', 1),
    ('AMD RX 7900 XTX', 'High-end AMD GPU with 24GB GDDR6', 999.99, 20, 'GPU', 3),
    ('Intel Core i9-14900K', '24-core desktop processor', 589.99, 40, 'CPU', 2),
    ('AMD Ryzen 9 7950X', '16-core desktop processor', 699.99, 35, 'CPU', 3),
    ('Corsair Vengeance 32GB DDR5', '32GB DDR5 5600MHz memory kit', 129.99, 100, 'Memory', 4),
    ('Samsung 980 Pro 2TB', '2TB NVMe PCIe 4.0 SSD', 179.99, 60, 'Storage', 5),
    ('WD Black SN850X 2TB', '2TB NVMe PCIe 4.0 SSD', 169.99, 55, 'Storage', 6),
    ('Logitech MX Master 3S', 'Wireless performance mouse', 99.99, 75, 'Peripherals', 7),
    ('ASUS ROG Swift Monitor', '27-inch 1440p gaming monitor', 699.99, 25, 'Monitors', 8),
    ('MSI MAG B650 Tomahawk', 'AMD AM5 motherboard', 219.99, 30, 'Motherboard', 9),
    ('Cooler Master Hyper 212', 'CPU air cooler', 44.99, 80, 'Cooling', 10),
    ('Gigabyte AORUS PSU 850W', '80+ Gold power supply', 149.99, 40, 'PSU', 11),
    ('EVGA RTX 4070 Super', 'Mid-range gaming GPU', 599.99, 35, 'GPU', 12)
]
cur.executemany("INSERT INTO product (name, description, price, stock_quantity, category, supplier_id) VALUES (?, ?, ?, ?, ?, ?)", products)

# ----- Customers (12+ rows) -----
customers = [
    ('Kevin Nguyen', 'kevin.nguyen@email.com', '555-0101', '123 Main St, New York, NY'),
    ('Sarah Holmes', 'sarah.holmes@email.com', '555-0102', '456 Oak Ave, Los Angeles, CA'),
    ('Mikey Chen', 'mikey.chen@email.com', '555-0103', '789 Pine Rd, Chicago, IL'),
    ('Emily Vu', 'emily.vu@email.com', '555-0104', '321 Elm St, Houston, TX'),
    ('Shawn Wilson', 'shawn.wilson@email.com', '555-0105', '654 Maple Dr, Phoenix, AZ'),
    ('Lisa Pink', 'lisa.pink@email.com', '555-0106', '987 Cedar Ln, Philadelphia, PA'),
    ('Robert Taylor', 'robert.taylor@email.com', '555-0107', '147 Birch Way, San Antonio, TX'),
    ('Jennifer Lee', 'jennifer.lee@email.com', '555-0108', '258 Walnut St, San Diego, CA'),
    ('Thomas Miller', 'thomas.miller@email.com', '555-0109', '369 Spruce Ave, Dallas, TX'),
    ('Naomi Garcia', 'naomi.garcia@email.com', '555-0110', '741 Aspen Blvd, San Jose, CA'),
    ('Alex Johnson', 'alex.johnson@email.com', '555-0111', '852 Palm St, Seattle, WA'),
    ('Maria Rodriguez', 'maria.rodriguez@email.com', '555-0112', '963 Redwood Dr, Denver, CO'),
    ('David Kim', 'david.kim@email.com', '555-0113', '159 Willow Ln, Boston, MA')
]
cur.executemany("INSERT INTO customer (name, email, phone, address) VALUES (?, ?, ?, ?)", customers)

# ----- Orders (10+ rows) -----
orders = [
    (2999.97, 'completed', 1, 1),
    (799.99, 'completed', 2, 1),
    (169.99, 'pending', 3, 1),
    (1299.98, 'shipped', 4, 1),
    (199.99, 'completed', 5, 1),
    (699.99, 'processing', 6, 2),
    (589.99, 'completed', 7, 1),
    (219.99, 'shipped', 8, 2),
    (149.99, 'completed', 9, 1),
    (599.99, 'pending', 10, 1),
    (129.99, 'completed', 11, 2),
    (179.99, 'shipped', 12, 1)
]
cur.executemany("INSERT INTO orders (total_amount, status, customer_id, employee_id) VALUES (?, ?, ?, ?)", orders)

# ----- Order Items (12+ rows) -----
order_items = [
    (1, 1599.99, 1, 1),
    (1, 1399.98, 1, 2),
    (2, 799.99, 2, 4),
    (1, 169.99, 3, 6),
    (2, 649.99, 4, 10),
    (1, 199.99, 5, 11),
    (1, 699.99, 6, 10),
    (1, 589.99, 7, 4),
    (1, 219.99, 8, 11),
    (1, 149.99, 9, 13),
    (1, 599.99, 10, 14),
    (1, 129.99, 11, 6),
    (1, 179.99, 12, 7)
]
cur.executemany("INSERT INTO order_items (quantity, unit_price, order_id, product_id) VALUES (?, ?, ?, ?)", order_items)

conn.commit()
conn.close()

print("Database created successfully!")
print("Table Summary:")
print("   - 2 employees")
print("   - 12 suppliers")
print("   - 14 products")
print("   - 13 customers")
print("   - 12 orders")
print("   - 13 order items")
print(" Location: instance/pixel_haven.db")
print(" Login: username='admin', password='admin123'")