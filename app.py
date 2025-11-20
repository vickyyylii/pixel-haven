from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'pixel-haven-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pixel_haven.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class Employee(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50))
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    
    supplier = db.relationship('Supplier', backref=db.backref('products', lazy=True))

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, server_default=db.func.now())
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))
    employee = db.relationship('Employee', backref=db.backref('orders', lazy=True))
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    product = db.relationship('Product', backref=db.backref('order_items', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(int(user_id))

# Analytics Functions

def get_dashboard_stats():
    """Get statistics for dashboard"""
    total_products = Product.query.count()
    total_customers = Customer.query.count()
    total_orders = Order.query.count()
    low_stock_products = Product.query.filter(Product.stock_quantity < 10).count()
    
    return {
        'total_products': total_products,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'low_stock_products': low_stock_products
    }

def get_category_stats():
    """Get product counts by category"""
    categories = db.session.query(
        Product.category, 
        db.func.count(Product.id).label('count')
    ).group_by(Product.category).all()
    
    return {category: count for category, count in categories if category}

def get_price_range_stats():
    """Get product counts by price range"""
    ranges = [
        ('Under $50', Product.query.filter(Product.price < 50).count()),
        ('$50-$100', Product.query.filter(Product.price.between(50, 100)).count()),
        ('$100-$200', Product.query.filter(Product.price.between(100, 200)).count()),
        ('Over $200', Product.query.filter(Product.price > 200).count())
    ]
    return ranges

# Helper functions
def create_admin_user():
    print("🔧 Checking for admin user...")
    if not Employee.query.filter_by(username='admin').first():
        admin = Employee(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created: admin / admin123")
    else:
        print("✅ Admin user already exists")

def create_default_supplier():
    print("🔧 Checking for default supplier...")
    if not Supplier.query.first():
        supplier = Supplier(
            name="Default Supplier",
            contact_email="supplier@example.com",
            phone="123-456-7890",
            address="123 Main Street, City, State"
        )
        db.session.add(supplier)
        db.session.commit()
        print("✅ Default supplier created.")
    else:
        print("✅ Default supplier already exists")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    stats = get_dashboard_stats()
    category_stats = get_category_stats()
    price_stats = get_price_range_stats()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         category_stats=category_stats,
                         price_stats=price_stats)

@app.route('/test')
def test():
    return "<h1>Simple Test</h1><p>If you see this, basic routing works!</p>"

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("🔐 LOGIN ROUTE ACCESSED")
    
    if request.method == 'POST':
        print("📝 POST request received")
        username = request.form['username']
        password = request.form['password']
        
        employee = Employee.query.filter_by(username=username).first()
        
        if employee and check_password_hash(employee.password_hash, password):
            login_user(employee)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    print("🎨 Rendering login template...")
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Product Management Routes 
@app.route('/products')
@login_required
def products():
    all_products = Product.query.all()
    return render_template('products/list.html', products=all_products)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    suppliers = Supplier.query.all()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        stock_quantity = int(request.form['stock_quantity'])
        category = request.form['category']
        supplier_id = int(request.form['supplier_id'])
        
        new_product = Product(
            name=name,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            category=category,
            supplier_id=supplier_id
        )
        
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))
    
    return render_template('products/add.html', suppliers=suppliers)

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    suppliers = Supplier.query.all()
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.stock_quantity = int(request.form['stock_quantity'])
        product.category = request.form['category']
        product.supplier_id = int(request.form['supplier_id'])
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products'))
    
    return render_template('products/edit.html', product=product, suppliers=suppliers)

@app.route('/products/delete/<int:id>')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products'))

# Customer Management Routes
@app.route('/customers')
@login_required
def customers():
    all_customers = Customer.query.all()
    return render_template('customers/list.html', customers=all_customers)

@app.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        new_customer = Customer(
            name=name,
            email=email,
            phone=phone,
            address=address
        )
        
        try:
            db.session.add(new_customer)
            db.session.commit()
            flash('Customer added successfully!', 'success')
            return redirect(url_for('customers'))
        except:
            db.session.rollback()
            flash('Error: Email already exists!', 'error')
    
    return render_template('customers/add.html')

@app.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.email = request.form['email']
        customer.phone = request.form['phone']
        customer.address = request.form['address']
        
        try:
            db.session.commit()
            flash('Customer updated successfully!', 'success')
            return redirect(url_for('customers'))
        except:
            db.session.rollback()
            flash('Error: Email already exists!', 'error')
    
    return render_template('customers/edit.html', customer=customer)

@app.route('/customers/delete/<int:id>')
@login_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted successfully!', 'success')
    return redirect(url_for('customers'))

@app.route('/debug')
def debug_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'path': rule.rule,
            'methods': list(rule.methods)
        })
    return {'routes': sorted(routes, key=lambda x: x['endpoint'])}

