#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import pymysql
import json
from datetime import date, datetime

print("Content-Type: application/json\n")


def json_serial(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError("Type not serializable")


try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT 
            sample_no,
            customer_name,
            fabric_type,
            sample_status
        FROM samples 
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    print(json.dumps(rows, default=json_serial))

except Exception as e:
    print(json.dumps({"error": str(e)}))
finally:
    if 'conn' in locals():
        conn.close()
