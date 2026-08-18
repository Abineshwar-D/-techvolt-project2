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
    customer_name = form.getvalue("customer_name")
    phone_number = form.getvalue("phone_number")
    email = form.getvalue("email")
    new_quantity = form.getvalue("quantity")

    # Fetch current record details to compare quantity
    cursor.execute(
        "SELECT quantity, sample_status FROM customers_enquiries WHERE id = %s",
        (db_id,),
    )
    current_record = cursor.fetchone()

    if current_record:
        old_quantity = current_record[0]
        current_status = current_record[1]

        # If quantity is modified, set sample_status = 1, else keep current status
        if (
            new_quantity is not None
            and str(new_quantity) != str(old_quantity)
        ):
            new_status = 1
        else:
            new_status = current_status

        # Update row in database
        cursor.execute(
            """
            UPDATE customers_enquiries 
            SET customer_name = %s, 
                phone_number = %s, 
                email = %s, 
                quantity = %s,
                sample_status = %s
            WHERE id = %s
        """,
            (
                customer_name,
                phone_number,
                email,
                new_quantity,
                new_status,
                db_id,
            ),
        )

        conn.close()
        print(
            json.dumps({
                "status": "success",
                "message": "Enquiry updated successfully!",
            })
        )
    else:
        conn.close()
        print(
            json.dumps({
                "status": "error",
                "message": "Record not found!",
            })
        )

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))