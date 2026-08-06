#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
cgitb.enable()
import json
import pymysql

print("Content-Type: application/json\n")

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT supplier_code, supplier_name 
        FROM supplier 
        WHERE status = 'Active' 
        ORDER BY supplier_name
    """)
    rows = cursor.fetchall()

    suppliers = [{"code": row[0], "name": row[1]} for row in rows]
    print(json.dumps(suppliers))

    cursor.close()
    conn.close()
except Exception as e:
    print(json.dumps({"error": str(e)}))