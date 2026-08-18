#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
import json
import pymysql

cgitb.enable()
print("Content-Type: application/json\n")

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor()

    # Card 1: Total count of purchased_order table
    cursor.execute("SELECT COUNT(*) FROM purchased_order")
    total_po = cursor.fetchone()[0]

    # Card 2: Count where expected_delivery date <= today's date
    cursor.execute("SELECT COUNT(*) FROM purchased_order WHERE expected_delivery <= CURDATE()")
    pending_po = cursor.fetchone()[0]

    # Card 3: Approved/Completed Orders Count
    cursor.execute("SELECT COUNT(*) FROM purchased_order WHERE LOWER(status) = 'completed'")
    approved_po = cursor.fetchone()[0]

    # Card 4: Rejected Orders Count
    cursor.execute("SELECT COUNT(*) FROM purchased_order WHERE LOWER(status) = 'rejected'")
    rejected_po = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    response = {
        "status": "success",
        "total_po": total_po,
        "pending_po": pending_po,
        "approved_po": approved_po,
        "rejected_po": rejected_po
    }
    print(json.dumps(response))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))