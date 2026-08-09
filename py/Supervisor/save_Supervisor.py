#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import json
import re
import sys
import pymysql

cgitb.enable()

print("Content-Type: text/html\n\n")

form = cgi.FieldStorage()

# READ LOGGED-IN USER ID PASSED FROM FORM
logged_in_user_id = form.getvalue("user_id") or form.getvalue("admin_id")

# DYNAMIC REDIRECT URL GENERATION
if logged_in_user_id and logged_in_user_id.strip():
    # Replace 'Production.html' with your target page name if different
    redirect_url = f"/techvoltInstituteProject/pages/Production.html?user_id={logged_in_user_id.strip()}#page13"
else:
    redirect_url = "/techvoltInstituteProject/pages/login.html"


def alert_and_redirect(message, success=False):
    safe_msg = json.dumps(message)

    # If success -> Redirect to the main page preserving session URL
    # If error   -> Go back to form so user can fix inputs
    if success:
        if not logged_in_user_id:
            action = 'window.location.href = "/techvoltInstituteProject/pages/login.html";'
        else:
            safe_url = json.dumps(redirect_url)
            action = f"window.location.href = {safe_url};"
    else:
        action = "window.history.back();"

    print(f"""
    <script>
        alert({safe_msg});
        {action}
    </script>
    """)


# Read Form Values
Supervisor_name = form.getvalue("Supervisor_name")
Supervisor_email = form.getvalue("Supervisor_email")
Supervisor_phone = form.getvalue("Supervisor_phone")

# ==================== VALIDATION LOGIC ====================

# 1. Validate Supervisor Name
if not Supervisor_name or not Supervisor_name.strip():
    alert_and_redirect("Supervisor Name is required!")
    sys.exit()

Supervisor_name = Supervisor_name.strip()
if len(Supervisor_name) < 3 or len(Supervisor_name) > 20:
    alert_and_redirect("Supervisor Name must be between 3 and 20 characters long!")
    sys.exit()

# 2. Validate Supervisor Email
if not Supervisor_email or not Supervisor_email.strip():
    alert_and_redirect("Supervisor Email is required!")
    sys.exit()

Supervisor_email = Supervisor_email.strip()
# Regex requirement: Must contain at least 1 digit, special character allowed, valid domain
email_pattern = r"^(?=.*\d)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
if not re.match(email_pattern, Supervisor_email):
    alert_and_redirect(
        "Invalid Email! Email must contain at least one digit and have a valid domain format (e.g. user123@domain.com).")
    sys.exit()

# 3. Validate Supervisor Phone
if not Supervisor_phone or not Supervisor_phone.strip():
    alert_and_redirect("Supervisor Phone Number is required!")
    sys.exit()

Supervisor_phone = Supervisor_phone.strip()
# Regex requirement: Starts with 6, 7, 8, or 9 and exactly 10 digits long
phone_pattern = r"^[6-9]\d{9}$"
if not re.match(phone_pattern, Supervisor_phone):
    alert_and_redirect(
        "Invalid Phone Number! Phone number must be exactly 10 digits long and start with 6, 7, 8, or 9.")
    sys.exit()

# ==================== DATABASE OPERATION ====================

try:
    conn = pymysql.connect(
        host="localhost", user="root", password="", database="techvoltproject2"
    )
    cursor = conn.cursor()

    # Check for Duplicate Supervisor Name, Email, or Phone Number
    check_query = """
        SELECT Supervisor_name, Supervisor_email, Supervisor_phone 
        FROM Supervisor 
        WHERE LOWER(Supervisor_name) = LOWER(%s) 
           OR LOWER(Supervisor_email) = LOWER(%s) 
           OR Supervisor_phone = %s
    """
    cursor.execute(check_query, (Supervisor_name, Supervisor_email, Supervisor_phone))
    existing_record = cursor.fetchone()

    if existing_record:
        matched_name, matched_email, matched_phone = existing_record
        cursor.close()
        conn.close()

        if matched_name and matched_name.lower() == Supervisor_name.lower():
            alert_and_redirect(f"Error: Supervisor Name '{Supervisor_name}' already exists!")
        elif matched_email and matched_email.lower() == Supervisor_email.lower():
            alert_and_redirect(f"Error: Supervisor Email '{Supervisor_email}' is already registered!")
        elif matched_phone and matched_phone == Supervisor_phone:
            alert_and_redirect(f"Error: Supervisor Phone Number '{Supervisor_phone}' is already registered!")
        else:
            alert_and_redirect("Error: Duplicate supervisor details found!")

        sys.exit()

    # Auto-generate Supervisor Code (e.g. SUP001, SUP002)
    cursor.execute("SELECT MAX(id) FROM Supervisor")
    max_id_row = cursor.fetchone()
    next_id = (max_id_row[0] + 1) if max_id_row and max_id_row[0] else 1
    Supervisor_code = f"SUP{next_id:03d}"

    # Insert into DB
    insert_query = """
        INSERT INTO Supervisor (Supervisor_code, Supervisor_name, Supervisor_email, Supervisor_phone, status)
        VALUES (%s, %s, %s, %s, 'Available')
    """
    cursor.execute(insert_query, (Supervisor_code, Supervisor_name, Supervisor_email, Supervisor_phone))
    conn.commit()

    cursor.close()
    conn.close()

    alert_and_redirect(
        f"Success! Supervisor '{Supervisor_name}' saved with Code: {Supervisor_code}",
        success=True,
    )

except Exception as e:
    alert_and_redirect(f"Database Error: {str(e)}")