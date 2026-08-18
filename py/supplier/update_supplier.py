#!C:\Users\Abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import json
import sys
import pymysql

cgitb.enable()

sys.stdout.reconfigure(encoding="utf-8")

print("Content-Type: application/json; charset=utf-8\n")

try:
    form = cgi.FieldStorage()
    supplier_code = form.getvalue("supplier_code", "").strip()
    phone = form.getvalue("phone", "").strip()
    email = form.getvalue("email", "").strip()
    material_supplied = form.getvalue("material_supplied", "").strip()
    status = form.getvalue("status", "").strip()

    if not supplier_code:
        print(json.dumps({"status": "error", "message": "Supplier code is missing."}))
        sys.exit()

    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2",
        autocommit=True,
        charset="utf8mb4"
    )
    cursor = conn.cursor()

    # Update supplier record in database
    cursor.execute("""
        UPDATE supplier 
        SET phone = %s, email = %s, material_supplied = %s, status = %s 
        WHERE supplier_code = %s
    """, (phone, email, material_supplied, status, supplier_code))

    cursor.close()
    conn.close()

    print(json.dumps({"status": "success", "message": "Supplier updated successfully."}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))