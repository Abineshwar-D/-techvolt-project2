#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe
import pymysql
import cgitb

cgitb.enable()
print("Content-Type: text/html\n")

try:
    db = pymysql.connect(host="localhost", user="root", password="", database="techvoltproject2")
    cursor = db.cursor()

    # Query matching enquiry_id in customers_enquiries with customer in orders
    query = """
        SELECT ce.enquiry_id, ce.customer_name 
        FROM customers_enquiries ce
        WHERE ce.sample_status = 2 
          AND ce.enquiry_id NOT IN (
              SELECT o.customer 
              FROM orders o 
              WHERE o.customer IS NOT NULL
          )
    """
    cursor.execute(query)
    results = cursor.fetchall()

    print('<option value="">-- Select Customer --</option>')
    for row in results:
        print(f'<option value="{row[0]}">{row[1]} ({row[0]})</option>')

except Exception as e:
    print(f'<option>Error: {str(e)}</option>')
finally:
    db.close()