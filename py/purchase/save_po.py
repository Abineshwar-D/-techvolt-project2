#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import json
import pymysql
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

cgitb.enable()

# Output JSON header for fetch()
print("Content-Type: application/json\n\n")

# ---------------------------------------------------------
# EMAIL & COMPANY CONFIGURATION
# ---------------------------------------------------------
SENDER_EMAIL = "abineshwar68@gmail.com"
SENDER_PASSWORD = "orsswjpkbkubbmqk".replace(" ", "")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

COMPANY_NAME = "Techvolt"
COMPANY_EMAIL = "techvolt@gmail.com"
COMPANY_PHONE = "06384930973"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "techvoltproject2"
}
# ---------------------------------------------------------

form = cgi.FieldStorage()

# Extract user_id from form submission
logged_in_user_id = (form.getvalue("user_id") or form.getvalue("admin_id") or "").strip()

# Resolve Creator Full Name based on user_id (First check users table, then admin table)
creator_name = "System User"
if logged_in_user_id:
    try:
        conn_check = pymysql.connect(**DB_CONFIG)
        cur_check = conn_check.cursor()

        # Step A: Check 'users' table FIRST
        cur_check.execute("SELECT fullname FROM users WHERE employee_id=%s", (logged_in_user_id,))
        u_row = cur_check.fetchone()

        if u_row and u_row[0]:
            creator_name = u_row[0].strip()
        else:
            # Step B: Check 'admin' table if not found in 'users'
            cur_check.execute("SELECT fullname FROM admin WHERE employee_id=%s", (logged_in_user_id,))
            a_row = cur_check.fetchone()
            if a_row and a_row[0]:
                creator_name = a_row[0].strip()
            elif a_row:
                creator_name = "Admin"

        cur_check.close()
        conn_check.close()
    except Exception:
        pass


# Helper function: Convert values to float safely
def parse_float(value, default=0.0):
    if value is None:
        return default
    try:
        clean_val = str(value).strip().replace("₹", "").replace(",", "")
        return float(clean_val) if clean_val else default
    except (ValueError, TypeError):
        return default


# 1. READ FORM DATA
supplier = form.getvalue("supplier_name", "").strip() # Holds Supplier Code / ID like SUP0001
material = form.getvalue("material_name", "").strip()
available_stock = parse_float(form.getvalue("available_stock"), 0.0)
required_qty = parse_float(form.getvalue("required_qty"), 0.0)
expected_delivery = form.getvalue("expected_delivery", "").strip()
remarks = form.getvalue("remarks", "").strip()
status = "NEW PO"


# 2. VALIDATION
errors = []
if not supplier or supplier == "Select Supplier":
    errors.append("Please select a supplier.")
if not material or material == "Select Material":
    errors.append("Please select a material.")
if required_qty <= 0:
    errors.append("Required quantity must be greater than 0.")
if not expected_delivery:
    errors.append("Expected delivery date is required.")

if errors:
    error_text = "Validation Errors: " + ", ".join(errors)
    print(json.dumps({"success": False, "message": error_text}))
    exit()


