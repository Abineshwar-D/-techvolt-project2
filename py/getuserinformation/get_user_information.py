#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import pymysql
import json

cgitb.enable()

# Output JSON header
print("Content-Type: application/json\n")

form = cgi.FieldStorage()
user_id = form.getvalue("user_id")

response = {"success": False, "message": "User not found"}

if user_id:
    try:
        con = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="techvoltproject2",
            cursorclass=pymysql.cursors.DictCursor  # Returns query result as a Dictionary
        )
        cur = con.cursor()

        # Fetch employee details from users table
        cur.execute(
            "SELECT employee_id, fullname, email, role FROM users WHERE employee_id=%s",
            (user_id,)
        )
        user_data = cur.fetchone()

        if user_data:
            response = {
                "success": True,
                "data": user_data
            }
        else:
            # Check admin table if not found in users
            cur.execute(
                "SELECT employee_id, fullname, email, 'Admin' as role FROM admin WHERE employee_id=%s",
                (user_id,)
            )
            admin_data = cur.fetchone()
            if admin_data:
                response = {
                    "success": True,
                    "data": admin_data
                }

        con.close()
    except Exception as e:
        response = {"success": False, "message": str(e)}

print(json.dumps(response))