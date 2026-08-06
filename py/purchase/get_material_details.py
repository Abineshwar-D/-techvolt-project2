#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
cgitb.enable()

import cgi
import json
import pymysql

print("Content-Type: application/json\n")

form = cgi.FieldStorage()
material_id = form.getvalue("id")

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="techvoltproject2"
)

cursor = conn.cursor()

cursor.execute("""
SELECT
    opening_stock,  
    reorder_level,
    unit_cost
FROM materials
WHERE material_id = %s
""", (material_id,))

row = cursor.fetchone()

if row:
    print(json.dumps({
        "stock": float(row[0] or 0),
        "reorder": float(row[1] or 0),
        "cost": float(row[2] or 0)
    }))
else:
    print(json.dumps({
        "error": "Material not found"
    }))

cursor.close()
conn.close()