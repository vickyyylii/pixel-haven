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
    return render_template('dashboard.html')

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
        create_default_supplier()
    app.run(debug=True)