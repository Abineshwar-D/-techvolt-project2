#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import pymysql
import json

print("Content-Type: application/json\n")

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT enquiry_no FROM enquiries ORDER BY enquiry_id DESC")
    rows = cursor.fetchall()

    print(json.dumps(rows))

except Exception as e:
    print(json.dumps([]))
finally:
    if 'conn' in locals():
        conn.close()