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
    plan_no = form.getvalue("plan_no", "").strip()
    status = form.getvalue("status", "").strip()

    if not plan_no or not status:
        print(json.dumps({"status": "error", "message": "Plan number or status missing"}))
        sys.exit()

    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2",
        autocommit=True,
    )
    cursor = conn.cursor()

    cursor.execute("UPDATE production_plan SET status = %s WHERE plan_no = %s", (status, plan_no))

    cursor.close()
    conn.close()

    print(json.dumps({"status": "success", "message": "Production plan status updated successfully."}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))