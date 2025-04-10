import pymysql
from pymysql import Error

def get_db_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            database='travelbus',
            user='root',
            password=''
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        raise e
