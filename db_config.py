import mysql.connector as MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return MySQLdb.connect(
        host=os.getenv('MYSQL_HOST', '127.0.0.1'),
        user=os.getenv('MYSQL_USER', 'flaskuser'),
        passwd=os.getenv('MYSQL_PASSWORD'),
        db=os.getenv('MYSQL_NAME', 'User_Logins')
    )
