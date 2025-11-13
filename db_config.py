import mysql.connector as MySQLdb

def get_db_connection():
    return MySQLdb.connect(
        host="localhost",
        user="flaskuser",
        passwd="Babul(1109)",
        db="User_Logins"
    )
