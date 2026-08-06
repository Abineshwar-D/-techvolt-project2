#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb

cgitb.enable()

print("Content-Type: text/html\n")

import cgi
import pymysql
import re

form = cgi.FieldStorage()

# ==================== INPUT RETRIEVAL ====================
customer_name = form.getvalue("customer_name", "").strip()
company_name = form.getvalue("company_name", "").strip()
contact_person = form.getvalue("contact_person", "").strip()
gst_number = form.getvalue("gst_number", "").strip().upper()
phone = form.getvalue("phone", "").strip()
email = form.getvalue("email", "").strip().lower()
customer_type = form.getvalue("customer_type", "").strip()

address = form.getvalue("address", "").strip()
city = form.getvalue("city", "").strip()
state = form.getvalue("state", "").strip()
pincode = form.getvalue("pincode", "").strip()

payment_terms = form.getvalue("payment_terms", "30 Days Credit").strip()
status = form.getvalue("status", "").strip()


# ==================== VALIDATION FUNCTIONS ====================

def show_alert(message):
    """Helper to print JS alert and exit"""
    print(f"""
    <script>
        alert("{message}");
        history.back();
    </script>
    """)
    exit()


def validate_required_fields():
    """Check all required fields are present"""
    required = {
        "Customer Name": customer_name,
        "Company Name": company_name,
        "Contact Person": contact_person,
        "GST Number": gst_number,
        "Phone Number": phone,
        "Email": email,
        "Customer Type": customer_type,
        "Address": address,
        "City": city,
        "State": state,
        "PIN Code": pincode,
        "Payment Terms": payment_terms,
        "Status": status
    }

    for field_name, value in required.items():
        if not value:
            show_alert(f"{field_name} is required.")


def validate_customer_name():
    """Customer name: 3-50 chars, letters and spaces only"""
    if not re.fullmatch(r"[A-Za-z ]{3,50}", customer_name):
        show_alert("Customer Name must contain only letters and spaces (3-50 characters).")


def validate_company_name():
    """Company name: 3-100 chars, letters, numbers, spaces, and common business symbols"""
    if not re.fullmatch(r"[A-Za-z0-9 &.,'-]{3,100}", company_name):
        show_alert("Company Name must be 3-100 characters (letters, numbers, spaces, &, ., -, ').")


def validate_contact_person():
    """Contact person: 3-50 chars, letters and spaces only"""
    if not re.fullmatch(r"[A-Za-z ]{3,50}", contact_person):
        show_alert("Contact Person must contain only letters and spaces (3-50 characters).")


def validate_gst_number():
    """
    Indian GST Number validation
    Format: 2 digits (state code) + 10 chars (PAN) + 1 digit (entity) + 'Z' + 1 digit (check)
    Total: 15 characters
    Example: 27AABCU9603R1ZX
    """
    gst_pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
    if not re.fullmatch(gst_pattern, gst_number):
        show_alert("Invalid GST Number. Format: 15 characters (e.g., 27AABCU9603R1ZX)")


def validate_email():
    """Email validation with proper regex"""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.fullmatch(email_pattern, email):
        show_alert("Invalid email address format.")
    if len(email) > 100:
        show_alert("Email must not exceed 100 characters.")


def validate_phone():
    """Indian mobile number: starts with 6-9, exactly 10 digits"""
    if not re.fullmatch(r"[6-9]\d{9}", phone):
        show_alert("Invalid phone number. Must be 10 digits starting with 6-9.")


def validate_address():
    """Address: 10-200 characters"""
    if len(address) < 10 or len(address) > 200:
        show_alert("Address must be between 10 and 200 characters.")


def validate_city():
    """City: 2-50 chars, letters and spaces only"""
    if not re.fullmatch(r"[A-Za-z ]{2,50}", city):
        show_alert("City must contain only letters and spaces (2-50 characters).")


def validate_state():
    """State: 2-50 chars, letters and spaces only"""
    if not re.fullmatch(r"[A-Za-z ]{2,50}", state):
        show_alert("State must contain only letters and spaces (2-50 characters).")


def validate_pincode():
    """Indian PIN code: exactly 6 digits"""
    if not re.fullmatch(r"\d{6}", pincode):
        show_alert("Invalid PIN Code. Must be exactly 6 digits.")


def validate_customer_type():
    """Customer type: must be from allowed values"""
    allowed_types = ["Wholesaler", "Exporter", "Textile Mill", "Garments"]
    if customer_type not in allowed_types:
        show_alert(f"Invalid Customer Type. Allowed: {', '.join(allowed_types)}")


def validate_payment_terms():
    """Payment terms: must be from allowed values"""
    allowed_terms = ["Cash on Delivery", "15 Days Credit", "30 Days Credit", "45 Days Credit", "60 Days Credit",
                     "Net 90", "Immediate"]
    if payment_terms not in allowed_terms:
        show_alert(f"Invalid Payment Terms. Allowed: {', '.join(allowed_terms)}")


def validate_status():
    """Status: must be from allowed values"""
    allowed_status = ["Active", "Inactive", "Pending", "Suspended", "Blacklisted"]
    if status not in allowed_status:
        show_alert(f"Invalid Status. Allowed: {', '.join(allowed_status)}")


# ==================== EXECUTE VALIDATIONS ====================

validate_required_fields()
validate_customer_name()
validate_company_name()
validate_contact_person()
validate_gst_number()
validate_email()
validate_phone()
validate_address()
validate_city()
validate_state()
validate_pincode()
validate_customer_type()
validate_payment_terms()
validate_status()

# ==================== DATABASE OPERATIONS ====================

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor()

    # Check for duplicates before inserting
    check_sql = """
        SELECT customer_name, gst_number, phone_number, email_address 
        FROM customers 
        WHERE gst_number = %s OR phone_number = %s OR email_address = %s
    """
    cursor.execute(check_sql, (gst_number, phone, email))
    existing = cursor.fetchone()

    if existing:
        dup_fields = []
        if existing[1] == gst_number:
            dup_fields.append("GST Number")
        if existing[2] == phone:
            dup_fields.append("Phone Number")
        if existing[3] == email:
            dup_fields.append("Email Address")
        show_alert(f"Duplicate entry found: {', '.join(dup_fields)} already exists.")

    # Insert new customer
    insert_sql = """
        INSERT INTO customers (
            customer_name, company_name, contact_person, gst_number,
            phone_number, email_address, customer_type,
            address, city, state, pincode,
            payment_terms, account_status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        customer_name, company_name, contact_person, gst_number,
        phone, email, customer_type,
        address, city, state, pincode,
        payment_terms, status
    )

    cursor.execute(insert_sql, values)
    conn.commit()

    print("""
        <script>
            alert("Customer saved successfully!");
            window.location.href = "/techvoltInstituteProject/pages/admin_dashboard.html";
        </script>
    """)

except pymysql.MySQLError as e:
    print(f"<h3>Database Error:</h3><p>{e}</p>")
except Exception as e:
    print(f"<h3>Unexpected Error:</h3><p>{e}</p>")

finally:
    try:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    except:
        pass
