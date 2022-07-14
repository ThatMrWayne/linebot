import mysql.connector
from mysql.connector import errorcode
from mysql.connector import pooling
from settings import MYSQL_PASSWORD
from settings import MYSQL_USER
from flask import current_app
import time


class DataBase():
    def __init__(self):
        try:
            config = {
                'user': MYSQL_USER,
                'password': MYSQL_PASSWORD,
                'host': '127.0.0.1',
                'database': 'linebot',
                'raise_on_warnings': True, 
                }
            # create connection
            self.cnxpool = pooling.MySQLConnectionPool(pool_name="pool", pool_size=5, **config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err.msg)
            exit(1)


    def set_image(self,user_id,image_id):
        n = 0
        cnx = None
        result,msg=None,None
        while n < 50: 
            try:
                cnx = self.cnxpool.get_connection()
                break
            except mysql.connector.Error as err: 
                current_app.logger.info('cannot get mysql connection from connection pool.')
                n+=1
                time.sleep(0.1) 
        if cnx:
            cursor = cnx.cursor()
            query = "INSERT INTO images VALUES (%(user_id)s,%(image_id)s) ON DUPLICATE KEY UPDATE image=%(image_id)s"            
            try:
                cursor.execute(query, {'user_id': user_id , "image_id" : image_id})
                cnx.commit()
                affected_row = cursor.rowcount
                result = affected_row
            except mysql.connector.Error as err: 
                msg = err.msg
                current_app.logger.info(msg)
            finally:
                cursor.close()
                cnx.close()
                if result:
                    return result
                else:
                    return "error"
        else:
            return "error"



    def get_image(self,user_id):
        n = 0
        cnx = None
        result,msg=None,None
        while n < 50: 
            try:
                cnx = self.cnxpool.get_connection()
                break
            except mysql.connector.Error as err: 
                current_app.logger.info('cannot get mysql connection from connection pool.')
                n+=1
                time.sleep(0.1) 
        if cnx:
            cursor = cnx.cursor(dictionary=True)
            query = "SELECT image FROM images WHERE userId = %(user_id)s"
            try:
                cursor.execute(query, {'user_id': user_id })
                result = cursor.fetchone()
            except mysql.connector.Error as err: 
                msg = err.msg
                current_app.logger.info(msg)
            finally:
                cursor.close()
                cnx.close()
                if result:
                    return result["image"]
                elif msg:
                    return "error"
                else:
                    return "no image"    
        else:
            return "error"

            


 

db = DataBase() 