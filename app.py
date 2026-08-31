from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from functools import wraps
import os
import re
import traceback

# Import db and models from models.py
from models import db, User, Book, Wishlist, CartItem, Order, OrderItem, Review

# Create Flask app
app = Flask(__name__)

# Ensure instance folder exists
INSTANCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(INSTANCE_PATH, exist_ok=True)

# Database path
DATABASE_PATH = os.path.join(INSTANCE_PATH, 'bookstore.db')

# App configuration
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions with app
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

# -------- Helper Functions --------

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def get_cart_count():
    """Get the number of items in the current user's cart"""
    if current_user.is_authenticated:
        try:
            return CartItem.query.filter_by(user_id=current_user.id).count()
        except:
            return 0
    return 0

# -------- User Loader --------

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except:
        return None

# -------- Context Processors --------

@app.context_processor
def inject_globals():
    return {
        'cart_count': get_cart_count(),
        'current_year': datetime.now().year
    }

# -------- Routes --------

@app.route('/test')
def test_page():
    return render_template('test.html')

@app.route('/')
def index():
    """Homepage"""
    try:
        featured_books = Book.query.order_by(Book.created_at.desc()).limit(12).all()
        categories = ['Fiction', 'Classics', 'Philosophy', 'Science', 'Technology', 
                      'Self Help', 'Mystery', 'Fantasy', 'Romance']
        return render_template('index.html', books=featured_books, categories=categories)
    except Exception as e:
        print(f"Error in index: {e}")
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/debug')
def debug():
    try:
        books = Book.query.all()
        return f"Found {len(books)} books in database"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/books')
def books():
    """Catalogue page with search, filter, sort"""
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '')
        sort = request.args.get('sort', 'featured')
        page = request.args.get('page', 1, type=int)
        per_page = 12

        book_query = Book.query

        # Search
        if query:
            search_term = f'%{query}%'
            book_query = book_query.filter(
                (Book.title.ilike(search_term)) |
                (Book.author.ilike(search_term)) |
                (Book.category.ilike(search_term))
            )

        # Category filter
        if category and category != 'All':
            book_query = book_query.filter(Book.category == category)

        # Sorting
        if sort == 'price_low':
            book_query = book_query.order_by(Book.price.asc())
        elif sort == 'price_high':
            book_query = book_query.order_by(Book.price.desc())
        elif sort == 'rating':
            book_query = book_query.order_by(Book.rating.desc())
        elif sort == 'newest':
            book_query = book_query.order_by(Book.created_at.desc())
        else:  # featured
            book_query = book_query.order_by(Book.rating.desc(), Book.created_at.desc())

        # Pagination
        paginated_books = book_query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get all categories for filter
        categories = ['All'] + [c[0] for c in db.session.query(Book.category).distinct().all() if c[0]]

        return render_template('books.html', 
                             books=paginated_books,
                             categories=categories,
                             current_category=category,
                             current_sort=sort,
                             search_query=query)
    except Exception as e:
        print(f"Error in books: {e}")
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    """Book detail page"""
    try:
        book = Book.query.get_or_404(book_id)
        
        # Check if book is in wishlist
        in_wishlist = False
        if current_user.is_authenticated:
            in_wishlist = Wishlist.query.filter_by(user_id=current_user.id, book_id=book_id).first() is not None
        
        # Get reviews
        reviews = Review.query.filter_by(book_id=book_id).order_by(Review.created_at.desc()).all()
        
        # Get recommendations (same category, excluding current book)
        recommendations = Book.query.filter(
            Book.category == book.category,
            Book.id != book_id
        ).limit(4).all()
        
        return render_template('book_detail.html', 
                             book=book, 
                             in_wishlist=in_wishlist,
                             reviews=reviews,
                             recommendations=recommendations)
    except Exception as e:
        print(f"Error in book_detail: {e}")
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/cart')
@login_required
def cart():
    """Shopping cart page"""
    try:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        subtotal = sum(item.book.price * item.quantity for item in cart_items)
        shipping = 50 if subtotal < 500 else 0
        total = subtotal + shipping
        
        return render_template('cart.html', 
                             cart_items=cart_items,
                             subtotal=subtotal,
                             shipping=shipping,
                             total=total)
    except Exception as e:
        print(f"Error in cart: {e}")
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/cart/add/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    """Add book to cart"""
    try:
        book = Book.query.get_or_404(book_id)
        
        if book.stock <= 0:
            flash('This book is out of stock.', 'danger')
            return redirect(request.referrer or url_for('book_detail', book_id=book_id))
        
        cart_item = CartItem.query.filter_by(user_id=current_user.id, book_id=book_id).first()
        
        if cart_item:
            if cart_item.quantity < book.stock:
                cart_item.quantity += 1
                flash(f'Increased quantity of "{book.title}" in your cart.', 'success')
            else:
                flash('Not enough stock available.', 'danger')
        else:
            cart_item = CartItem(user_id=current_user.id, book_id=book_id, quantity=1)
            db.session.add(cart_item)
            flash(f'Added "{book.title}" to your cart.', 'success')
        
        db.session.commit()
        return redirect(request.referrer or url_for('book_detail', book_id=book_id))
    except Exception as e:
        print(f"Error in add_to_cart: {e}")
        traceback.print_exc()
        flash('An error occurred.', 'danger')
        return redirect(url_for('index'))

