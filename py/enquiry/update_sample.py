#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe
import cgi
import json
import pymysql

print("Content-Type: application/json\n")

form = cgi.FieldStorage()
db_id = form.getvalue("id")
enq_id = form.getvalue("enquiry_id")

try:
    db = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2",
        autocommit=True,
    )
    cursor = db.cursor()

    # Match by numeric DB id if available, else by string enquiry_id
    if db_id:
        cursor.execute(
            "UPDATE customers_enquiries SET sample_status = 1 WHERE id = %s",
            (db_id,),
        )
    elif enq_id:
        cursor.execute(
            "UPDATE customers_enquiries SET sample_status = 1 WHERE enquiry_id = %s",
            (enq_id,),
        )
    else:
        print(
            json.dumps({"status": "error", "message": "Missing ID parameter"})
        )
        exit()

    print(json.dumps({"status": "success"}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
finally:
    if "db" in locals():
        db.close()