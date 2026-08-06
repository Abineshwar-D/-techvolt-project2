#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe
import cgi
import pymysql
import cgitb

cgitb.enable()
print("Content-Type: text/plain\n")  # Sending simple text

form = cgi.FieldStorage()
enq_id = form.getvalue("enquiry_id")

if not enq_id:
    print("Error: Missing enquiry_id parameter")
    exit()

try:
    db = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = db.cursor()

    # Get the row for this customer
    cursor.execute("SELECT * FROM customers_enquiries WHERE enquiry_id = %s", (enq_id,))
    row = cursor.fetchone()

    if row:
        # --- CALCULATIONS ---
        base_price = 20.0
        color_p = float(row['price']) if row.get('price') else 0.0
        gsm_p = (float(row['fabric_gsm']) * 0.5) if row.get('fabric_gsm') else 0.0
        unit_price = round(base_price + color_p + gsm_p, 2)

        qty = float(row['quantity']) if row.get('quantity') else 0.0

        o_date = row['created_at'].strftime('%Y-%m-%d') if row.get('created_at') else ""

        # Handle delivery_date properly if it's a date/datetime object
        d_date = row['delivery_date'] if row.get('delivery_date') else ""
        if hasattr(d_date, 'strftime'):
            d_date = d_date.strftime('%Y-%m-%d')

        # --- BUILD PIPE STRING ---
        # JS expects:
        # p[0]  = contact
        # p[1]  = fabric
        # p[2]  = gsm
        # p[3]  = color
        # p[4]  = qty
        # p[5]  = price
        # p[6]  = percentage
        # p[7]  = (Unused placeholder / extra field)
        # p[8]  = order_date
        # p[9]  = delivery_date
        # p[10] = customerId (enquiry_id)

        data_string = (
            f"{row.get('phone_number', '')}|"  # p[0]
            f"{row.get('fabric_type', '')}|"  # p[1]
            f"{row.get('fabric_gsm', '')}|"  # p[2]
            f"{row.get('color', '')}|"  # p[3]
            f"{qty}|"  # p[4]
            f"{unit_price}|"  # p[5]
            f"50|"  # p[6]
            f"0|"  # p[7] (Placeholder for index alignment)
            f"{o_date}|"  # p[8]
            f"{d_date}|"  # p[9]
            f"{row.get('enquiry_id', '')}"  # p[10]
        )
        print(data_string)
    else:
        print("Error: No data found for given enquiry_id")

except Exception as e:
    print(f"Error: {str(e)}")
finally:
    if 'db' in locals():
        db.close()