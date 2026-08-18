#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import json
import pymysql

print("Content-Type: application/json\n")

form = cgi.FieldStorage()
supplier_code = form.getvalue("supplier_code", "")

materials_list = []

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

    if row and row[0]:
        # Converts "sun run,bun" -> ['sun run', 'bun']
        materials_list = str(row[0]).split(",")

    cursor.close()
    conn.close()

    # Wrap in {"materials": [...]} dict so JavaScript can access data.materials
    print(json.dumps({"materials": materials_list}))

except Exception as e:
    print(json.dumps({"materials": [], "error": str(e)}))