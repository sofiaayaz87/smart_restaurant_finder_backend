import mysql.connector

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASS = ""
DB_NAME = "smart_restaurant_finder"

try:
    db = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        auth_plugin='mysql_native_password'
    )

    cursor = db.cursor(buffered=True)
    cursor.execute("SHOW TABLES;")
    _ = cursor.fetchall()

    print("Database connected successfully!")

except mysql.connector.Error as err:
    print("Connection error:", err)
    db = None
    cursor = None
