#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import pymysql
import json
import os
import sys

print("Content-Type: application/json\n")

try:
    data = json.loads(sys.stdin.read(int(os.environ.get('CONTENT_LENGTH', 0))))
except:
    data = {}

sample_no = data.get('sample_no')
enquiry_no = data.get('enquiry_no')
sample_quantity = data.get('sample_quantity')
sample_status = data.get('sample_status')
dispatch_date = data.get('dispatch_date')
courier = data.get('courier')
tracking_number = data.get('tracking_number')
remarks = data.get('remarks')

customer_name = None
contact_person = None
fabric_type = None
fabric_gsm = None
color = None

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Fetch details from enquiry
    if enquiry_no:
        cursor.execute("""
            SELECT 
                customer_id AS customer_name,
                contact_person,
                fabric_type,
                fabric_gsm,
                color
            FROM enquiries 
            WHERE enquiry_no = %s
        """, (enquiry_no,))
        row = cursor.fetchone()
        if row:
            customer_name = row['customer_name']
            contact_person = row['contact_person']
            fabric_type = row['fabric_type']
            fabric_gsm = row['fabric_gsm']
            color = row['color']

    # Insert into samples
    sql = """
    INSERT INTO samples (
        sample_no, 
        enquiry_no, 
        customer_name, 
        contact_person,
        fabric_type, 
        fabric_gsm, 
        color,
        sample_quantity, 
        sample_status, 
        dispatch_date, 
        courier, 
        tracking_number, 
        remarks
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (
        sample_no, enquiry_no, customer_name, contact_person,
        fabric_type, fabric_gsm, color,
        sample_quantity, sample_status, dispatch_date,
        courier, tracking_number, remarks
    ))

    conn.commit()
    print(json.dumps({"success": True, "message": "Sample saved successfully!"}))

except Exception as e:
    print(json.dumps({"success": False, "message": str(e)}))
finally:
    if 'conn' in locals():
        conn.close()