# 3. DATABASE OPERATIONS & EMAIL SENDING
try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Fetch Supplier Details AND Supplier Name specifically using Supplier ID/Code
    sup_contact_person = "N/A"
    sup_shop_name = "N/A"
    supplier_name_val = ""
    sup_address = "N/A"
    sup_phone = "N/A"
    sup_email = ""

    cursor.execute("""
        SELECT supplier_name, contact_person, address, city, state, pincode, phone, email 
        FROM supplier 
        WHERE LOWER(TRIM(supplier_code)) = LOWER(TRIM(%s)) 
           OR LOWER(TRIM(supplier_name)) = LOWER(TRIM(%s)) 
        LIMIT 1
    """, (supplier, supplier))
    sup_row = cursor.fetchone()

    if sup_row:
        supplier_name_val = sup_row[0] or ""   # Fetches 'ABC Yarns Pvt Ltd'
        sup_contact_person = sup_row[1] or supplier_name_val
        sup_shop_name = supplier_name_val
        addr_parts = [p for p in [sup_row[2], sup_row[3], sup_row[4], sup_row[5]] if p]
        sup_address = ", ".join(addr_parts) if addr_parts else "N/A"
        sup_phone = sup_row[6] or "N/A"
        sup_email = sup_row[7] or ""

    # Generate next PO Number
    cursor.execute("""
        SELECT po_number 
        FROM purchased_order 
        ORDER BY id DESC 
        LIMIT 1
    """)
    last_po = cursor.fetchone()

    if last_po and last_po[0]:
        try:
            last_num = int(str(last_po[0]).replace("PO", ""))
            po_number = f"PO{last_num + 1:04d}"
        except ValueError:
            po_number = "PO0001"
    else:
        po_number = "PO0001"

    # Insert including supplier_name fetched from supplier table
    sql = """
        INSERT INTO purchased_order (
            po_number, supplier, supplier_name, material,
            available_stock, required_qty,
            expected_delivery, remarks, status,
            created_by_id, created_by_name
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        po_number, supplier, supplier_name_val, material,
        available_stock, required_qty,
        expected_delivery, remarks, status,
        logged_in_user_id, creator_name
    )

    cursor.execute(sql, values)
    conn.commit()

    cursor.close()
    conn.close()

    # ---------------------------------------------------------
    # SEND EMAIL TO SUPPLIER
    # ---------------------------------------------------------
    email_status_msg = ""
    if sup_email:
        try:
            remarks_html = f"<div style='margin-top: 20px; padding-top: 10px; border-top: 1px solid " \
                           f"#eee;'><p><strong>Remarks / Special Instructions:</strong> {remarks}</p></div>" if \
                remarks else ""

            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
                <div style="max-width: 700px; margin: auto; background: #ffffff; border: 1px solid #ddd; padding: 25px; border-radius: 8px;">
                    <h2 style="text-align: center; color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px;">
                        PURCHASE ORDER ({po_number})
                    </h2>

                    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse; margin-top: 15px;">
                        <tr>
                            <td width="50%" valign="top" style="border-right: 2px solid #333; padding-right: 15px;">
                                <p style="margin: 8px 0;"><strong>Name :</strong> {sup_contact_person}</p>
                                <p style="margin: 8px 0;"><strong>Shop Name :</strong> {sup_shop_name}</p>
                                <p style="margin: 8px 0;"><strong>Address :</strong> {sup_address}</p>
                                <p style="margin: 8px 0;"><strong>Phone :</strong> {sup_phone}</p>
                                <p style="margin: 8px 0;"><strong>Email :</strong> {sup_email}</p>
                            </td>

                            <td width="50%" valign="top" style="padding-left: 15px;">
                                <h3 style="margin-top: 0; color: #2c3e50;">Company details</h3>
                                <p style="margin: 8px 0;"><strong>Company Name :</strong> {COMPANY_NAME}</p>
                                <p style="margin: 8px 0;"><strong>Material :</strong> {material}</p>
                                <p style="margin: 8px 0;"><strong>Quantity :</strong> {required_qty} Kg</p>
                                <p style="margin: 8px 0;"><strong>Delivery date :</strong> {expected_delivery}</p>
                                <p style="margin: 8px 0;"><strong>Email :</strong> {COMPANY_EMAIL}</p>
                                <p style="margin: 8px 0;"><strong>Phone :</strong> {COMPANY_PHONE}</p>
                            </td>
                        </tr>
                    </table>

                    {remarks_html}
                </div>
            </body>
            </html>
            """

            recipients = [sup_email]
            if SENDER_EMAIL and SENDER_EMAIL not in recipients:
                recipients.append(SENDER_EMAIL)

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"New Purchase Order Request - {po_number}"
            msg["From"] = SENDER_EMAIL
            msg["To"] = sup_email
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, recipients, msg.as_string())

            email_status_msg = f" & Email sent successfully to {sup_email}!"
        except Exception as mail_err:
            email_status_msg = f" (Email failed: {str(mail_err)})"
    else:
        email_status_msg = f" (No email found in supplier table for {supplier})."

    print(json.dumps({
        "success": True,
        "message": f"Purchase Order {po_number} saved successfully!{email_status_msg}"
    }))

except Exception as e:
    print(json.dumps({
        "success": False,
        "message": f"Database Error: {str(e)}"
    }))
    exit()