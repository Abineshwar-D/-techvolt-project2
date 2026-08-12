#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
import cgi
import pymysql

cgitb.enable()

print("Content-Type: text/html\n")

# 1. Database Connection
try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor()

    # 2. Get form data
    form = cgi.FieldStorage()
    color_id = form.getvalue("color_id")
    color_name = form.getvalue("color_name")
    price_name = form.getvalue("price_name")

    # 3. Validation Check
    if color_id and color_name and price_name:
        cursor.execute(
            "UPDATE fabric_colors SET color_name = %s, price = %s, created_at = NOW() WHERE id = %s",
            (color_name, price_name, color_id)
        )
        conn.commit()
        print("Success")
    else:
        # Diagnostic message to pinpoint which value is missing
        missing = []
        if not color_id: missing.append("color_id")
        if not color_name: missing.append("color_name")
        if not price_name: missing.append("price_name")
        print(f"<h3>Error: Missing fields -> {', '.join(missing)}</h3>")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"<h3>Database/Server Error: {e}</h3>")