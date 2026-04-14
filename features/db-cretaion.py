import mysql.connector
from faker import Faker
import random
import json
import bcrypt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from config import settings
load_dotenv()


class EcommerceDataGenerator:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=settings.db_host,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            port=settings.db_port,
        )
        self.cursor = self.conn.cursor()
        self.fake = Faker()

    def generate_categories(self):
        categories = [
            # Electronics
            ('Smartphones', 'Mobile devices and smart phones'),
            ('Laptops', 'Portable computers and notebooks'),
            ('Tablets', 'Handheld computing devices'),
            ('Headphones', 'Audio listening devices'),
            
            # Home Appliances
            ('Refrigerators', 'Kitchen cooling and preservation devices'),
            ('Washing Machines', 'Laundry cleaning appliances'),
            ('Vacuum Cleaners', 'Cleaning and dust removal devices'),
            
            # Fashion
            ('Men\'s Clothing', 'Apparel for men'),
            ('Women\'s Clothing', 'Apparel for women'),
            ('Shoes', 'Footwear for all genders'),
            
            # Books
            ('Fiction Books', 'Novels and storytelling literature'),
            ('Non-Fiction Books', 'Informative and educational books'),
            
            # Home & Kitchen
            ('Cookware', 'Cooking utensils and equipment'),
            ('Furniture', 'Home and office furnishings')
        ]
        self.cursor.executemany(
            'INSERT INTO categories (name, description) VALUES (%s, %s)', 
            categories
        )
        self.conn.commit()

    def generate_brands(self):
        brands = [
            # Electronics
            ('Apple', 'Innovative technology company'),
            ('Samsung', 'Global electronics manufacturer'),
            ('Dell', 'Computer and technology solutions'),
            ('Sony', 'Multimedia and electronics brand'),
            ('Bose', 'High-end audio equipment'),
            
            # Home Appliances
            ('LG', 'Home appliance and electronics manufacturer'),
            ('Whirlpool', 'Home appliance solutions'),
            ('Dyson', 'Innovative home technology'),
            
            # Fashion
            ('Nike', 'Athletic and casual wear'),
            ('Adidas', 'Sports and lifestyle brand'),
            ('Levi\'s', 'Denim and clothing manufacturer'),
            
            # Books
            ('Penguin', 'Publishing house'),
            ('Harper Collins', 'Book publishing company'),
            
            # Home & Kitchen
            ('KitchenAid', 'Cooking and kitchen appliances'),
            ('IKEA', 'Furniture and home accessories')
        ]
        self.cursor.executemany(
            'INSERT INTO brands (name, description) VALUES (%s, %s)', 
            brands
        )
        self.conn.commit()

    def generate_smartphone_specs(self):
        return json.dumps({
            'screen_size': f"{random.choice([5.8, 6.1, 6.5, 6.7])} inches",
            'camera': f"{random.choice([12, 16, 48, 64])} MP",
            'battery': f"{random.choice([3000, 4000, 5000])} mAh",
            'processor': random.choice(['A15 Bionic', 'Snapdragon 888', 'Exynos 2100']),
            'ram': f"{random.choice([6, 8, 12])} GB",
            'storage': f"{random.choice([128, 256, 512])} GB"
        })

    def generate_products(self):
        # Fetch existing categories and brands
        self.cursor.execute('SELECT category_id, name FROM categories')
        categories = self.cursor.fetchall()
        
        self.cursor.execute('SELECT brand_id, name FROM brands')
        brands = self.cursor.fetchall()

        # Generate Products
        products_to_insert = []
        for _ in range(100):  # Generate 100 products
            category = random.choice(categories)
            brand = random.choice(brands)

            # Determine specifications based on category
            if category[1] == 'Smartphones':
                specs = self.generate_smartphone_specs()
            else:
                specs = json.dumps({})

            product = (
                f"{brand[1]} {category[1]} Product",
                f"High-quality {category[1]} from {brand[1]}",
                category[0],
                brand[0],
                round(random.uniform(50, 2000), 2),
                random.randint(10, 500),
                specs,
                round(random.uniform(3.5, 5.0), 2),
                random.randint(10, 200)
            )
            products_to_insert.append(product)

        self.cursor.executemany('''
            INSERT INTO products 
            (name, description, category_id, brand_id, price, stock_quantity, 
            specifications, rating, num_reviews) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', products_to_insert)
        self.conn.commit()

    def generate_reviews(self):
        # Fetch product IDs
        self.cursor.execute('SELECT product_id FROM products')
        product_ids = [pid[0] for pid in self.cursor.fetchall()]

        # Generate Reviews
        reviews_to_insert = []
        for product_id in product_ids:
            num_reviews = random.randint(5, 50)
            for _ in range(num_reviews):
                review = (
                    product_id,
                    self.fake.name(),
                    random.randint(1, 5),
                    self.fake.paragraph(),
                    self.fake.date_between(start_date='-2y', end_date='today')
                )
                reviews_to_insert.append(review)

        self.cursor.executemany('''
            INSERT INTO reviews 
            (product_id, user_name, rating, review_text, review_date) 
            VALUES (%s, %s, %s, %s, %s)
        ''', reviews_to_insert)
        self.conn.commit()

    def generate_users(self, num_users=50):
        users_to_insert = []
        for _ in range(num_users):
            # Hash password
            password = self.fake.password()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            user = (
                self.fake.user_name(),
                self.fake.email(),
                hashed_password.decode('utf-8'),
                self.fake.name(),
                datetime.now() - timedelta(days=random.randint(1, 365))
            )
            users_to_insert.append(user)

        self.cursor.executemany('''
            INSERT INTO users 
            (username, email, password, full_name, registration_date) 
            VALUES (%s, %s, %s, %s, %s)
        ''', users_to_insert)
        self.conn.commit()

    def generate_orders(self, num_orders=200):
        # Fetch user and product IDs
        self.cursor.execute('SELECT user_id FROM users')
        user_ids = [uid[0] for uid in self.cursor.fetchall()]
        
        self.cursor.execute('SELECT product_id, price FROM products')
        products = self.cursor.fetchall()

        for _ in range(num_orders):
            user_id = random.choice(user_ids)
            order_date = self.fake.date_between(start_date='-1y', end_date='today')
            
            # Create order
            num_items = random.randint(1, 5)
            total_amount = 0
            
            order_status = random.choice(['Pending', 'Processing', 'Shipped', 'Delivered'])
            
            # Insert order first
            self.cursor.execute('''
                INSERT INTO orders 
                (user_id, order_date, total_amount, status) 
                VALUES (%s, %s, %s, %s)
            ''', (user_id, order_date, total_amount, order_status))
            
            # Get the last inserted order_id
            order_id = self.cursor.lastrowid

            # Create order items for this specific order
            order_items_to_insert = []
            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                price_at_time = product[1]
                item_total = quantity * price_at_time
                total_amount += item_total

                order_items_to_insert.append((
                    order_id,
                    product[0],
                    quantity,
                    price_at_time
                ))

            # Insert order items
            self.cursor.executemany('''
                INSERT INTO order_items 
                (order_id, product_id, quantity, price_at_time) 
                VALUES (%s, %s, %s, %s)
            ''', order_items_to_insert)

            # Update total amount in the order
            self.cursor.execute('''
                UPDATE orders 
                SET total_amount = %s 
                WHERE order_id = %s
            ''', (total_amount, order_id))

        self.conn.commit()

    def close_connection(self):
        self.cursor.close()
        self.conn.close()

def main():
    generator = EcommerceDataGenerator(
        host=settings.db_host,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )

    try:
        # Generate data in sequence
        generator.generate_categories()
        generator.generate_brands()
        generator.generate_products()
        generator.generate_reviews()
        generator.generate_users()
        generator.generate_orders()
        
        print("Database populated successfully!")
    finally:
        generator.close_connection()

if __name__ == '__main__':
    main()








   