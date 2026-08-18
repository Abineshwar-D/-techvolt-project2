#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import json
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import pymysql

# Disable HTML error dumps so it doesn't break JavaScript's response.json()
cgitb.enable(display=0, logdir=None)

# Send CGI Header
print("Content-Type: application/json\n")

form = cgi.FieldStorage()

# READ LOGGED-IN USER ID PASSED FROM FORM
logged_in_user_id = form.getvalue("user_id") or form.getvalue("admin_id")
if logged_in_user_id:
    logged_in_user_id = str(logged_in_user_id).strip()

# DB Config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "techvoltproject2",
    "charset": "utf8mb4"
}

# SMTP Configuration for sending email
SMTP_CONFIG = {
    "server": "smtp.gmail.com",
    "port": 587,
    "sender_email": "abineshwar68@gmail.com",      # <--- Sender email
    "sender_password": "orsswjpkbkubbmqk"          # <--- App Password
}

# Resolve Creator Full Name based on user_id (Check users table first, then admin table)
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

# DYNAMIC REDIRECT URL GENERATION
if logged_in_user_id:
    redirect_url = f"/techvoltInstituteProject/pages/production.html?user_id={logged_in_user_id}#page7"
else:
    redirect_url = "/techvoltInstituteProject/pages/login.html"

# CAPTURE FORM DATA
orderSelect = form.getvalue("orderSelect")
customer = form.getvalue("customer")
fabric = form.getvalue("fabric")
orderQty_raw = form.getvalue("orderQty") or "0"

orderQty_str = str(orderQty_raw).replace("Kg", "").strip()

try:
    orderQty_val = int(float(orderQty_str))
except ValueError:
    orderQty_val = 0

# AUTOMATICALLY CALCULATE PRODUCTION TARGET = ORDER QUANTITY + 5
target_val = orderQty_val + 5

# AUTOMATICALLY SET START DATE TO TODAY'S DATE (YYYY-MM-DD)
start = datetime.now().strftime("%Y-%m-%d")

# CAPTURE DELIVERY DATE FROM FORM
delivery_date_raw = form.getvalue("delivery_date")

# CALCULATE END DATE = DELIVERY DATE - 3 DAYS
end = ""
if delivery_date_raw and str(delivery_date_raw).strip():
    try:
        delivery_dt = datetime.strptime(str(delivery_date_raw).strip(), "%Y-%m-%d")
        end_dt = delivery_dt - timedelta(days=3)
        end = end_dt.strftime("%Y-%m-%d")
    except ValueError:
        end = ""

machine = form.getvalue("machine")
supervisor = form.getvalue("supervisor")
remarks = form.getvalue("remarks") or ""

# FORM VALIDATION
errors = []

if not orderSelect or str(orderSelect).strip() == "":
    errors.append("Order Number is required.")

if not customer or str(customer).strip() == "":
    errors.append("Customer is required.")

if not fabric or str(fabric).strip() == "":
    errors.append("Fabric Type is required.")

if orderQty_val <= 0:
    errors.append("Order Quantity must be greater than zero.")

if not delivery_date_raw or str(delivery_date_raw).strip() == "":
    errors.append("Delivery Date is required.")
elif not end:
    errors.append("Invalid Delivery Date format. Expected YYYY-MM-DD.")
elif end < start:
    errors.append(f"Calculated End Date ({end}) cannot be earlier than Today's Start Date ({start}).")

if not machine or str(machine).strip() == "" or machine.lower() == "select machine":
    errors.append("Machine selection is required.")

if not supervisor or str(supervisor).strip() == "" or supervisor.lower() == "select supervisor":
    errors.append("Supervisor selection is required.")

if errors:
    print(json.dumps({
        "status": "error",
        "errors": errors
    }))
    sys.exit()

