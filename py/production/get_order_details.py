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

# Query updated to fetch delivery_date
cursor.execute("""
SELECT
customer,
fabric_type,
quantity,
delivery_date
FROM orders
WHERE order_number=%s
""", (order,))

row = cursor.fetchone()

if row:
    # Convert delivery_date to string for JSON serialization
    delivery_date_str = str(row[3]) if row[3] else ""

    print(json.dumps({
        "customer": row[0],
        "fabric": row[1],
        "quantity": row[2],
        "delivery_date": delivery_date_str
    }))
else:
    print(json.dumps({
        "customer": "",
        "fabric": "",
        "quantity": 0,
        "delivery_date": ""
    }))

cursor.close()
conn.close()
