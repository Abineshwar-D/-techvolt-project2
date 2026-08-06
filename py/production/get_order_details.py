#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
cgitb.enable()

import cgi
import json
import pymysql

print("Content-Type: application/json\n")

form = cgi.FieldStorage()

order = form.getvalue("order")

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="techvoltproject2"
)

cursor = conn.cursor()

cursor.execute("""
SELECT
customer,
fabric_type,
quantity
FROM orders
WHERE order_number=%s
""",(order,))

row = cursor.fetchone()

print(json.dumps({

    "customer": row[0],
    "fabric": row[1],
    "quantity": row[2]

}))

cursor.close()
conn.close()