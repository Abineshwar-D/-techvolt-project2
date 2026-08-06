#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
import cgi
import pymysql
import json

cgitb.enable()

print("Content-Type: application/json\n")


conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="techvoltproject2"
)


cursor = conn.cursor()

form = cgi.FieldStorage()

employee_id = form.getvalue("employee_id")


sql = """
SELECT employee_id,email,state,city,phonenumber
FROM users
WHERE employee_id=%s
"""


cursor.execute(sql, (employee_id,))


user = cursor.fetchone()


if user:

    data = {
        "employee_id": user[0],
        "email": user[1],
        "state": user[2],
        "city": user[3],
        "phone": user[4]
    }

else:

    data = {
        "error": "User not found"
    }


print(json.dumps(data))


conn.close()