from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from extensions import db, login_manager
from models import User, Product, Order, Cart, Category
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        
        # Create categories
        categories_data = [
            'Electronics', 'Fashion', 'Home & Kitchen', 
            'Groceries', 'Sports', 'Home Decor'
        ]
        
        categories = {}
        for cat_name in categories_data:
            category = Category(name=cat_name)
            db.session.add(category)
            db.session.flush()  # Get the ID
            categories[cat_name] = category.id
        
        # Create sample products
        sample_products = [
            {'name': 'Samsung Galaxy M34', 'price': 18999.00, 'description': '5G Smartphone with 6000mAh battery', 'category_id': categories['Electronics'], 'stock': 25},
            {'name': 'Mi Smart Band 6', 'price': 2499.00, 'description': 'AMOLED Display Fitness Band', 'category_id': categories['Electronics'], 'stock': 30},
            {'name': 'Boat Airdopes 141', 'price': 1299.00, 'description': 'Wireless Earbuds with 42H Playback', 'category_id': categories['Electronics'], 'stock': 40},
            {'name': 'Cotton Kurti', 'price': 899.00, 'description': 'Handblock Printed Cotton Kurti', 'category_id': categories['Fashion'], 'stock': 15},
            {'name': 'Men\'s Formal Shirt', 'price': 1599.00, 'description': 'Slim Fit Cotton Formal Shirt', 'category_id': categories['Fashion'], 'stock': 20},
            {'name': 'Kitchen Set', 'price': 2999.00, 'description': '7 Pcs Non-Stick Cookware Set', 'category_id': categories['Home & Kitchen'], 'stock': 10},
            {'name': 'Silk Saree', 'price': 4599.00, 'description': 'Banarasi Silk Saree with Blouse', 'category_id': categories['Fashion'], 'stock': 8},
            {'name': 'Pressure Cooker', 'price': 1899.00, 'description': 'Stainless Steel Pressure Cooker 5L', 'category_id': categories['Home & Kitchen'], 'stock': 12},
            {'name': 'Indian Spices Kit', 'price': 699.00, 'description': 'Assorted Indian Masalas Pack', 'category_id': categories['Groceries'], 'stock': 50},
            {'name': 'Yoga Mat', 'price': 799.00, 'description': 'Anti-Skip Exercise Yoga Mat', 'category_id': categories['Sports'], 'stock': 25},
            {'name': 'Tea Gift Set', 'price': 599.00, 'description': 'Assam & Darjeeling Tea Pack', 'category_id': categories['Groceries'], 'stock': 35},
            {'name': 'Brass Diya Set', 'price': 499.00, 'description': 'Handcrafted Brass Diya for Pooja', 'category_id': categories['Home Decor'], 'stock': 20}
        ]
        
        for product_data in sample_products:
            product = Product(**product_data)
            db.session.add(product)
        
        # Create a sample user for testing
        sample_user = User(
            username='demo',
            email='demo@example.com',
            password=generate_password_hash('password123')
        )
        db.session.add(sample_user)
        
        db.session.commit()
        print("Database initialized successfully!")

@app.route('/')
def index():
    products = Product.query.all()
    categories = Category.query.all()
    
    cart_count = 0
    if current_user.is_authenticated:
        cart_count = Cart.query.filter_by(user_id=current_user.id).count()
    
    return render_template('index.html', 
                         products=products, 
                         categories=categories, 
                         cart_count=cart_count)

@app.route('/category/<int:category_id>')
def category_products(category_id):
    products = Product.query.filter_by(category_id=category_id).all()
    categories = Category.query.all()
    selected_category = Category.query.get(category_id)
    
    cart_count = 0
    if current_user.is_authenticated:
        cart_count = Cart.query.filter_by(user_id=current_user.id).count()
    
    return render_template('index.html', 
                         products=products, 
                         categories=categories, 
                         selected_category=selected_category, 
                         cart_count=cart_count)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    else:
        products = Product.query.all()
    
    categories = Category.query.all()
    
    cart_count = 0
    if current_user.is_authenticated:
        cart_count = Cart.query.filter_by(user_id=current_user.id).count()
    
    return render_template('index.html', 
                         products=products, 
                         categories=categories, 
                         search_query=query, 
                         cart_count=cart_count)

@app.route('/about')
def about():
    cart_count = 0
    if current_user.is_authenticated:
        cart_count = Cart.query.filter_by(user_id=current_user.id).count()
    return render_template('about.html', cart_count=cart_count)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        flash(f'Thank you {name} for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    cart_count = 0
    if current_user.is_authenticated:
        cart_count = Cart.query.filter_by(user_id=current_user.id).count()
    return render_template('contact.html', cart_count=cart_count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
    cart_count = Cart.query.filter_by(user_id=current_user.id).count()
    return render_template('dashboard.html', 
                         user=current_user, 
                         orders=user_orders, 
                         cart_count=cart_count)

@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Check if product already in cart
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += 1
        flash(f'Increased quantity of {product.name} in cart!', 'success')
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(cart_item)
        flash(f'{product.name} added to cart!', 'success')
    
    db.session.commit()
    return redirect(request.referrer or url_for('index'))

@app.route('/update_cart/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    if cart_item.user_id != current_user.id:
        flash('Unauthorized action', 'error')
        return redirect(url_for('cart'))
    
    quantity = int(request.form.get('quantity', 1))
    if quantity <= 0:
        db.session.delete(cart_item)
        flash('Item removed from cart', 'success')
    else:
        cart_item.quantity = quantity
        flash('Cart updated successfully!', 'success')
    
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    if cart_item.user_id == current_user.id:
        product_name = cart_item.product.name
        db.session.delete(cart_item)
        db.session.commit()
        flash(f'{product_name} removed from cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    cart_count = len(cart_items)
    
    return render_template('cart.html', 
                         cart_items=cart_items, 
                         total_amount=total_amount, 
                         cart_count=cart_count)

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty!', 'error')
        return redirect(url_for('cart'))
    
    if request.method == 'POST':
        # Create orders from cart items
        for cart_item in cart_items:
            order = Order(
                user_id=current_user.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                total_price=cart_item.product.price * cart_item.quantity,
                status='confirmed',
                shipping_address=request.form.get('address'),
                payment_method=request.form.get('payment_method')
            )
            db.session.add(order)
        
        # Clear cart
        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        flash('Order placed successfully! Thank you for shopping with us.', 'success')
        return redirect(url_for('orders'))
    
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    cart_count = len(cart_items)
    
    return render_template('checkout.html', 
                         cart_items=cart_items, 
                         total_amount=total_amount, 
                         cart_count=cart_count)

@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    cart_count = Cart.query.filter_by(user_id=current_user.id).count()
    return render_template('orders.html', 
                         orders=user_orders, 
                         cart_count=cart_count)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

# API endpoint to get cart count
@app.route('/api/cart_count')
@login_required
def api_cart_count():
    count = Cart.query.filter_by(user_id=current_user.id).count()
    return jsonify({'count': count})

if __name__ == '__main__':
    # Check if database needs initialization
    if not os.path.exists('database.db'):
        init_database()
    
    with app.app_context():
        # Ensure all tables are created
        db.create_all()
    
    app.run(debug=True)