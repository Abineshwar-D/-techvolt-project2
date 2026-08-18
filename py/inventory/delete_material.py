#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import json
import sys
import pymysql

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

print("Content-Type: application/json; charset=utf-8\n")

form = cgi.FieldStorage()
material_code = form.getvalue("material_code", "").strip()

if not material_code:
    print(json.dumps({"success": False, "error": "Material code missing"}))
    sys.exit()

try:
    conn = pymysql.connect(
        host="localhost", user="root", password="", database="techvoltproject2"
    )
    cursor = conn.cursor()

    cursor.execute("DELETE FROM materials WHERE material_code = %s", (material_code,))
    conn.commit()

    cursor.close()
    conn.close()

    print(json.dumps({"success": True}))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}))