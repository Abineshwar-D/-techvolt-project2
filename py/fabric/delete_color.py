#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
import cgi
import pymysql

cgitb.enable()

# Return plain text instead of text/html for fetch API
print("Content-Type: text/plain\n")

# 1. Database Connection
try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor()

    # 2. Get the form data
    form = cgi.FieldStorage()
    color_id = form.getvalue("color_id")

    if color_id:
        # 3. Delete using the primary key ID directly
        cursor.execute("DELETE FROM fabric_colors WHERE id = %s", (color_id,))
        conn.commit()

        # Send simple plain text back to JavaScript
        print("success")
    else:
        print("Error: Color ID not received.")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")