import random
from faker import Faker
import json
import mysql.connector
from datetime import datetime, timedelta
from config import settings

class EcommerceDataGenerator:
    def __init__(self, db_config):
        self.fake = Faker()
        self.db_config = db_config
        
    def generate_brands(self, num_brands=20):
        brands = []
        tech_brands = [
            "Apple", "Samsung", "Sony", "Dell", "HP", 
            "Lenovo", "Microsoft", "Asus", "Acer", "Huawei",
            "LG", "Xiaomi", "OnePlus", "Google", "Razer",
            "Alienware", "Oppo", "Realme", "Nvidia", "Intel"
        ]
        
        for name in tech_brands[:num_brands]:
            brands.append({
                'name': name,
                'description': f"{name} is a leading technology company specializing in innovative {random.choice(['electronics', 'computing', 'mobile', 'consumer technology'])} products."
            })
        return brands
    
    def generate_categories(self):
        return [
            {'name': 'Smartphones', 'description': 'Latest mobile phones and smart devices'},
            {'name': 'Laptops', 'description': 'Portable computing devices for work and play'},
            {'name': 'Tablets', 'description': 'Versatile touchscreen devices'},
            {'name': 'Smartwatches', 'description': 'Wearable tech for fitness and communication'},
            {'name': 'Accessories', 'description': 'Phone cases, chargers, and tech add-ons'},
            {'name': 'Audio', 'description': 'Headphones, speakers, and sound systems'}
        ]
    
    def generate_product_specifications(self, category):
        spec_templates = {
            'Smartphones': {
                'ram': ['4 GB', '6 GB', '8 GB', '12 GB'],
                'camera': ['12 MP', '48 MP', '64 MP', '108 MP'],
                'battery': ['3500 mAh', '4000 mAh', '5000 mAh', '6000 mAh'],
                'storage': ['64 GB', '128 GB', '256 GB', '512 GB'],
                'processor': ['Snapdragon 888', 'Exynos 2100', 'A14 Bionic', 'Tensor G2'],
                'screen_size': ['5.8 inches', '6.1 inches', '6.5 inches', '6.7 inches']
            },
            'Laptops': {
                'cpu': ['Intel Core i5', 'Intel Core i7', 'AMD Ryzen 5', 'AMD Ryzen 7'],
                'ram': ['8 GB', '16 GB', '32 GB'],
                'storage': ['256 GB SSD', '512 GB SSD', '1 TB SSD'],
                'display': ['14 inch', '15.6 inch', '16 inch'],
                'graphics': ['Integrated', 'NVIDIA GeForce', 'AMD Radeon']
            }
        }
        return json.dumps(
            {k: random.choice(v) for k, v in spec_templates.get(category, {}).items()}
        )
    
    def generate_products(self, brands, categories):
        products = []
        product_names = {
            'Smartphones': [
                '{brand} {model} Smartphone',
                '{brand} {model} Pro',
                '{brand} {model} Ultra'
            ],
            'Laptops': [
                '{brand} {model} Laptop',
                '{brand} {model} Pro Laptop',
                '{brand} {model} Business Laptop'
            ]
        }
        
        models = ['X', 'Pro', 'Elite', 'Plus', 'Max', 'Prime']
        
        for category in categories:
            cat_name = category['name']
            for brand in brands:
                for _ in range(random.randint(3, 6)):
                    model = random.choice(models)
                    name_template = random.choice(product_names.get(cat_name, ['{brand} {model}']))
                    name = name_template.format(brand=brand['name'], model=model)
                    
                    products.append({
                        'name': name,
                        'description': f"High-performance {cat_name.lower()} from {brand['name']}",
                        'category_id': categories.index(category) + 1,
                        'brand_id': brands.index(brand) + 1,
                        'price': round(random.uniform(100, 2000), 2),
                        'stock_quantity': random.randint(50, 500),
                        'specifications': self.generate_product_specifications(cat_name),
                        'rating': round(random.uniform(3.5, 5.0), 2),
                        'num_reviews': random.randint(10, 200)
                    })
        return products
    
    def generate_users(self, num_users=100):
        users = []
        for _ in range(num_users):
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            username = f"{first_name.lower()}_{last_name.lower()}_{random.randint(10, 999)}"
            
            users.append({
                'username': username,
                'email': self.fake.email(),
                'password': self.fake.password(),
                'full_name': f"{first_name} {last_name}",
                'registration_date': self.fake.date_time_between(start_date='-2y', end_date='now')
            })
        return users
    
    def generate_reviews(self, products, users):
        reviews = []
        review_templates = [
            "{positive_adj} {product}! {specific_praise}",
            "Not what I expected. {constructive_criticism}",
            "Absolutely recommend this {product}. {detailed_feedback}",
            "Great value for money. {specific_highlight}"
        ]
        
        positive_adjs = ['Fantastic', 'Amazing', 'Incredible', 'Wonderful']
        specific_praises = [
            'The performance blew me away!',
            'Perfect for my everyday needs.',
            'Best purchase I\'ve made this year!'
        ]
        
        constructive_criticisms = [
            'Battery life could be improved.',
            'Somewhat expensive for the features.',
            'Takes time to get used to the interface.'
        ]
        
        for product in products:
            num_reviews = random.randint(5, min(product['num_reviews'], 50))
            for _ in range(num_reviews):
                user = random.choice(users)
                rating = random.choices(
                    [1, 2, 3, 4, 5], 
                    weights=[5, 10, 15, 30, 40]
                )[0]
                
                review_type = random.choice(review_templates)
                review_text = review_type.format(
                    product=product['name'],
                    positive_adj=random.choice(positive_adjs),
                    specific_praise=random.choice(specific_praises),
                    constructive_criticism=random.choice(constructive_criticisms),
                    detailed_feedback='Highly recommended!',
                    specific_highlight='Great design and functionality.'
                )
                
                reviews.append({
                    'product_id': products.index(product) + 1,
                    'user_name': user['username'],
                    'rating': rating,
                    'review_text': review_text,
                    'review_date': self.fake.date_between(start_date='-1y', end_date='today')
                })
        return reviews
    
    def generate_orders(self, users, products):
        orders = []
        order_items = []
        
        for user in users:
            num_orders = random.randint(1, 5)
            for _ in range(num_orders):
                num_items = random.randint(1, 4)
                total_amount = 0
                order_date = self.fake.date_time_between(start_date='-1y', end_date='now')
                
                order = {
                    'user_id': users.index(user) + 1,
                    'order_date': order_date,
                    'status': random.choice(['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'])
                }
                
                order_id = len(orders) + 1
                order['order_id'] = order_id
                orders.append(order)
                
                selected_products = random.sample(products, num_items)
                for product in selected_products:
                    quantity = random.randint(1, 3)
                    price_at_time = product['price']
                    total_amount += price_at_time * quantity
                    
                    order_items.append({
                        'order_id': order_id,
                        'product_id': products.index(product) + 1,
                        'quantity': quantity,
                        'price_at_time': price_at_time
                    })
                
                orders[-1]['total_amount'] = round(total_amount, 2)
        
        return orders, order_items

    def insert_brands(self, connection, brands):
        cursor = connection.cursor()
        insert_query = "INSERT INTO brands (name, description) VALUES (%s, %s)"
        try:
            cursor.executemany(insert_query, [(b['name'], b['description']) for b in brands])
            connection.commit()
            print(f"Inserted {cursor.rowcount} brands")
        except mysql.connector.Error as err:
            print(f"Error inserting brands: {err}")
        finally:
            cursor.close()

    def insert_categories(self, connection, categories):
        cursor = connection.cursor()
        insert_query = "INSERT INTO categories (name, description) VALUES (%s, %s)"
        try:
            cursor.executemany(insert_query, [(c['name'], c['description']) for c in categories])
            connection.commit()
            print(f"Inserted {cursor.rowcount} categories")
        except mysql.connector.Error as err:
            print(f"Error inserting categories: {err}")
        finally:
            cursor.close()

    def insert_products(self, connection, products):
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO products 
        (name, description, category_id, brand_id, price, stock_quantity, specifications, rating, num_reviews) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            cursor.executemany(insert_query, [
                (p['name'], p['description'], p['category_id'], p['brand_id'], 
                 p['price'], p['stock_quantity'], p['specifications'], 
                 p['rating'], p['num_reviews']) for p in products
            ])
            connection.commit()
            print(f"Inserted {cursor.rowcount} products")
        except mysql.connector.Error as err:
            print(f"Error inserting products: {err}")
        finally:
            cursor.close()

    def insert_users(self, connection, users):
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO users 
        (username, email, password, full_name, registration_date) 
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            cursor.executemany(insert_query, [
                (u['username'], u['email'], u['password'], 
                 u['full_name'], u['registration_date']) for u in users
            ])
            connection.commit()
            print(f"Inserted {cursor.rowcount} users")
        except mysql.connector.Error as err:
            print(f"Error inserting users: {err}")
        finally:
            cursor.close()

    def insert_reviews(self, connection, reviews):
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO reviews 
        (product_id, user_name, rating, review_text, review_date) 
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            cursor.executemany(insert_query, [
                (r['product_id'], r['user_name'], r['rating'], 
                 r['review_text'], r['review_date']) for r in reviews
            ])
            connection.commit()
            print(f"Inserted {cursor.rowcount} reviews")
        except mysql.connector.Error as err:
            print(f"Error inserting reviews: {err}")
        finally:
            cursor.close()

    def insert_orders(self, connection, orders):
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO orders 
        (user_id, order_date, total_amount, status) 
        VALUES (%s, %s, %s, %s)
        """
        try:
            cursor.executemany(insert_query, [
                (o['user_id'], o['order_date'], o['total_amount'], o['status']) for o in orders
            ])
            connection.commit()
            print(f"Inserted {cursor.rowcount} orders")
        except mysql.connector.Error as err:
            print(f"Error inserting orders: {err}")
        finally:
            cursor.close()

    def insert_order_items(self, connection, order_items):
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO order_items 
        (order_id, product_id, quantity, price_at_time) 
        VALUES (%s, %s, %s, %s)
        """
        try:
            cursor.executemany(insert_query, [
                (oi['order_id'], oi['product_id'], oi['quantity'], oi['price_at_time']) for oi in order_items
            ])
            connection.commit()
            print(f"Inserted {cursor.rowcount} order items")
        except mysql.connector.Error as err:
            print(f"Error inserting order items: {err}")
        finally:
            cursor.close()


    def populate_database(self):

        try:

            # Establish database connection

            connection = mysql.connector.connect(**self.db_config)

            # Generate data

            brands = self.generate_brands()

            categories = self.generate_categories()

            # Clear existing data (optional, be careful!)

            cursors = connection.cursor()

            tables_to_clear = [

                'order_items', 'orders', 'reviews', 

                'products', 'categories', 'brands', 'users'

            ]

            for table in tables_to_clear:

                cursors.execute(f"DELETE FROM {table}")

            connection.commit()

            cursors.close()

            # Insert base data first

            self.insert_brands(connection, brands)

            self.insert_categories(connection, categories)

            # Generate and insert dependent data

            users = self.generate_users()

            self.insert_users(connection, users)

            products = self.generate_products(brands, categories)

            self.insert_products(connection, products)

            reviews = self.generate_reviews(products, users)

            self.insert_reviews(connection, reviews)

            orders, order_items = self.generate_orders(users, products)

            self.insert_orders(connection, orders)

            self.insert_order_items(connection, order_items)

            print("Database population completed successfully!")

        except mysql.connector.Error as err:

            print(f"Error: {err}")

        finally:

            if connection.is_connected():

                connection.close()

                print("MySQL connection is closed")
 
def main():

    db_config = settings.db_config
 
    # Create generator instance

    generator = EcommerceDataGenerator(db_config)

    # Populate the database

    generator.populate_database()
 
# Prerequisite installations

print("Before running this script, ensure you have installed:")

print("1. pip install Faker")

print("2. pip install mysql-connector-python")

print("\nAlso, make sure you have:")

print("1. MySQL server running")

print("2. Database 'ecommerce_chatbot_101' created")

print("3. Updated database credentials in the script")
 
if __name__ == "__main__":

    main()

