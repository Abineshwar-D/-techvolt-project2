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
    order_no = form.getvalue("order_number")

    if order_no:
        cursor.execute(
            "DELETE FROM orders WHERE order_number = %s", (order_no,)
        )
        conn.close()
        print(
            json.dumps({
                "status": "success",
                "message": "Order deleted successfully!",
            })
        )
    else:
        conn.close()
        print(
            json.dumps({
                "status": "error",
                "message": "Order number is missing!",
            })
        )

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))