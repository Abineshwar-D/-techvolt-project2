#!C:\Users\Abi\AppData\Local\Programs\Python\Python311\python.exe

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

    # Fetch unique active supplier names
    cursor.execute("""
        SELECT DISTINCT supplier_name 
        FROM supplier 
        WHERE status = 'Active' 
        ORDER BY supplier_name ASC
    """)

    rows = cursor.fetchall()

    # Convert tuples list to simple array e.g., ["ABC Yarns Pvt Ltd", "google"]
    suppliers = [row[0] for row in rows]

    cursor.close()
    conn.close()

    print(json.dumps(suppliers))

except Exception as e:
    print(json.dumps([]))