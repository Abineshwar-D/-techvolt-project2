#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

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
    s_id = form.getvalue("id", "").strip()

    if not s_id:
        print(json.dumps({"status": "error", "message": "Supervisor ID is missing."}))
        sys.exit()

    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2",
        autocommit=True,
    )
    cursor = conn.cursor()

    cursor.execute("DELETE FROM supervisor WHERE id = %s", (s_id,))

    cursor.close()
    conn.close()

    print(json.dumps({"status": "success", "message": "Supervisor deleted successfully."}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))