# ==================== DATABASE OPERATION ====================

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 1. FETCH COLOR VALUE FROM ORDERS TABLE USING ORDER NUMBER
    color_val = "N/A"
    cursor.execute("SELECT color FROM orders WHERE order_number = %s", (orderSelect,))
    color_row = cursor.fetchone()
    if color_row and color_row[0]:
        color_val = color_row[0].strip()

    # 2. FETCH SUPERVISOR DETAILS FROM SUPERVISOR TABLE
    sup_email = ""
    sup_phone = "N/A"
    sup_code = "N/A"

    cursor.execute("""
        SELECT Supervisor_email, Supervisor_phone, Supervisor_code 
        FROM Supervisor 
        WHERE LOWER(TRIM(Supervisor_name)) = LOWER(TRIM(%s))
    """, (supervisor,))
    sup_row = cursor.fetchone()

    if sup_row:
        sup_email = (sup_row[0] or "").strip()
        sup_phone = (sup_row[1] or "N/A").strip()
        sup_code = (sup_row[2] or "N/A").strip()

    # 3. Generate Plan Number (e.g. PLAN001, PLAN002)
    cursor.execute("""
        SELECT plan_no
        FROM production_plan
        ORDER BY plan_no DESC
        LIMIT 1
    """)
    row = cursor.fetchone()

    if row and row[0]:
        num = int(row[0].replace("PLAN", ""))
        newplan = f"PLAN{num + 1:03d}"
    else:
        newplan = "PLAN001"

    # 4. Insert SQL into production_plan table
    cursor.execute(
        """
        INSERT INTO production_plan (
            plan_no, order_no, customer_name, fabric_type, color,
            production_target, order_quantity, start_date, 
            end_date, machine, supervisor, remarks,
            created_by_id, created_by_name
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
        (
            newplan,
            orderSelect,
            customer,
            fabric,
            color_val,
            target_val,
            orderQty_val,
            start,
            end,
            machine,
            supervisor,
            remarks,
            logged_in_user_id,
            creator_name
        ),
    )

    conn.commit()
    cursor.close()
    conn.close()

    # ==================== EMAIL SENDING LOGIC ====================
    email_sent = False
    email_error_msg = ""

    if not sup_email or "@" not in sup_email:
        email_error_msg = f" (Warning: No email registered for supervisor '{supervisor}')"
    else:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Production Order Assignment - {newplan}"
            msg["From"] = f"KnitPro ERP <{SMTP_CONFIG['sender_email']}>"
            msg["To"] = sup_email

            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; background-color: #f9f9f9; padding: 20px; }}
                    .container {{ max-width: 650px; margin: 0 auto; background: #ffffff; padding: 25px; border-radius: 8px; border: 1px solid #e0e0e0; }}
                    .header {{ text-align: center; border-bottom: 2px solid #2b579a; padding-bottom: 10px; margin-bottom: 20px; }}
                    .header h2 {{ color: #2b579a; margin: 0; text-transform: uppercase; }}
                    .message-body {{ background: #fff8e7; padding: 15px; border-left: 4px solid #f39c12; margin-bottom: 20px; font-size: 0.95rem; border-radius: 4px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.88rem; }}
                    th, td {{ border: 1px solid #dddddd; text-align: center; padding: 8px; }}
                    th {{ background-color: #2b579a; color: white; }}
                    .footer {{ margin-top: 30px; border-top: 1px solid #eee; pt: 15px; text-align: right; font-style: italic; color: #555; }}
                    .footer-brand {{ font-weight: bold; color: #2b579a; font-size: 1rem; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Production Order</h2>
                    </div>

                    <table style="border:none; margin-bottom:20px; text-align:left;">
                        <tr style="border:none;">
                            <td style="border:none; width:50%; vertical-align:top; text-align:left;">
                                <strong style="color:#2b579a;">From:</strong><br>
                                <strong>Company:</strong> KnitPro ERP<br>
                                <strong>Assigned Person:</strong> {creator_name}
                            </td>
                            <td style="border:none; width:50%; vertical-align:top; text-align:left;">
                                <strong style="color:#2b579a;">To:</strong><br>
                                <strong>Supervisor:</strong> {supervisor}<br>
                                <strong>Phone:</strong> {sup_phone}<br>
                                <strong>Email:</strong> {sup_email}<br>
                                <strong>ID:</strong> {sup_code}
                            </td>
                        </tr>
                    </table>

                    <div class="message-body">
                        Hello <strong>{supervisor}</strong>,<br><br>
                        You are required to start this production order on <strong>{start}</strong> and complete it by <strong>{end}</strong>.<br><br>
                        You will be using the <strong>{machine}</strong> machine, with a production target of <strong>{target_val} Kg</strong>.<br><br>
                        The production will use <strong>{fabric}</strong> fabric in <strong>{color_val}</strong>.<br><br>
                        This production order has been assigned to you by <strong>{creator_name}</strong>.<br><br>
                        Please ensure that the production is completed within the specified time period.<br><br>
                        Thank you.
                    </div>

                    <h3>Order Summary</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Production No</th>
                                <th>Order No</th>
                                <th>Fabric Type</th>
                                <th>Color</th>
                                <th>Production Target</th>
                                <th>Start Date</th>
                                <th>End Date</th>
                                <th>Machine</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{newplan}</td>
                                <td>{orderSelect}</td>
                                <td>{fabric}</td>
                                <td>{color_val}</td>
                                <td>{target_val} Kg</td>
                                <td>{start}</td>
                                <td>{end}</td>
                                <td>{machine}</td>
                            </tr>
                        </tbody>
                    </table>

                    <div class="footer">
                        <br>
                        <span class="footer-brand">By: KnitPro ERP</span><br>
                        <small>⚡ Smart Textile Manufacturing Solution</small>
                    </div>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(html_content, "html"))

            # Send Email via SMTP
            server = smtplib.SMTP(SMTP_CONFIG["server"], SMTP_CONFIG["port"], timeout=10)
            server.starttls()
            server.login(SMTP_CONFIG["sender_email"], SMTP_CONFIG["sender_password"])
            server.sendmail(SMTP_CONFIG["sender_email"], sup_email, msg.as_string())
            server.quit()
            email_sent = True

        except Exception as email_err:
            email_sent = False
            email_error_msg = f" (Email Error: {str(email_err)})"

    # Build Response Message
    msg_status = f"Plan {newplan} saved successfully!"
    if email_sent:
        msg_status += f" Email sent to {supervisor} ({sup_email})."
    else:
        msg_status += email_error_msg

    print(json.dumps({
        "status": "success",
        "message": msg_status,
        "redirect_url": redirect_url
    }))

except Exception as e:
    error_detail = str(e).replace('"', "'")
    print(json.dumps({
        "status": "error",
        "errors": [f"Database Error: {error_detail}"]
    }))