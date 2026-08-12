#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

from decimal import Decimal
import cgi
import cgitb
import json
import pymysql

cgitb.enable()

print("Content-Type: application/json\n")


# Custom JSON Encoder to handle Decimal and datetime types automatically
class CustomJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # Convert Decimal to Float for clean JSON output
        return super().default(obj)


try:
    form = cgi.FieldStorage()
    target_id = form.getvalue("id")

    if not target_id:
        print(json.dumps({"status": "error", "message": "No ID provided"}))
        exit()

    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2",
        cursorclass=pymysql.cursors.DictCursor,
    )

    cursor = conn.cursor()

    # Query required fields
    query = """
        SELECT 
            customer_name, company_name, phone_number, fabric_type, 
            color, price, quantity, city, state, created_at, created_by_name 
        FROM customers_enquiries 
        WHERE id = %s
    """
    cursor.execute(query, (target_id,))
    record = cursor.fetchone()

    if record:
        # Convert created_at to YYYY-MM-DD string format
        if record.get("created_at"):
            record["created_at"] = record["created_at"].strftime("%Y-%m-%d")

        # Dump JSON using our CustomJSONEncoder
        print(
            json.dumps(
                {"status": "success", "data": record}, cls=CustomJSONEncoder
            )
        )
    else:
        print(json.dumps({"status": "error", "message": "Record not found"}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))

finally:
    if "conn" in locals():
        cursor.close()
        conn.close()