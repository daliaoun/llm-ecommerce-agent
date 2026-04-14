import mysql.connector
import json
from config import settings

def extract_and_save_schema(database_name, file_name="schema.json", host="localhost", user="root", password="", port=3306):
    """
    Extracts the schema of a MySQL database and saves it locally as a JSON file.
    
    Args:
        database_name (str): The name of the database to extract the schema from.
        file_name (str): The name of the JSON file to save the schema to (default is "schema.json").
        host (str): The host of the MySQL server (default is "localhost").
        user (str): The MySQL username (default is "root").
        password (str): The MySQL password (default is empty).

    Returns:
        None
    """
    try:
        # Connect to the MySQL server
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_name,
            port=port,
        )
        cursor = connection.cursor()

        # Get all table names
        cursor.execute("SHOW TABLES;")
        tables = [table[0] for table in cursor.fetchall()]

        schema = {}

        # Get columns for each table
        for table in tables:
            cursor.execute(f"DESCRIBE {table};")
            columns = cursor.fetchall()
            schema[table] = [{"Field": col[0], "Type": col[1], "Null": col[2], "Key": col[3]} for col in columns]

        cursor.close()
        connection.close()

        # Save schema to JSON file
        with open(file_name, "w") as file:
            json.dump(schema, file, indent=4)
        print(f"Schema saved to {file_name}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    except IOError as io_err:
        print(f"File Error: {io_err}")

if __name__ == "__main__":
    extract_and_save_schema(
        database_name=settings.db_name,
        file_name="one_of_one.json",
        host=settings.db_host,
        user=settings.db_user,
        password=settings.db_password,
        port=settings.db_port,
    )