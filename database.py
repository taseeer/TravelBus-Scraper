import pymysql

# Database connection
def get_db_connection():
    return pymysql.connect(
        host="localhost",  # Change if needed
        user="root",
        password="",
        database="travelbus",
        cursorclass=pymysql.cursors.DictCursor
    )
