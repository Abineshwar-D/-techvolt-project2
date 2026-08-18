#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import pymysql
from datetime import date

cgitb.enable()

print("Content-Type: text/html\n")

form = cgi.FieldStorage()

# ==================== GET FORM VALUES ====================
logged_in_user_id = form.getvalue("user_id", "").strip() or form.getvalue("admin_id", "").strip()

material_name = form.getvalue("material_name", "").strip()
category = form.getvalue("category", "").strip()
unit = form.getvalue("unit", "").strip()
opening_stock = form.getvalue("opening_stock", "").strip()
supplier = form.getvalue("supplier", "").strip()
manufacturing_date = form.getvalue("manufacturing_date", "").strip()
delivery_date = date.today().strftime("%Y-%m-%d")
status = "Stored"
purchase_order = form.getvalue("purchase_order", "").strip()
description = form.getvalue("description", "").strip()

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

# ==================== DYNAMIC REDIRECT URL ====================
if logged_in_user_id:
    redirect_url = f"/techvoltInstituteProject/pages/storekeeper.html?user_id={logged_in_user_id}#page6"
else:
    # Fallback to login if session parameter is missing
    redirect_url = "/techvoltInstituteProject/pages/login.html"

# ==================== VALIDATION ====================
errors = []

# Material Name
if not material_name:
    errors.append("Material Name is required.")
elif len(material_name) < 2:
    errors.append("Material Name must be at least 2 characters.")

# Dropdowns & Text inputs
if not category:
    errors.append("Category is required.")

if not unit:
    errors.append("Unit of Measurement is required.")

if not supplier or supplier in ["Select Supplier", "select option"]:
    errors.append("Please select a valid Supplier.")

if not manufacturing_date:
    errors.append("Manufacturing Date is required.")

# Numeric Field Safety Check for Opening Stock
if not opening_stock:
    errors.append("Opening Stock is required.")
else:
    try:
        if float(opening_stock) < 0:
            errors.append("Opening Stock cannot be negative.")
    except ValueError:
        errors.append("Opening Stock must be a valid number.")

# If validation fails, alert user and return back
if errors:
    error_msg = "\\n".join([f"• {err}" for err in errors])
    print(f"""
    <script>
        alert("Please fix the following errors:\\n\\n{error_msg}");
        window.history.back();
    </script>
    """)
    exit()

# ==================== DATABASE OPERATION ====================
try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 1. Prevent Duplicate Material Names
    check_sql = "SELECT material_id FROM materials WHERE LOWER(material_name) = LOWER(%s)"
    cursor.execute(check_sql, (material_name,))

    if cursor.fetchone():
        print("""
        <script>
            alert("Error: A material with this name already exists in inventory!");
            window.history.back();
        </script>
        """)
        exit()

    # 2. Generate Next Material Code (MAT001, MAT002...)
    cursor.execute("""
        SELECT material_code
        FROM materials
        ORDER BY material_id DESC
        LIMIT 1
    """)
    row = cursor.fetchone()

    if row and row[0].startswith("MAT"):
        try:
            last_no = int(row[0][3:])
            new_code = f"MAT{last_no + 1:03d}"
        except ValueError:
            new_code = "MAT001"
    else:
        new_code = "MAT001"

    # 3. Insert Record into SQL Database (Includes manufacturing_date)
    insert_sql = """
    INSERT INTO materials (
        po_orderid,  material_code, material_name, category, unit,
        opening_stock, supplier, manufacturing_date, delivery_date, status, description,
        created_by_id, created_by_name
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(insert_sql, (
        purchase_order, new_code, material_name, category, unit,
        opening_stock, supplier, manufacturing_date, delivery_date, status, description,
        logged_in_user_id, creator_name
    ))

    conn.commit()

    # Success Redirect with user_id attached in the URL
    print(f"""
    <script>
        alert("Material saved successfully!");
        window.location.href = "{redirect_url}";
    </script>
    """)

except Exception as e:
    print(f"""
    <script>
        alert("Database Error: {str(e)}");
        window.history.back();
    </script>
    """)

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals() and conn.open:
        conn.close()