@app.route('/cart/update/<int:book_id>', methods=['POST'])
@login_required
def update_cart(book_id):
    """Update cart item quantity"""
    try:
        cart_item = CartItem.query.filter_by(user_id=current_user.id, book_id=book_id).first_or_404()
        quantity = request.form.get('quantity', type=int)
        
        if quantity and quantity > 0:
            if quantity <= cart_item.book.stock:
                cart_item.quantity = quantity
                db.session.commit()
                flash('Cart updated successfully.', 'success')
            else:
                flash('Not enough stock available.', 'danger')
        else:
            flash('Invalid quantity.', 'danger')
        
        return redirect(url_for('cart'))
    except Exception as e:
        print(f"Error in update_cart: {e}")
        traceback.print_exc()
        flash('An error occurred.', 'danger')
        return redirect(url_for('cart'))

@app.route('/cart/remove/<int:book_id>', methods=['POST'])
@login_required
def remove_from_cart(book_id):
    """Remove book from cart"""
    try:
        cart_item = CartItem.query.filter_by(user_id=current_user.id, book_id=book_id).first_or_404()
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart.', 'info')
        return redirect(url_for('cart'))
    except Exception as e:
        print(f"Error in remove_from_cart: {e}")
        traceback.print_exc()
        flash('An error occurred.', 'danger')
        return redirect(url_for('cart'))

