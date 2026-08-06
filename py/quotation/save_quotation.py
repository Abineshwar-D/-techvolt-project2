#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import pymysql
import cgi
import cgitb

cgitb.enable()

print("Content-Type: text/html\n")

form = cgi.FieldStorage()

quotationNumber = form.getvalue("quotationNumber")
sampleNumber = form.getvalue("sampleNumber")
customerName = form.getvalue("customerName")
contactPerson = form.getvalue("contactPerson")
fabricType = form.getvalue("fabricType")
fabricGsm = form.getvalue("fabricGsm")
fabricColor = form.getvalue("fabricColor")
requiredQuantity = form.getvalue("requiredQuantity")
pricePerKg = form.getvalue("pricePerKg")
totalAmount1 = form.getvalue("totalAmount")
validUntil = form.getvalue("validUntil")
paymentTerms = form.getvalue("paymentTerms")
deliveryDays = form.getvalue("deliveryDays")
quotationRemarks = form.getvalue("quotationRemarks")

con = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="techvoltproject2"
)

cur = con.cursor()
quotationstatus = [
    "send"
]
cur.execute("""
    SELECT quotation_number
    FROM quotation
    WHERE quotation_number LIKE %s
    ORDER BY quotation_number DESC
    LIMIT 1
""", ("QT%",))

row = cur.fetchone()

if row:
    last_no = int(row[0][3:])
    new_id = f"{'QT'}{last_no + 1:04d}"
else:
    new_id = f"{'QT'}0001"

cur.execute("""
        INSERT INTO quotation 
        (quotation_number, sample_number, customer_name, contact_person, fabric_type, fabric_gsm, fabric_color, 
        required_quantity,price_per_kg,total_amount,valid_until,payment_terms,delivery_days,quotation_status,remarks)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        new_id,
        sampleNumber,
        customerName,
        contactPerson,
        fabricType,
        fabricGsm,
        fabricColor,
        requiredQuantity,
        pricePerKg,
        totalAmount1,
        validUntil,
        paymentTerms,
        deliveryDays,
        quotationstatus[0],
        quotationRemarks
    ))

con.commit()
con.close()

print(f"""
<script>
    alert("Saved successfully! ");
    window.location.href="/techvoltInstituteProject/pages/merchandising.html";
</script>
""")