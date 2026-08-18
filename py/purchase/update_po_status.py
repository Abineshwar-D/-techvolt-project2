#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe
import sys
import cgi
import json
import pymysql

# Set standard output to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Set JSON header
print("Content-Type: application/json; charset=utf-8\n")

form = cgi.FieldStorage()
po_number = form.getvalue("po_number", "").strip()
new_status = form.getvalue("status", "").strip()

if not po_number or not new_status:
    print(json.dumps({"success": False, "message": "Missing PO Number or Status."}))
    sys.exit(0)

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2",
        autocommit=True,
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    sql = "UPDATE purchased_order SET status = %s WHERE po_number = %s"
    affected_rows = cursor.execute(sql, (new_status, po_number))
    conn.commit()

    if affected_rows > 0:
        print(json.dumps({"success": True, "message": f"Status updated to '{new_status}' successfully!"}))
    else:
        print(json.dumps({"success": False, "message": f"No record found for PO Number '{po_number}'."}))

    cursor.close()
    conn.close()

except Exception as e:
    print(json.dumps({"success": False, "message": f"Database error: {str(e)}"}))