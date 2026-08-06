#!C:\Users\Abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import pymysql
import re

cgitb.enable()

# Output HTTP header (Requires double newline \n\n)
print("Content-Type: text/html\n\n")

form = cgi.FieldStorage()

# 1. Read logged-in user ID passed from the hidden form field
logged_in_user_id = (form.getvalue("admin_id") or form.getvalue("user_id") or "").strip()

# Database Connection Settings
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "techvoltproject2"
}

# Role-to-Page mapping matching your auth.py configuration
ROLE_PAGES = {
    "merchandising": "Merchandising.html",
    "marketing": "Marketing.html",
    "production": "Production.html",
    "storekeeper": "StoreKeeper.html"
}

# 2. Dynamic Redirect URL logic based on Database Role & Creator Name Resolution
redirect_url = "/techvoltInstituteProject/pages/login.html"
creator_name = "System User"

if logged_in_user_id:
    try:
        conn_check = pymysql.connect(**DB_CONFIG)
        cur_check = conn_check.cursor()

        # Step A: Check 'users' table FIRST for role and fullname
        cur_check.execute("SELECT role, fullname FROM users WHERE employee_id=%s", (logged_in_user_id,))
        user_row = cur_check.fetchone()

        if user_row:
            user_role = (user_row[0] or "").strip().lower()
            creator_name = user_row[1] or logged_in_user_id
            matched_page = ROLE_PAGES.get(user_role, "login.html")
            redirect_url = f"/techvoltInstituteProject/pages/{matched_page}?user_id={logged_in_user_id}#page4"
        else:
            # Step B: Check 'admin' table if user is NOT in 'users' table
            cur_check.execute("SELECT employee_id, fullname FROM admin WHERE employee_id=%s", (logged_in_user_id,))
            admin_row = cur_check.fetchone()

            if admin_row:
                creator_name = "Admin"
                redirect_url = f"/techvoltInstituteProject/pages/admin_dashboard.html?user_id={logged_in_user_id}#page4"
            else:
                redirect_url = "/techvoltInstituteProject/pages/login.html"

        cur_check.close()
        conn_check.close()
    except Exception as e:
        redirect_url = "/techvoltInstituteProject/pages/login.html"

# ==================== VALIDATION ====================

def validate():
    errors = []

    # Required fields check
    required = {
        "supplier_name": "Supplier name",
        "contact_person": "Contact person",
        "phone": "Phone number",
        "email": "Email",
        "address": "Address",
        "city": "City",
        "state": "State",
        "pincode": "Pincode",
        "material": "Material supplied",
        "status": "Status"
    }

    for field, label in required.items():
        value = form.getvalue(field)
        if not value or str(value).strip() == "":
            errors.append(f"{label} is required")

    if errors:
        return errors

    # Supplier name validation
    supplier_name = form.getvalue("supplier_name", "").strip()
    if len(supplier_name) < 2 or len(supplier_name) > 100:
        errors.append("Supplier name must be between 2 and 100 characters")

    # Contact person validation
    contact_person = form.getvalue("contact_person", "").strip()
    if len(contact_person) < 2:
        errors.append("Contact person name must be at least 2 characters")

    # Phone validation (Valid 10-digit Indian Mobile: starts with 6-9)
    phone = form.getvalue("phone", "").strip()
    phone_digits = re.sub(r'\D', '', phone)
    if not re.match(r'^[6-9]\d{9}$', phone_digits):
        errors.append("Please enter a valid 10-digit mobile number starting with 6, 7, 8, or 9")

    # Email validation
    email = form.getvalue("email", "").strip()
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        errors.append("Please enter a valid email address")

    # GST number validation (15-character standard format)
    gst_number = form.getvalue("gst_number", "").strip().upper()
    if gst_number:
        gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(gst_pattern, gst_number):
            errors.append("GST number format is invalid (e.g., 33AAAAA0000A1Z5)")

    # Address validation
    address = form.getvalue("address", "").strip()
    if len(address) < 5 or len(address) > 250:
        errors.append("Address must be between 5 and 250 characters")

    # City & State validation
    city = form.getvalue("city", "").strip()
    if len(city) < 2 or not re.match(r'^[a-zA-Z\s\-]+$', city):
        errors.append("City name can only contain letters, spaces, and hyphens")

    state = form.getvalue("state", "").strip()
    if len(state) < 2:
        errors.append("State name must be at least 2 characters")

    # Pincode validation (6 digits, cannot start with 0)
    pincode = form.getvalue("pincode", "").strip()
    if not re.match(r'^[1-9][0-9]{5}$', pincode):
        errors.append("Please enter a valid 6-digit Indian Pincode")

    # Material validation
    material = form.getvalue("material", "").strip()
    if len(material) < 2:
        errors.append("Material supplied must be at least 2 characters")

    # Status validation
    status = form.getvalue("status", "").strip().capitalize()
    valid_status = ["Active", "Inactive", "Pending", "Blocked"]
    if status not in valid_status:
        errors.append(f"Status must be one of: {', '.join(valid_status)}")

    return errors


