#!/usr/bin/env python
"""Seed script for Book Ninja database"""
import sys
import os
import random
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure instance folder exists
INSTANCE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance')
os.makedirs(INSTANCE_PATH, exist_ok=True)

# Import from app
from app import app
from models import db, User, Book, Wishlist, CartItem, Order, OrderItem, Review
from werkzeug.security import generate_password_hash

# Book data
BOOKS = [
    {
        'title': 'The Great Gatsby',
        'author': 'F. Scott Fitzgerald',
        'description': 'The story of the mysteriously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan, set against the backdrop of the Roaring Twenties.',
        'price': 299.00,
        'original_price': 499.00,
        'category': 'Classics',
        'isbn': '9780743273565',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780743273565-L.jpg',
        'rating': 4.5,
        'stock': 50
    },
    {
        'title': 'To Kill a Mockingbird',
        'author': 'Harper Lee',
        'description': 'The story of a young girl growing up in the American South during the 1930s, and her father\'s fight for justice in a racially divided town.',
        'price': 349.00,
        'original_price': 599.00,
        'category': 'Classics',
        'isbn': '9780061120084',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780061120084-L.jpg',
        'rating': 4.8,
        'stock': 45
    },
    {
        'title': '1984',
        'author': 'George Orwell',
        'description': 'A dystopian novel set in a totalitarian society ruled by Big Brother, exploring themes of surveillance, truth, and individual freedom.',
        'price': 279.00,
        'original_price': 499.00,
        'category': 'Classics',
        'isbn': '9780451524935',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780451524935-L.jpg',
        'rating': 4.7,
        'stock': 60
    },
    {
        'title': 'Pride and Prejudice',
        'author': 'Jane Austen',
        'description': 'The story of Elizabeth Bennet and her tumultuous relationship with the wealthy Mr. Darcy, set in Regency-era England.',
        'price': 249.00,
        'original_price': 449.00,
        'category': 'Classics',
        'isbn': '9780141439518',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780141439518-L.jpg',
        'rating': 4.6,
        'stock': 40
    },
    {
        'title': 'The Alchemist',
        'author': 'Paulo Coelho',
        'description': 'A philosophical novel about a young shepherd who follows his dream to find treasure in Egypt, learning about life and destiny along the way.',
        'price': 329.00,
        'original_price': 549.00,
        'category': 'Fiction',
        'isbn': '9780062502174',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780062502174-L.jpg',
        'rating': 4.3,
        'stock': 35
    },
    {
        'title': 'The Catcher in the Rye',
        'author': 'J.D. Salinger',
        'description': 'The story of Holden Caulfield, a teenage rebel navigating the complexities of adolescence and society in 1950s America.',
        'price': 259.00,
        'original_price': 459.00,
        'category': 'Classics',
        'isbn': '9780316769488',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780316769488-L.jpg',
        'rating': 4.1,
        'stock': 30
    },
    {
        'title': 'The Little Prince',
        'author': 'Antoine de Saint-Exupéry',
        'description': 'A timeless tale about a young prince who travels through the universe, learning about love, friendship, and what truly matters in life.',
        'price': 199.00,
        'original_price': 349.00,
        'category': 'Fiction',
        'isbn': '9780156012195',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780156012195-L.jpg',
        'rating': 4.9,
        'stock': 55
    },
    {
        'title': 'The Name of the Rose',
        'author': 'Umberto Eco',
        'description': 'A historical mystery set in a 14th-century Italian monastery, featuring Franciscan friar William of Baskerville as he investigates a series of murders.',
        'price': 399.00,
        'original_price': 699.00,
        'category': 'Mystery',
        'isbn': '9780156001311',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780156001311-L.jpg',
        'rating': 4.4,
        'stock': 25
    },
    {
        'title': 'The Hobbit',
        'author': 'J.R.R. Tolkien',
        'description': 'The story of Bilbo Baggins, a hobbit who embarks on a quest to reclaim the Lonely Mountain from the dragon Smaug.',
        'price': 349.00,
        'original_price': 599.00,
        'category': 'Fantasy',
        'isbn': '9780547928227',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780547928227-L.jpg',
        'rating': 4.8,
        'stock': 48
    },
    {
        'title': 'The Lord of the Rings',
        'author': 'J.R.R. Tolkien',
        'description': 'An epic fantasy novel about the quest to destroy the One Ring and defeat the Dark Lord Sauron.',
        'price': 699.00,
        'original_price': 999.00,
        'category': 'Fantasy',
        'isbn': '9780544003484',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780544003484-L.jpg',
        'rating': 4.9,
        'stock': 30
    },
    {
        'title': 'Dune',
        'author': 'Frank Herbert',
        'description': 'A science fiction novel set in a distant future, featuring the desert planet Arrakis and the struggle for control of its valuable spice.',
        'price': 459.00,
        'original_price': 699.00,
        'category': 'Science',
        'isbn': '9780441172719',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780441172719-L.jpg',
        'rating': 4.7,
        'stock': 32
    },
    {
        'title': 'Brave New World',
        'author': 'Aldous Huxley',
        'description': 'A dystopian novel exploring a future society where technology and conditioning have created a shallow, consumerist world.',
        'price': 289.00,
        'original_price': 499.00,
        'category': 'Classics',
        'isbn': '9780060850524',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780060850524-L.jpg',
        'rating': 4.3,
        'stock': 38
    },
    {
        'title': 'The Art of War',
        'author': 'Sun Tzu',
        'description': 'An ancient Chinese military treatise that offers timeless wisdom on strategy, leadership, and conflict resolution.',
        'price': 219.00,
        'original_price': 399.00,
        'category': 'Philosophy',
        'isbn': '9781590302259',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9781590302259-L.jpg',
        'rating': 4.2,
        'stock': 45
    },
    {
        'title': 'Meditations',
        'author': 'Marcus Aurelius',
        'description': 'A series of personal writings by the Roman Emperor, offering a glimpse into the mind of a Stoic philosopher.',
        'price': 239.00,
        'original_price': 449.00,
        'category': 'Philosophy',
        'isbn': '9780140449334',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780140449334-L.jpg',
        'rating': 4.6,
        'stock': 40
    },
    {
        'title': 'The Psychology of Money',
        'author': 'Morgan Housel',
        'description': 'An exploration of how our personal experiences and beliefs shape our financial decisions, featuring timeless lessons on wealth.',
        'price': 379.00,
        'original_price': 599.00,
        'category': 'Psychology',
        'isbn': '9780857199090',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780857199090-L.jpg',
        'rating': 4.5,
        'stock': 28
    },
    {
        'title': 'Thinking, Fast and Slow',
        'author': 'Daniel Kahneman',
        'description': 'A groundbreaking exploration of how our minds work, examining the two systems of thought that drive our decisions.',
        'price': 459.00,
        'original_price': 699.00,
        'category': 'Psychology',
        'isbn': '9780374533557',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780374533557-L.jpg',
        'rating': 4.7,
        'stock': 25
    },
    {
        'title': 'The 7 Habits of Highly Effective People',
        'author': 'Stephen R. Covey',
        'description': 'A classic self-help book that presents a principle-centered approach to personal and professional effectiveness.',
        'price': 399.00,
        'original_price': 649.00,
        'category': 'Self Help',
        'isbn': '9780743269513',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780743269513-L.jpg',
        'rating': 4.4,
        'stock': 35
    },
    {
        'title': 'Atomic Habits',
        'author': 'James Clear',
        'description': 'A practical guide to building good habits and breaking bad ones, focusing on small changes that lead to remarkable results.',
        'price': 399.00,
        'original_price': 599.00,
        'category': 'Self Help',
        'isbn': '9781847941831',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9781847941831-L.jpg',
        'rating': 4.8,
        'stock': 42
    },
    {
        'title': 'The Clean Coder',
        'author': 'Robert C. Martin',
        'description': 'A guide to the professional practices, responsibilities, and ethics of software developers, featuring practical advice from a veteran.',
        'price': 349.00,
        'original_price': 549.00,
        'category': 'Technology',
        'isbn': '9780137081073',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780137081073-L.jpg',
        'rating': 4.3,
        'stock': 20
    },
    {
        'title': 'The Pragmatic Programmer',
        'author': 'David Thomas and Andrew Hunt',
        'description': 'A collection of tips and insights for software developers, covering everything from coding practices to career development.',
        'price': 389.00,
        'original_price': 599.00,
        'category': 'Technology',
        'isbn': '9780201616224',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780201616224-L.jpg',
        'rating': 4.6,
        'stock': 22
    },
    {
        'title': 'Code Complete',
        'author': 'Steve McConnell',
        'description': 'A comprehensive guide to software construction, covering everything from coding techniques to project management.',
        'price': 499.00,
        'original_price': 799.00,
        'category': 'Technology',
        'isbn': '9780735619678',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780735619678-L.jpg',
        'rating': 4.5,
        'stock': 18
    },
    {
        'title': 'A Brief History of Time',
        'author': 'Stephen Hawking',
        'description': 'An exploration of the universe\'s origins, structure, and ultimate fate, written for the general reader.',
        'price': 329.00,
        'original_price': 549.00,
        'category': 'Science',
        'isbn': '9780553380163',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780553380163-L.jpg',
        'rating': 4.7,
        'stock': 30
    },
    {
        'title': 'The Selfish Gene',
        'author': 'Richard Dawkins',
        'description': 'A groundbreaking work on evolutionary biology, proposing that genes are the primary units of selection in evolution.',
        'price': 299.00,
        'original_price': 499.00,
        'category': 'Science',
        'isbn': '9780199291151',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780199291151-L.jpg',
        'rating': 4.4,
        'stock': 28
    },
    {
        'title': 'The Doors of Perception',
        'author': 'Aldous Huxley',
        'description': 'A personal account of Huxley\'s experience with mescaline, exploring the nature of consciousness and perception.',
        'price': 199.00,
        'original_price': 349.00,
        'category': 'Philosophy',
        'isbn': '9780060850524',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780060850524-L.jpg',
        'rating': 4.0,
        'stock': 25
    },
    {
        'title': 'The Gene: An Intimate History',
        'author': 'Siddhartha Mukherjee',
        'description': 'A comprehensive exploration of the history and science of genetics, from Mendel to the modern era.',
        'price': 459.00,
        'original_price': 699.00,
        'category': 'Science',
        'isbn': '9781476733500',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9781476733500-L.jpg',
        'rating': 4.5,
        'stock': 20
    },
    {
        'title': 'The Art of Happiness',
        'author': 'Dalai Lama and Howard Cutler',
        'description': 'A dialogue between the Dalai Lama and a psychiatrist, offering a guide to living a happier life.',
        'price': 349.00,
        'original_price': 549.00,
        'category': 'Self Help',
        'isbn': '9781573221115',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9781573221115-L.jpg',
        'rating': 4.3,
        'stock': 30
    },
    {
        'title': 'The Four Agreements',
        'author': 'Don Miguel Ruiz',
        'description': 'A guide to personal freedom, based on ancient Toltec wisdom, offering four principles for living a better life.',
        'price': 289.00,
        'original_price': 459.00,
        'category': 'Self Help',
        'isbn': '9781878424310',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9781878424310-L.jpg',
        'rating': 4.6,
        'stock': 35
    },
    {
        'title': 'The Elements of Style',
        'author': 'William Strunk Jr. and E.B. White',
        'description': 'A classic guide to English writing style, offering practical advice on grammar, composition, and clarity.',
        'price': 199.00,
        'original_price': 349.00,
        'category': 'Fiction',
        'isbn': '9780205309023',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780205309023-L.jpg',
        'rating': 4.2,
        'stock': 40
    },
    {
        'title': 'The War of Art',
        'author': 'Steven Pressfield',
        'description': 'A guide to overcoming creative blocks and resistance, offering a practical approach to pursuing your creative work.',
        'price': 279.00,
        'original_price': 449.00,
        'category': 'Self Help',
        'isbn': '9780446581455',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780446581455-L.jpg',
        'rating': 4.4,
        'stock': 30
    },
    {
        'title': 'The Design of Everyday Things',
        'author': 'Don Norman',
        'description': 'An exploration of design principles and their application to everyday objects, focusing on user-centered design.',
        'price': 399.00,
        'original_price': 599.00,
        'category': 'Technology',
        'isbn': '9780465050659',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9780465050659-L.jpg',
        'rating': 4.6,
        'stock': 25
    },
    {
        'title': 'The Power of Habit',
        'author': 'Charles Duhigg',
        'description': 'An exploration of how habits work and how they can be changed, featuring case studies and practical insights.',
        'price': 349.00,
        'original_price': 549.00,
        'category': 'Psychology',
        'isbn': '9781400069286',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9781400069286-L.jpg',
        'rating': 4.5,
        'stock': 32
    },
    {
        'title': 'The Sixth Extinction',
        'author': 'Elizabeth Kolbert',
        'description': 'An exploration of the ongoing mass extinction of species, caused by human activities, and its implications for the future.',
        'price': 379.00,
        'original_price': 599.00,
        'category': 'Science',
        'isbn': '9781250062185',
        'cover_image': 'https://covers.openlibrary.org/b/isbn/9781250062185-L.jpg',
        'rating': 4.3,
        'stock': 22
    }
]

