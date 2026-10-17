
import psycopg2
import getpass

try:
    password = getpass.getpass("Enter PostgreSQL password: ")

    connection = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        database="smart_file_manager",
        user="postgres",
        password=password
    )

    print("Database connected successfully!")

    cursor = connection.cursor()
    cursor.execute("SELECT current_database();")
    print("Connected database:", cursor.fetchone()[0])

    cursor.close()
    connection.close()
    print("Connection closed successfully.")

except psycopg2.Error as error:
    print("Database connection failed.")
    print(error)
