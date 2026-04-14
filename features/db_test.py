import mysql.connector
from mysql.connector import Error
from config import settings

def connect_to_database():
    try:
        # Establish the connection
        connection = mysql.connector.connect(
            host=settings.db_host,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            port=settings.db_port,
        )


        if connection.is_connected():
            print("Successfully connected to the database")

            # Create a cursor to interact with the database
            cursor = connection.cursor()

            # Query to get all table names
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()

            # Print all the table names
            print("Tables in the database:")
            for table in tables:
                print(table[0])  # table is a tuple, so table[0] will give the table name

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    connect_to_database()