def seed_database():
    """Seed the database with initial data"""
    print("🌱 Seeding database...")
    
    with app.app_context():
        # Create all tables if they don't exist
        print("📦 Ensuring database tables exist...")
        db.create_all()
        print("✅ Tables ready.")
        
        # Check if data already exists
        existing_books = Book.query.count()
        if existing_books > 0:
            print(f"⚠️ Database already has {existing_books} books. Skipping seed.")
            print("   To re-seed, delete the database file first.")
            return
        
        # Create admin user
        print("👤 Creating admin user...")
        admin = User(
            name='Admin',
            email='admin@bookninja.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        
        # Create regular users
        users = [
            User(
                name='John Doe',
                email='john@example.com',
                password_hash=generate_password_hash('password123'),
                is_admin=False
            ),
            User(
                name='Jane Smith',
                email='jane@example.com',
                password_hash=generate_password_hash('password123'),
                is_admin=False
            ),
            User(
                name='Bob Wilson',
                email='bob@example.com',
                password_hash=generate_password_hash('password123'),
                is_admin=False
            ),
            User(
                name='Alice Johnson',
                email='alice@example.com',
                password_hash=generate_password_hash('password123'),
                is_admin=False
            )
        ]
        for user in users:
            db.session.add(user)
        
        db.session.flush()
        print(f"👤 Created {len(users) + 1} users")
        
        # Create books
        print("📚 Creating books...")
        for book_data in BOOKS:
            book = Book(**book_data)
            db.session.add(book)
        
        db.session.flush()
        print(f"📚 Created {len(BOOKS)} books")
        
        # Get all books and users for relationships
        all_books = Book.query.all()
        all_users = User.query.filter_by(is_admin=False).all()
        
        # Create reviews
        review_comments = [
            "Absolutely loved this book! Couldn't put it down.",
            "A must-read for everyone. Highly recommended.",
            "Beautifully written and thought-provoking.",
            "Great story, but a bit slow in the middle.",
            "A classic that everyone should read at least once.",
            "Incredible depth and meaning. A masterpiece.",
            "Loved the characters and the plot. 5 stars!",
            "Good read, but I preferred the author's other works.",
            "A fresh perspective on a timeless topic.",
            "Stunning prose and vivid imagery. A gem.",
            "I couldn't stop thinking about this book.",
            "Not my usual genre, but I was thoroughly impressed.",
            "A bit predictable, but still enjoyable.",
            "Absolutely fantastic! Will read again.",
            "Great insight into the human condition."
        ]
        
        print("📝 Creating reviews...")
        review_count = 0
        for book in all_books[:20]:
            num_reviews = random.randint(3, 8)
            if all_users:
                selected_users = random.sample(all_users, min(num_reviews, len(all_users)))
                for user in selected_users:
                    review = Review(
                        user_id=user.id,
                        book_id=book.id,
                        rating=random.randint(3, 5),
                        comment=random.choice(review_comments),
                        created_at=datetime.now() - timedelta(days=random.randint(1, 180))
                    )
                    db.session.add(review)
                    review_count += 1
        
        db.session.flush()
        print(f"📝 Created {review_count} reviews")
        
        # Update book ratings
        print("⭐ Updating book ratings...")
        for book in all_books:
            reviews = Review.query.filter_by(book_id=book.id).all()
            if reviews:
                avg_rating = sum(r.rating for r in reviews) / len(reviews)
                book.rating = round(avg_rating, 1)
        
        # Create orders - FIXED: calculate total BEFORE adding order
        print("📦 Creating orders...")
        order_count = 0
        if all_users:
            for user in all_users[:3]:
                num_orders = random.randint(1, 3)
                for _ in range(num_orders):
                    # Select random books
                    num_items = random.randint(1, 4)
                    order_books = random.sample(all_books, min(num_items, len(all_books)))
                    
                    # Calculate total first
                    total = 0
                    items_data = []
                    for book in order_books:
                        quantity = random.randint(1, 2)
                        items_data.append({'book': book, 'quantity': quantity})
                        total += book.price * quantity
                    
                    # Add shipping if needed
                    total += 50 if total < 500 else 0
                    
                    # Create order with total already set
                    order = Order(
                        user_id=user.id,
                        total=total,
                        status=random.choice(['Confirmed', 'Shipped', 'Delivered']),
                        shipping_address=f"{random.choice(['12 Main St', '45 Park Ave', '78 Oak St', '23 Pine St'])}, {random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai'])}, {random.choice(['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu'])} - {random.randint(400001, 600000)}",
                        payment_method=random.choice(['Cash on Delivery', 'Demo Card Payment']),
                        created_at=datetime.now() - timedelta(days=random.randint(1, 90))
                    )
                    db.session.add(order)
                    db.session.flush()
                    
                    # Add order items
                    for item_data in items_data:
                        book = item_data['book']
                        quantity = item_data['quantity']
                        order_item = OrderItem(
                            order_id=order.id,
                            book_id=book.id,
                            quantity=quantity,
                            price=book.price
                        )
                        db.session.add(order_item)
                        if book.stock >= quantity:
                            book.stock -= quantity
                    
                    order_count += 1
        
        db.session.commit()
        print("=" * 50)
        print("✅ Database seeded successfully!")
        print(f"📚 {Book.query.count()} books")
        print(f"👤 {User.query.count()} users")
        print(f"📝 {Review.query.count()} reviews")
        print(f"📦 {Order.query.count()} orders")
        print("=" * 50)
        print("\n🔑 Demo Credentials:")
        print("   Admin: admin@bookninja.com / admin123")
        print("   User: john@example.com / password123")

if __name__ == '__main__':
    seed_database()