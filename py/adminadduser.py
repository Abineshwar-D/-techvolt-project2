#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import smtplib
import sys

import pymysql

# Enable CGI debug tracking
cgitb.enable()

# Output HTTP header
print("Content-Type: text/html\n\n")

# ====================================================
# YOUR FIXED EMAIL CONFIGURATION (ADMIN'S EMAIL)
# ====================================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "abineshwar68@gmail.com"  # YOUR email
SMTP_PASSWORD = "pjlo yemf queh tfrl"  # YOUR app password
SENDER_EMAIL = "abineshwar68@gmail.com"  # YOUR email

# ====================================================
# DATABASE CONNECTION
# ====================================================
con = pymysql.connect(
    host="localhost", user="root", password="", database="techvoltproject2"
)
cur = con.cursor()


# ====================================================
# FUNCTIONS (CLEANED - NO PRINT STATEMENTS INSIDE)
# ====================================================
def generate_employee_id():
    cur.execute("""
            SELECT employee_id 
            FROM users
            ORDER BY user_id DESC
            LIMIT 1
        """)
    row = cur.fetchone()

    if row:
        num = int(row[0].replace("EMP", ""))
        return f"EMP{num + 1:03}"
    else:
        return "EMP001"


def generate_password(employee_id):
    return employee_id + "@123"


def validate_phone(phone):
    """Clean validation - Returns True or False without printing HTML noise"""
    if not phone:
        return False

    clean_phone = re.sub(r"[\s\-\(\)]", "", str(phone))
    pattern = r"^(?:\+91|0)?[6-9][0-9]{9}$"

    return re.match(pattern, clean_phone) is not None


def validate_email(email):
    """Clean validation - Returns True or False without printing HTML noise"""
    if not email:
        return False

    clean_email = str(email).strip()
    pattern = r"^[a-zA-Z0-9._%+-]+@gmail.com$"

    return re.match(pattern, clean_email, re.IGNORECASE) is not None


def send_email_via_smtp(recipient_email, employee_id, password, full_name, role):
    """Send email to the user (dynamic recipient)"""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
        msg["Subject"] = "Welcome to TechVolt - Your Account Credentials"

        html_content = f"""
            <html>
            <body>
                <h2>Welcome to TechVolt!</h2>
                <p>Dear <strong>{full_name}</strong>,</p>
                <p>Your account has been created successfully.</p>

                <div style="background: #f5f5f5; padding: 15px; border-left: 4px solid #667eea;">
                    <p><strong>Employee ID:</strong> {employee_id}</p>
                    <p><strong>Password:</strong> {password}</p>
                    <p><strong>Role:</strong> {role}</p>
                </div>

                <p><a href="http://localhost/techvoltInstituteProject/">Click here to login</a></p>
                <p>Please change your password after first login.</p>
            </body>
            </html>
            """

        msg.attach(MIMEText(html_content, "html"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()

        return True, f"Email sent to {recipient_email}"

    except Exception as e:
        return False, f"Failed: {str(e)}"


# ====================================================
# GET FORM DATA
# ====================================================
form = cgi.FieldStorage()

fullname = form.getvalue("fullname")
email = form.getvalue("email")
DOB = form.getvalue("DOB")
state1 = form.getvalue("state1")
gender = form.getvalue("gender")
city1 = form.getvalue("city1")
phonenumber = form.getvalue("phonenumber")
role = form.getvalue("role")
status = form.getvalue("status") or "Active"

# READ CURRENT LOGGED-IN USER ID PASSED FROM FORM
logged_in_user_id = form.getvalue("admin_id") or form.getvalue("user_id")

# ====================================================
# DYNAMIC REDIRECT URL GENERATION
# ====================================================
if logged_in_user_id and logged_in_user_id.strip():
    redirect_url = f"/techvoltInstituteProject/pages/admin_dashboard.html?user_id={logged_in_user_id.strip()}#page11"
else:
    # Safe fallback if user access parameter is completely missing
    redirect_url = "/techvoltInstituteProject/pages/login.html"

# ====================================================
# VALIDATE FORM FIELDS
# ====================================================

# 1. Required fields check
if not all([fullname, email, phonenumber, role, DOB, state1, gender, city1]):
    print("""
        <script>
            alert("All fields are required!");
            window.history.back();
        </script>
        """)
    con.close()
    sys.exit()

# 2. Phone validation check
if not validate_phone(phonenumber):
    print("""
        <script>
            alert("Phone number is invalid! Must be a 10-digit number starting with 6-9.");
            window.history.back();
        </script>
        """)
    con.close()
    sys.exit()

# 3. Email validation check
if not validate_email(email):
    print("""
        <script>
            alert("Email is invalid!");
            window.history.back();
        </script>
        """)
    con.close()
    sys.exit()

# ====================================================
# SAVE TO DATABASE
# ====================================================
try:
    employee_id = generate_employee_id()
    password = generate_password(employee_id)

    # Check if email exists
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cur.fetchone():
        print("""
            <script>
                alert("Email already exists!");
                window.history.back();
            </script>
            """)
        con.close()
        sys.exit()

        # 2. Check if PHONE NUMBER already exists
    cur.execute("SELECT user_id FROM users WHERE phonenumber = %s", (phonenumber,))
    if cur.fetchone():
        print("""
                   <script>
                       alert("Phone number is already registered with another user!");
                       window.history.back();
                   </script>
                   """)
        con.close()
        sys.exit()

    # 3. Optional: Check if FULLNAME already exists (if required)
    cur.execute("SELECT user_id FROM users WHERE fullname = %s", (fullname,))
    if cur.fetchone():
        print("""
                   <script>
                       alert("A user with this full name already exists!");
                       window.history.back();
                   </script>
                   """)
        con.close()
        sys.exit()

    # Insert user
    sql = """INSERT INTO users
                 (employee_id, fullname, email, dob, state, gender, city, phonenumber, role, password, status, created_at)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())"""

    cur.execute(
        sql,
        (
            employee_id,
            fullname,
            email,
            DOB,
            state1,
            gender,
            city1,
            phonenumber,
            role,
            password,
            status,
        ),
    )
    con.commit()
    con.close()

    # ====================================================
    # SEND EMAIL
    # ====================================================
    email_sent, email_message = send_email_via_smtp(
        email, employee_id, password, fullname, role
    )

    # ====================================================
    # RESPONSE REDIRECT
    # ====================================================
    if not logged_in_user_id:
        print("""
            <script>
                alert("User created, but session parameter was missing. Redirecting to login.");
                window.location.href = "/techvoltInstituteProject/pages/login.html";
            </script>
            """)
    elif email_sent:
        print(f"""
            <script>
                alert("User created successfully!\\nCredentials sent to: {email}\\nEmployee ID: {employee_id}");
                window.location.href = "{redirect_url}";
            </script>
            """)
    else:
        print(f"""
            <script>
                alert("User created but email failed to send.\\nEmployee ID: {employee_id}");
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