@app.route('/wishlist')
@login_required
def wishlist():
    """Wishlist page"""
    try:
        wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
        books = [item.book for item in wishlist_items]
        return render_template('wishlist.html', books=books)
    except Exception as e:
        print(f"Error in wishlist: {e}")
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/wishlist/toggle/<int:book_id>', methods=['POST'])
@login_required
def toggle_wishlist(book_id):
    """Toggle book in wishlist"""
    try:
        book = Book.query.get_or_404(book_id)
        wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, book_id=book_id).first()
        
        if wishlist_item:
            db.session.delete(wishlist_item)
            db.session.commit()
            flash(f'Removed "{book.title}" from wishlist.', 'info')
            return jsonify({'wishlisted': False})
        else:
            wishlist_item = Wishlist(user_id=current_user.id, book_id=book_id)
            db.session.add(wishlist_item)
            db.session.commit()
            flash(f'Added "{book.title}" to wishlist.', 'success')
            return jsonify({'wishlisted': True})
    except Exception as e:
        print(f"Error in toggle_wishlist: {e}")
        traceback.print_exc()
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page"""
    try:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        
        if not cart_items:
            flash('Your cart is empty.', 'warning')
            return redirect(url_for('cart'))
        
        subtotal = sum(item.book.price * item.quantity for item in cart_items)
        shipping = 50 if subtotal < 500 else 0
        total = subtotal + shipping
        
        if request.method == 'POST':
            # Validate form
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()
            pincode = request.form.get('pincode', '').strip()
            payment_method = request.form.get('payment_method', '')
            
            if not all([name, email, phone, address, city, state, pincode, payment_method]):
                flash('Please fill in all fields.', 'danger')
                return render_template('checkout.html', cart_items=cart_items, subtotal=subtotal, shipping=shipping, total=total)
            
            # Validate email
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                flash('Please enter a valid email address.', 'danger')
                return render_template('checkout.html', cart_items=cart_items, subtotal=subtotal, shipping=shipping, total=total)
            
            # Check stock
            for item in cart_items:
                if item.quantity > item.book.stock:
                    flash(f'Not enough stock for "{item.book.title}". Available: {item.book.stock}', 'danger')
                    return render_template('checkout.html', cart_items=cart_items, subtotal=subtotal, shipping=shipping, total=total)
            
            # Create order
            shipping_address = f"{address}, {city}, {state} - {pincode}"
            order = Order(
                user_id=current_user.id,
                total=total,
                status='Confirmed',
                shipping_address=shipping_address,
                payment_method=payment_method
            )
            db.session.add(order)
            db.session.flush()
            
            # Create order items and reduce stock
            for cart_item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    book_id=cart_item.book_id,
                    quantity=cart_item.quantity,
                    price=cart_item.book.price
                )
                db.session.add(order_item)
                
                # Reduce stock
                cart_item.book.stock -= cart_item.quantity
            
            # Clear cart
            for cart_item in cart_items:
                db.session.delete(cart_item)
            
            db.session.commit()
            
            flash('Order placed successfully!', 'success')
            return redirect(url_for('order_success', order_id=order.id))
        
        return render_template('checkout.html', cart_items=cart_items, subtotal=subtotal, shipping=shipping, total=total)
    except Exception as e:
        print(f"Error in checkout: {e}")
        traceback.print_exc()
        flash('An error occurred during checkout.', 'danger')
        return redirect(url_for('cart'))

@app.route('/order/<int:order_id>')
@login_required
def order_success(order_id):
    """Order confirmation page"""
    try:
        order = Order.query.get_or_404(order_id)
        
        if order.user_id != current_user.id and not current_user.is_admin:
            flash('You do not have permission to view this order.', 'danger')
            return redirect(url_for('index'))
        
        return render_template('order_success.html', order=order)
    except Exception as e:
        print(f"Error in order_success: {e}")
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/orders')
@login_required
def orders():
    """Order history page"""
    try:
        user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
        return render_template('orders.html', orders=user_orders)
    except Exception as e:
        print(f"Error in orders: {e}")
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/order/detail/<int:order_id>')
@login_required
def order_detail(order_id):
    """Detailed order page"""
    try:
        order = Order.query.get_or_404(order_id)
        
        if order.user_id != current_user.id and not current_user.is_admin:
            flash('You do not have permission to view this order.', 'danger')
            return redirect(url_for('index'))
        
        return render_template('order_detail.html', order=order)
    except Exception as e:
        print(f"Error in order_detail: {e}")
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            remember = request.form.get('remember', False)
            
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user, remember=remember)
                next_page = request.args.get('next')
                flash(f'Welcome back, {user.name}!', 'success')
                return redirect(next_page or url_for('index'))
            else:
                flash('Invalid email or password.', 'danger')
        
        return render_template('login.html')
    except Exception as e:
        print(f"Error in login: {e}")
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validation
            if not all([name, email, password, confirm_password]):
                flash('Please fill in all fields.', 'danger')
                return render_template('register.html')
            
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                flash('Please enter a valid email address.', 'danger')
                return render_template('register.html')
            
            if len(password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return render_template('register.html')
            
            if password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered. Please log in.', 'warning')
                return redirect(url_for('login'))
            
            # Create user
            hashed_password = generate_password_hash(password)
            user = User(name=name, email=email, password_hash=hashed_password, is_admin=False)
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    except Exception as e:
        print(f"Error in register: {e}")
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/review/submit/<int:book_id>', methods=['POST'])
@login_required
def submit_review(book_id):
    """Submit a review for a book"""
    try:
        book = Book.query.get_or_404(book_id)
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment', '').strip()
        
        if not rating or rating < 1 or rating > 5:
            flash('Please provide a rating from 1 to 5.', 'danger')
            return redirect(url_for('book_detail', book_id=book_id))
        
        if not comment:
            flash('Please write a review comment.', 'danger')
            return redirect(url_for('book_detail', book_id=book_id))
        
        # Check for existing review
        existing_review = Review.query.filter_by(user_id=current_user.id, book_id=book_id).first()
        if existing_review:
            flash('You have already reviewed this book.', 'warning')
            return redirect(url_for('book_detail', book_id=book_id))
        
        # Create review
        review = Review(
            user_id=current_user.id,
            book_id=book_id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        
        # Update book rating
        reviews = Review.query.filter_by(book_id=book_id).all()
        avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else rating
        book.rating = round(avg_rating, 1)
        
        db.session.commit()
        flash('Review submitted successfully!', 'success')
        return redirect(url_for('book_detail', book_id=book_id))
    except Exception as e:
        print(f"Error in submit_review: {e}")
        traceback.print_exc()
        flash('An error occurred.', 'danger')
        return redirect(url_for('book_detail', book_id=book_id))

# -------- Admin Routes --------

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    try:
        total_books = Book.query.count()
        total_users = User.query.count()
        total_orders = Order.query.count()
        total_revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0
        
        return render_template('admin/dashboard.html',
                             total_books=total_books,
                             total_users=total_users,
                             total_orders=total_orders,
                             total_revenue=total_revenue)
    except Exception as e:
        print(f"Error in admin_dashboard: {e}")
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/admin/books')
@login_required
@admin_required
def admin_books():
    """Admin book management"""
    try:
        books = Book.query.order_by(Book.created_at.desc()).all()
        return render_template('admin/books.html', books=books)
    except Exception as e:
        print(f"Error in admin_books: {e}")
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/admin/books/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_book_new():
    """Create a new book"""
    try:
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            author = request.form.get('author', '').strip()
            description = request.form.get('description', '').strip()
            price = request.form.get('price', type=float)
            original_price = request.form.get('original_price', type=float)
            category = request.form.get('category', '').strip()
            isbn = request.form.get('isbn', '').strip()
            cover_image = request.form.get('cover_image', '').strip()
            stock = request.form.get('stock', type=int)
            rating = request.form.get('rating', type=float)
            
            if not all([title, author, description, price, category, stock]):
                flash('Please fill in all required fields.', 'danger')
                return render_template('admin/book_form.html', book=None)
            
            book = Book(
                title=title,
                author=author,
                description=description,
                price=price,
                original_price=original_price,
                category=category,
                isbn=isbn,
                cover_image=cover_image or '/static/images/books/placeholder.jpg',
                stock=stock,
                rating=rating or 0.0
            )
            db.session.add(book)
            db.session.commit()
            flash('Book created successfully!', 'success')
            return redirect(url_for('admin_books'))
        
        return render_template('admin/book_form.html', book=None)
    except Exception as e:
        print(f"Error in admin_book_new: {e}")
        traceback.print_exc()
        flash('An error occurred.', 'danger')
        return redirect(url_for('admin_books'))

@app.route('/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_book_edit(book_id):
    """Edit a book"""
    try:
        book = Book.query.get_or_404(book_id)
        
        if request.method == 'POST':
            book.title = request.form.get('title', '').strip()
            book.author = request.form.get('author', '').strip()
            book.description = request.form.get('description', '').strip()
            book.price = request.form.get('price', type=float)
            book.original_price = request.form.get('original_price', type=float)
            book.category = request.form.get('category', '').strip()
            book.isbn = request.form.get('isbn', '').strip()
            book.cover_image = request.form.get('cover_image', '').strip() or '/static/images/books/placeholder.jpg'
            book.stock = request.form.get('stock', type=int)
            book.rating = request.form.get('rating', type=float)
            
            if not all([book.title, book.author, book.description, book.price, book.category, book.stock]):
                flash('Please fill in all required fields.', 'danger')
                return render_template('admin/book_form.html', book=book)
            
            db.session.commit()
            flash('Book updated successfully!', 'success')
            return redirect(url_for('admin_books'))
        
        return render_template('admin/book_form.html', book=book)
    except Exception as e:
        print(f"Error in admin_book_edit: {e}")
        traceback.print_exc()
        flash('An error occurred.', 'danger')
        return redirect(url_for('admin_books'))

@app.route('/admin/books/delete/<int:book_id>', methods=['POST'])
@login_required
@admin_required
def admin_book_delete(book_id):
    """Delete a book"""
    try:
        book = Book.query.get_or_404(book_id)
        
        # Remove related records
        Wishlist.query.filter_by(book_id=book_id).delete()
        CartItem.query.filter_by(book_id=book_id).delete()
        Review.query.filter_by(book_id=book_id).delete()
        
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully.', 'info')
        return redirect(url_for('admin_books'))
    except Exception as e:
        print(f"Error in admin_book_delete: {e}")
        traceback.print_exc()
        flash('An error occurred.', 'danger')
        return redirect(url_for('admin_books'))

# -------- Error Handlers --------

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash('An internal server error occurred. Please try again later.', 'danger')
    return render_template('index.html'), 500

# -------- Create tables --------
if __name__ == '__main__':
    with app.app_context():
        print("📦 Creating database tables...")
        db.create_all()
        print(f"✅ Database created at: {DATABASE_PATH}")
    app.run(debug=True)