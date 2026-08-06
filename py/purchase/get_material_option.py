#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
cgitb.enable()
import cgi
import json
import pymysql

print("Content-Type: application/json\n")

form = cgi.FieldStorage()
material_name = form.getvalue("material_name", "")

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor()

    # 1. Check for exact or partial name match in materials table
    cursor.execute("""
        SELECT opening_stock 
        FROM materials 
        WHERE LOWER(material_name) LIKE LOWER(%s) AND status = 'Active'
        LIMIT 1
    """, (f"%{material_name}%",))
    row = cursor.fetchone()

    # If material exists, send opening_stock; otherwise, send 0
    stock = float(row[0]) if (row and row[0] is not None) else 0

    print(json.dumps({"stock": stock}))

    cursor.close()
    conn.close()
except Exception as e:
    print(json.dumps({"stock": 0, "error": str(e)}))