def import_original_data():
    """Import data from your original setup_database.py - COMMIT 8"""
    print("🔄 Importing original Pixel Haven dataset...")
    
    # Clear existing data but KEEP employees (admin user)
    print("🗑️ Clearing existing data (keeping employees)...")
    OrderItem.query.delete()
    Order.query.delete()
    Customer.query.delete()
    Product.query.delete()
    Supplier.query.delete()
    
    suppliers_data = [
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
    
    # Add real suppliers
    suppliers = []
    for name, email, phone, address in suppliers_data:
        supplier = Supplier(name=name, contact_email=email, phone=phone, address=address)
        db.session.add(supplier)
        suppliers.append(supplier)
    
    db.session.flush()  # Get supplier IDs
    
    # Products
    products_data = [
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
    
    for name, description, price, stock, category, supplier_id in products_data:
        product = Product(
            name=name, description=description, price=price,
            stock_quantity=stock, category=category, supplier_id=supplier_id
        )
        db.session.add(product)
    
    customers_data = [
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
    
    for name, email, phone, address in customers_data:
        customer = Customer(name=name, email=email, phone=phone, address=address)
        db.session.add(customer)
    
    # Complete orders data 
    orders_data = [
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
    
    for total_amount, status, customer_id, employee_id in orders_data:
        order = Order(total_amount=total_amount, status=status, customer_id=customer_id, employee_id=employee_id)
        db.session.add(order)
    
    db.session.flush()  
    
    # Complete order items data 
    order_items_data = [
        (1, 1599.99, 1, 1),    # Order 1: NVIDIA RTX 4090
        (1, 1399.98, 1, 2),    # Order 1: NVIDIA RTX 4080
        (1, 799.99, 2, 4),     # Order 2: Intel Core i9-14900K
        (1, 169.99, 3, 8),     # Order 3: WD Black SN850X 2TB
        (2, 649.99, 4, 10),    # Order 4: 2x ASUS ROG Swift Monitor
        (1, 199.99, 5, 11),    # Order 5: MSI MAG B650 Tomahawk
        (1, 699.99, 6, 10),    # Order 6: ASUS ROG Swift Monitor
        (1, 589.99, 7, 4),     # Order 7: Intel Core i9-14900K
        (1, 219.99, 8, 11),    # Order 8: MSI MAG B650 Tomahawk
        (1, 149.99, 9, 13),    # Order 9: Gigabyte AORUS PSU 850W
        (1, 599.99, 10, 14),   # Order 10: EVGA RTX 4070 Super
        (1, 129.99, 11, 6),    # Order 11: Corsair Vengeance 32GB DDR5
        (1, 179.99, 12, 7)     # Order 12: Samsung 980 Pro 2TB
    ]
    
    for quantity, unit_price, order_id, product_id in order_items_data:
        order_item = OrderItem(
            quantity=quantity,
            unit_price=unit_price,
            order_id=order_id,
            product_id=product_id
        )
        db.session.add(order_item)
    
    db.session.commit()
    print("✅ Pixel Haven dataset imported successfully!")
    print("📊 Data Summary:")
    print(f"   - {Supplier.query.count()} suppliers")
    print(f"   - {Product.query.count()} products") 
    print(f"   - {Customer.query.count()} customers")
    print(f"   - {Order.query.count()} orders")
    print(f"   - {OrderItem.query.count()} order items")

# Order Management Routes
@app.route('/orders')
@login_required
def orders():
    all_orders = Order.query.all()
    return render_template('orders/list.html', orders=all_orders)

@app.route('/orders/create', methods=['GET', 'POST'])
@login_required
def create_order():
    customers = Customer.query.all()
    products = Product.query.all()
    
    if request.method == 'POST':
        customer_id = int(request.form['customer_id'])
        product_ids = request.form.getlist('product_ids')
        quantities = request.form.getlist('quantities')
        
        # Calculate total amount
        total_amount = 0
        order_items = []
        
        for i, product_id in enumerate(product_ids):
            product = Product.query.get(int(product_id))
            quantity = int(quantities[i])
            
            if product and quantity > 0:
                # Check stock availability
                if product.stock_quantity >= quantity:
                    subtotal = product.price * quantity
                    total_amount += subtotal
                    
                    # Create order item
                    order_item = OrderItem(
                        quantity=quantity,
                        unit_price=product.price,
                        product_id=product.id
                    )
                    order_items.append(order_item)
                    
                    # Update product stock
                    product.stock_quantity -= quantity
                else:
                    flash(f'Insufficient stock for {product.name}', 'error')
                    return redirect(url_for('create_order'))
        
        if order_items:
            # Create order
            new_order = Order(
                total_amount=total_amount,
                customer_id=customer_id,
                employee_id=current_user.id
            )
            
            db.session.add(new_order)
            db.session.flush()  # Get the order ID
            
            # Add order items
            for order_item in order_items:
                order_item.order_id = new_order.id
                db.session.add(order_item)
            
            db.session.commit()
            flash('Order created successfully!', 'success')
            return redirect(url_for('orders'))
        else:
            flash('No valid products selected for order', 'error')
    
    return render_template('orders/create.html', customers=customers, products=products)

@app.route('/orders/<int:id>')
@login_required
def order_details(id):
    order = Order.query.get_or_404(id)
    return render_template('orders/details.html', order=order)

@app.route('/orders/update_status/<int:id>', methods=['POST'])
@login_required
def update_order_status(id):
    order = Order.query.get_or_404(id)
    new_status = request.form['status']
    order.status = new_status
    db.session.commit()
    flash(f'Order status updated to {new_status}', 'success')
    return redirect(url_for('order_details', id=id))

@app.route('/orders/delete/<int:id>')
@login_required
def delete_order(id):
    order = Order.query.get_or_404(id)
    
    # Restore product stock
    for item in order.items:
        product = Product.query.get(item.product_id)
        if product:
            product.stock_quantity += item.quantity
    
    db.session.delete(order)
    db.session.commit()
    flash('Order deleted successfully!', 'success')
    return redirect(url_for('orders'))

# Supplier Management Routes
@app.route('/suppliers')
@login_required
def suppliers():
    all_suppliers = Supplier.query.all()
    return render_template('suppliers/list.html', suppliers=all_suppliers)

@app.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        name = request.form['name']
        contact_email = request.form['contact_email']
        phone = request.form['phone']
        address = request.form['address']
        
        new_supplier = Supplier(
            name=name,
            contact_email=contact_email,
            phone=phone,
            address=address
        )
        
        db.session.add(new_supplier)
        db.session.commit()
        flash('Supplier added successfully!', 'success')
        return redirect(url_for('suppliers'))
    
    return render_template('suppliers/add.html')

@app.route('/suppliers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    
    if request.method == 'POST':
        supplier.name = request.form['name']
        supplier.contact_email = request.form['contact_email']
        supplier.phone = request.form['phone']
        supplier.address = request.form['address']
        
        db.session.commit()
        flash('Supplier updated successfully!', 'success')
        return redirect(url_for('suppliers'))
    
    return render_template('suppliers/edit.html', supplier=supplier)

@app.route('/suppliers/delete/<int:id>')
@login_required
def delete_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    
    # Check if supplier has products
    if supplier.products:
        flash('Cannot delete supplier with associated products. Please reassign products first.', 'error')
        return redirect(url_for('suppliers'))
    
    db.session.delete(supplier)
    db.session.commit()
    flash('Supplier deleted successfully!', 'success')
    return redirect(url_for('suppliers'))

@app.route('/suppliers/<int:id>')
@login_required
def supplier_details(id):
    supplier = Supplier.query.get_or_404(id)
    return render_template('suppliers/details.html', supplier=supplier)

# Search & Filter Routes - COMMIT 9
@app.route('/search/products')
@login_required
def search_products():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    
    # Start with base query
    products_query = Product.query
    
    # Apply search filters
    if query:
        products_query = products_query.filter(Product.name.ilike(f'%{query}%'))
    
    if category:
        products_query = products_query.filter(Product.category == category)
    
    if min_price:
        products_query = products_query.filter(Product.price >= float(min_price))
    
    if max_price:
        products_query = products_query.filter(Product.price <= float(max_price))
    
    products = products_query.all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('search/products.html', 
                         products=products, 
                         categories=categories,
                         search_query=query,
                         selected_category=category,
                         min_price=min_price,
                         max_price=max_price)

@app.route('/search/customers')
@login_required
def search_customers():
    query = request.args.get('q', '')
    
    customers_query = Customer.query
    
    if query:
        customers_query = customers_query.filter(
            Customer.name.ilike(f'%{query}%') | 
            Customer.email.ilike(f'%{query}%')
        )
    
    customers = customers_query.all()
    
    return render_template('search/customers.html', 
                         customers=customers, 
                         search_query=query)

@app.route('/search/orders')
@login_required
def search_orders():
    status = request.args.get('status', '')
    customer_id = request.args.get('customer_id', '')
    
    orders_query = Order.query
    
    if status:
        orders_query = orders_query.filter(Order.status == status)
    
    if customer_id:
        orders_query = orders_query.filter(Order.customer_id == int(customer_id))
    
    orders = orders_query.all()
    customers = Customer.query.all()
    statuses = ['pending', 'processing', 'shipped', 'completed']
    
    return render_template('search/orders.html', 
                         orders=orders, 
                         customers=customers,
                         statuses=statuses,
                         selected_status=status,
                         selected_customer_id=customer_id)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
        create_default_supplier()
        import_original_data() 
    app.run(debug=True)