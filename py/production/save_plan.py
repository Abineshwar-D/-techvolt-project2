#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import json
import sys
from datetime import datetime
import pymysql

cgitb.enable()

print("Content-Type: application/json\n\n")

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
    "database": "techvoltproject2"
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

end = form.getvalue("end_date")
machine = form.getvalue("machine")
supervisor = form.getvalue("supervisor")
remarks = form.getvalue("remarks") or ""

# VALIDATION
errors = []

if not orderSelect or str(orderSelect).strip() == "":
    errors.append("Order Number is required.")

if not customer or str(customer).strip() == "":
    errors.append("Customer is required.")

if not fabric or str(fabric).strip() == "":
    errors.append("Fabric Type is required.")

if orderQty_val <= 0:
    errors.append("Order Quantity must be greater than zero.")

if not end or str(end).strip() == "":
    errors.append("End Date is required.")
elif end < start:
    errors.append(f"End Date ({end}) cannot be earlier than Today's Start Date ({start}).")

if (
    not machine
    or str(machine).strip() == ""
    or machine.lower() == "select machine"
):
    errors.append("Machine selection is required.")

if (
    not supervisor
    or str(supervisor).strip() == ""
    or supervisor.lower() == "select supervisor"
):
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

    # Generate Plan Number (e.g. PLAN001, PLAN002)
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

    # Insert SQL including created_by_id and created_by_name
    cursor.execute(
        """
        INSERT INTO production_plan (
            plan_no, order_no, customer_name, fabric_type, 
            production_target, order_quantity, start_date, 
            end_date, machine, supervisor, remarks,
            created_by_id, created_by_name
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
        (
            newplan,
            orderSelect,
            customer,
            fabric,
            target_val,  # Automatically set to Order Qty + 5
            orderQty_val,
            start,       # Today's date (e.g. 2026-08-03)
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

    # Response Redirect
    if not logged_in_user_id:
        print(json.dumps({
            "status": "success",
            "message": "Plan saved, but session parameter was missing. Redirecting to login.",
            "redirect_url": "/techvoltInstituteProject/pages/login.html"
        }))
    else:
        print(json.dumps({
            "status": "success",
            "message": f"Plan {newplan} saved successfully with Start Date: {start}!",
            "redirect_url": redirect_url
        }))

except Exception as e:
    error_detail = str(e).replace('"', "'")
    print(json.dumps({
        "status": "error",
        "errors": [f"Database Error: {error_detail}"]
    }))