#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
cgitb.enable()

print("Content-Type: text/html\n")

import cgi
import pymysql

form = cgi.FieldStorage()
customer_id = form.getvalue("id")

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )

    cursor = conn.cursor()

    sql = "DELETE FROM customers WHERE id=%s"
    cursor.execute(sql, (customer_id,))
    conn.commit()

    print("Customer deleted successfully")

    cursor.close()
    conn.close()

except Exception as e:
    print("Error:", e)