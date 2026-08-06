#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import json
import pymysql

cgitb.enable()

print("Content-Type: application/json\n\n")

try:
    conn = pymysql.connect(
        host="localhost", user="root", password="", database="techvoltproject2"
    )

    cursor = conn.cursor()

    # Query marketing staff
    cursor.execute("""
        SELECT employee_id, fullname 
        FROM users 
        WHERE LOWER(role) = 'marketing' AND LOWER(status) = 'active'
        ORDER BY fullname ASC
    """)

    employees = cursor.fetchall()
    emp_list = [{"id": emp[0], "name": emp[1]} for emp in employees]

    print(json.dumps({"status": "success", "data": emp_list}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))

finally:
    if "conn" in locals():
        cursor.close()
        conn.close()