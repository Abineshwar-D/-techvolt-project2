#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
import pymysql

cgitb.enable()

print("Content-Type: text/html\n")

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="techvoltproject2",
)

cursor = conn.cursor()

# Query to select only orders that do not exist in the production plan table
cursor.execute("""
    SELECT o.order_number
    FROM orders o
    LEFT JOIN production_plan p ON o.order_number = p.order_no
    WHERE p.order_no IS NULL
    ORDER BY o.id DESC
""")

print("<option value=''>Select Order</option>")

for row in cursor.fetchall():
    print(f"<option value='{row[0]}'>{row[0]}</option>")

cursor.close()
conn.close()