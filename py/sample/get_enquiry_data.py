#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import pymysql
import json

print("Content-Type: application/json\n")

form = cgi.FieldStorage()
enquiry_no = form.getvalue("enquiry_no")

if not enquiry_no:
    print(json.dumps({"success": False, "message": "Enquiry number required"}))
else:
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="techvoltproject2"
        )
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        cursor.execute("""
            SELECT 
                customer_id, 
                contact_person, 
                fabric_type, 
                fabric_gsm, 
                color 
            FROM enquiries 
            WHERE enquiry_no = %s
        """, (enquiry_no,))

        row = cursor.fetchone()

        if row:
            print(json.dumps({
                "success": True,
                **row
            }))
        else:
            print(json.dumps({"success": False, "message": "Enquiry not found"}))
    except Exception as e:
        print(json.dumps({"success": False, "message": str(e)}))
    finally:
        if 'conn' in locals():
            conn.close()