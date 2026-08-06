#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb

import cgi
import pymysql

cgitb.enable()
print("Content-Type: text/html\n")

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="techvoltproject2"
)

cursor = conn.cursor()
form = cgi.FieldStorage()
employee_id = form.getvalue("employee_id")

cursor.execute("""
UPDATE users
SET 
    status = %s
WHERE employee_id=%s
""", (
    "InActive",
    employee_id
))


print("""
{
    "status":"success",
    "message":"User InActive"
}
""")
conn.commit()
conn.close()
