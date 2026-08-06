#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import pymysql
import json

import cgitb
cgitb.enable()

print("Content-Type: application/json\n")

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="techvoltproject2"
)

cursor = conn.cursor()

cursor.execute("""
SELECT id, customer_name
FROM customers
ORDER BY customer_name
""")

rows = cursor.fetchall()

data=[]

for r in rows:
    data.append({
        "id":r[0],
        "name":r[1]
    })

print(json.dumps(data))

cursor.close()
conn.close()