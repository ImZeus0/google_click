import pymysql
from datetime import datetime
import random


def connect():
    return pymysql.connect(host='108.61.190.204', user='service',
                           password='123qweQWE', database='shema', charset='utf8', port=3306)


def add_click(id_project, country, url, key):
    c = connect()
    cursor = c.cursor()
    sql = f"INSERT INTO clicks (id_project, country, url, keyword,date) VALUES (%s,%s,%s,%s,%s);"
    cursor.execute(sql, (id_project, country, url, key,datetime.now()))
    c.commit()
    c.close()


