#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import json
import pymysql

cgitb.enable()

# JSON Header
print("Content-Type: application/json\n")

form = cgi.FieldStorage()
machine_id = form.getvalue("id", "").strip()

if not machine_id:
    print(json.dumps({"status": "error", "message": "Machine ID missing"}))
    exit()

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor()

    # Delete machine from database
    cursor.execute("DELETE FROM machines WHERE id = %s", (machine_id,))
    conn.commit()

    cursor.close()
    conn.close()

    print(json.dumps({"status": "success", "message": "Machine deleted successfully"}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))