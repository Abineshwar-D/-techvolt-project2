#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
cgitb.enable()
import cgi
import json
import pymysql

print("Content-Type: application/json\n")

form = cgi.FieldStorage()
supplier_code = form.getvalue("supplier_code", "")

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT material_supplied 
        FROM supplier 
        WHERE supplier_code = %s AND status = 'Active'
    """, (supplier_code,))
    row = cursor.fetchone()

    materials_list = []
    if row and row[0]:
        # Handles single or comma-separated materials (e.g., "Cotton Yarn, Dye")
        raw_materials = row[0].split(",")
        materials_list = [m.strip() for m in raw_materials if m.strip()]

    print(json.dumps(materials_list))

    cursor.close()
    conn.close()
except Exception as e:
    print(json.dumps({"error": str(e)}))