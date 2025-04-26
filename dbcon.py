import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YJnov@06",
        database="farmer_schemes_db"
    )
