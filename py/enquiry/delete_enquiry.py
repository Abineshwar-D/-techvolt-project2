#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe
import cgi
import cgitb
import json
import pymysql

cgitb.enable()

print("Content-Type: application/json\n")

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2",
        autocommit=True,
    )
    cursor = conn.cursor()

    form = cgi.FieldStorage()
    db_id = form.getvalue("db_id")

    if db_id:
        cursor.execute(
            "DELETE FROM customers_enquiries WHERE id = %s", (db_id,)
        )
        conn.close()
        print(
            json.dumps({
                "status": "success",
                "message": "Enquiry deleted successfully!",
            })
        )
    else:
        conn.close()
        print(
            json.dumps({
                "status": "error",
                "message": "Invalid ID provided!",
            })
        )

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))