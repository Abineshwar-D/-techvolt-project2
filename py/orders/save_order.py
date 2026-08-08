#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import re
import sys
from datetime import datetime
import pymysql

# Enable CGI debug tracking
cgitb.enable()

# Output HTTP header
print("Content-Type: text/html\n\n")

form = cgi.FieldStorage()

# READ LOGGED-IN USER ID PASSED FROM FORM
logged_in_user_id = form.getvalue("user_id") or form.getvalue("admin_id")
if logged_in_user_id:
    logged_in_user_id = str(logged_in_user_id).strip()

# Database Config Settings
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "techvoltproject2"
}

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

# DYNAMIC REDIRECT URL GENERATION
if logged_in_user_id:
    redirect_url = f"/techvoltInstituteProject/pages/marketing.html?user_id={logged_in_user_id}#page3"
else:
    redirect_url = "/techvoltInstituteProject/pages/login.html"


# ==================== VALIDATION ====================

def validate():
    errors = []
    required = {
        "customer": "Customer",
        "contact": "Contact",
        "fabric_type": "Fabric Type",
        "gsm": "GSM",
        "color": "Color",
        "quantity": "Quantity",
        "price": "Price",
        "percentage": "Payment Percentage",
        "delivery_date": "Delivery Date",
        "money": "Money Transition",
    }

    for field, label in required.items():
        value = form.getvalue(field)
        if value is None or str(value).strip() == "":
            errors.append(f"{label} is required")

    if errors:
        return errors

    # Phone validation
    contact = str(form.getvalue("contact", "")).strip()
    if not re.match(r"^[6-9][0-9]{9}$", contact):
        errors.append("Contact must be a 10-digit number starting with 6-9")

    return errors


validation_errors = validate()

if validation_errors:
    error_msg = "\\n".join([f"• {err}" for err in validation_errors])
    print(f"""
    <script>
        alert("Validation Errors:\\n\\n{error_msg}");
        window.history.back();
    </script>
    """)
    sys.exit()

# ==================== DATABASE OPERATION ====================

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 1. CAPTURE FORM DATA
    customer = form.getvalue("customer")
    contact = form.getvalue("contact")
    fabric_type = form.getvalue("fabric_type")
    gsm = int(float(form.getvalue("gsm") or 0))
    color = form.getvalue("color")
    quantity = float(form.getvalue("quantity") or 0)
    price = float(form.getvalue("price") or 0)

    base_amount = quantity * price

    # Calculate 18% GST
    gst_amount = base_amount * 0.18  # 18% GST

    # Calculate Total Amount including GST
    total_amount = base_amount + gst_amount

    # AUTO-SET ORDER DATE TO TODAY
    order_date = datetime.now().strftime("%Y-%m-%d")

    delivery_date = form.getvalue("delivery_date")
    remarks = form.getvalue("remarks")
    payment_percentage = form.getvalue("percentage")
    money = form.getvalue("money")

    # DUPLICATE CUSTOMER CHECK
    cursor.execute(
        "SELECT order_number FROM orders WHERE customer = %s", (customer,)
    )
    duplicate = cursor.fetchone()

    if duplicate:
        print(f"""
        <script>
            alert("Duplicate Entry: An order ({duplicate[0]}) already exists for customer {customer}. Multiple orders for the same customer are not allowed.");
            window.history.back();
        </script>
        """)
        conn.close()
        sys.exit()

    # DATE VALIDATION
    if delivery_date <= order_date:
        print(f"""
        <script>
            alert("Date Error: Delivery Date ({delivery_date}) must be greater than Order Date ({order_date}).");
            window.history.back();
        </script>
        """)
        conn.close()
        sys.exit()

    # 2. GENERATE NEW ORDER NUMBER
    cursor.execute(
        "SELECT order_number FROM orders WHERE order_number LIKE 'ORD%' ORDER BY id DESC LIMIT 1"
    )
    row = cursor.fetchone()
    if row:
        last_no = int(re.search(r"\d+", row[0]).group())
        new_id = f"ORD{last_no + 1:04d}"
    else:
        new_id = "ORD0001"

    # 3. SQL INSERT INCLUDING CREATED BY DETAILS
    sql = """
    INSERT INTO orders (
        order_number, customer, contact, fabric_type, gsm, color, 
        quantity, price_per_kg, total_amount, order_date, 
        delivery_date, remarks, payment_percentage, money,
        created_by_id, created_by_name
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        new_id,
        customer,
        contact,
        fabric_type,
        gsm,
        color,
        quantity,
        price,
        total_amount,
        order_date,
        delivery_date,
        remarks,
        payment_percentage,
        money,
        logged_in_user_id,
        creator_name
    )

    cursor.execute(sql, values)
    conn.commit()
    conn.close()

    # 4. RESPONSE REDIRECT
    if not logged_in_user_id:
        print("""
        <script>
            alert("Order saved, but session parameter was missing. Redirecting to login.");
            window.location.href = "/techvoltInstituteProject/pages/login.html";
        </script>
        """)
    else:
        print(f"""
        <script>
            alert("Order {new_id} saved successfully!");
            window.location.href = "{redirect_url}";
        </script>
        """)

except Exception as e:
    error_detail = str(e).replace('"', "'")
    print(f"""
    <script>
        alert("Database Error: {error_detail}");
        window.history.back();
    </script>
    """)
finally:
    if "conn" in locals() and conn.open:
        conn.close()