validation_errors = validate()

if validation_errors:
    error_msg = "\\n".join([f"• {err}" for err in validation_errors])
    print(f"""
    <script>
        alert("Please fix the following errors:\\n\\n{error_msg}");
        window.history.back();
    </script>
    """)
    exit()

# Extract sanitized values
supplier_name = form.getvalue("supplier_name", "").strip()
contact_person = form.getvalue("contact_person", "").strip()
phone = re.sub(r'\D', '', form.getvalue("phone", "").strip())
email = form.getvalue("email", "").strip().lower()
gst_number = form.getvalue("gst_number", "").strip().upper()
address = form.getvalue("address", "").strip()
city = form.getvalue("city", "").strip()
state = form.getvalue("state", "").strip()
pincode = form.getvalue("pincode", "").strip()
material = form.getvalue("material", "").strip()
status = form.getvalue("status", "").strip().capitalize()

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Check for duplicate email, phone, or GST number
    check_sql = """
        SELECT email, phone, gst_number, supplier_name FROM supplier 
        WHERE email = %s OR phone = %s OR (gst_number = %s AND gst_number != '') OR supplier_name = %s
    """
    cursor.execute(check_sql, (email, phone, gst_number, supplier_name))
    existing = cursor.fetchone()

    if existing:
        print("""
        <script>
            alert("Error: A supplier with this Phone Number, Email, Supplier Name or GST Number already exists!");
            window.history.back();
        </script>
        """)
        exit()

    # Generate next Supplier Code safely using numeric length check
    cursor.execute("""
        SELECT supplier_code 
        FROM supplier 
        ORDER BY LENGTH(supplier_code) DESC, supplier_code DESC 
        LIMIT 1
    """)
    row = cursor.fetchone()

    if row and row[0].startswith("SUP"):
        try:
            last_no = int(row[0][3:])
            supplier_code = f"SUP{last_no + 1:04d}"
        except ValueError:
            supplier_code = "SUP0001"
    else:
        supplier_code = "SUP0001"

    # Insert Supplier Record including created_by tracking details
    insert_sql = """
        INSERT INTO supplier (
            supplier_code, supplier_name, contact_person, phone, 
            email, gst_number, address, city, state, pincode, 
            material_supplied, status, created_by_id, created_by_name
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_sql, (
        supplier_code, supplier_name, contact_person, phone,
        email, gst_number, address, city, state, pincode,
        material, status, logged_in_user_id, creator_name
    ))

    conn.commit()

    # JS redirect sending the user back to THEIR assigned page
    if not logged_in_user_id:
        print("""
        <script>
            alert("Supplier saved successfully, but session ID was missing. Redirecting to login.");
            window.location.href = "/techvoltInstituteProject/pages/login.html";
        </script>
        """)
    else:
        print(f"""
        <script>
            alert("Supplier saved successfully!");
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
    if 'conn' in locals() and conn.open:
        cursor.close()
        conn.close()