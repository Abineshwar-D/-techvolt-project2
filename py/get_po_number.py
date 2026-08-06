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

# Get last material code
cursor.execute("""
        SELECT po_number
        FROM purchased_order
        ORDER BY id DESC
        LIMIT 1
    """)

row = cursor.fetchone()

if row:

    last_code = row[0]  # MAT001

    number = int(last_code[3:])

    new_code = "PO{:03d}".format(number + 1)

else:

    new_code = "MAT001"
