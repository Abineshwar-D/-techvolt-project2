#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
from datetime import date, datetime

import pymysql

cgitb.enable()
print("Content-Type: text/html\n")

conn = pymysql.connect(
    host="localhost", user="root", password="", database="techvoltproject2"
)

cursor = conn.cursor()
form = cgi.FieldStorage()

employee_id = form.getvalue("employee_id")

sql = """
    SELECT *
    FROM users
    WHERE employee_id=%s
    """
cursor.execute(sql, (employee_id,))
user = cursor.fetchone()


# Function to safely format dates
def format_date(val, fmt="%d-%m-%Y"):
    if not val:
        return "-"
    if isinstance(val, (datetime, date)):
        return val.strftime(fmt)
    try:
        clean_date = str(val).split()[0]
        return datetime.strptime(clean_date, "%Y-%m-%d").strftime(fmt)
    except Exception:
        return str(val)


if user:
    formatted_dob = format_date(user[4])  # Index 4 = dob
    formatted_created = format_date(user[10])  # Index 10 = created_at

    print(f"""
        <div class="col-6">
            <label class="fw-bold">Full Name</label>
            <p id="m_fullname" class="text-muted">{user[2]}</p>
        </div>

        <div class="col-6">
            <label class="fw-bold">Email</label>
            <p id="m_email" class="text-muted">{user[3]}</p>
        </div>

        <div class="col-6">
            <label class="fw-bold">DOB</label>
            <p id="m_dob" class="text-muted">{formatted_dob}</p>
        </div>

        <div class="col-6">
            <label class="fw-bold">Gender</label>
            <p id="m_gender" class="text-muted">{user[6]}</p>
        </div>

        <div class="col-6">
            <label class="fw-bold">State</label>
            <p id="m_state" class="text-muted">{user[5]}</p>
        </div>

        <div class="col-6">
            <label class="fw-bold">City</label>
            <p id="m_city" class="text-muted">{user[7]}</p>
        </div>

        <div class="col-6">
            <label class="fw-bold">Phone Number</label>
            <p id="m_phone" class="text-muted">{user[8]}</p>
        </div>

        <div class="col-6">
            <label class="fw-bold">Role</label>
            <p id="m_role" class="text-muted">{user[9]}</p>
        </div>

        <div class="col-6">
            <label class="fw-bold">Status</label>
            <p id="m_status" class="text-muted">{user[12]}</p>
        </div>

        <div class="col-6">
            <label class="fw-bold">Created At</label>
            <p id="m_created" class="text-muted">{formatted_created}</p>
        </div>
    """)
else:
    print("<p>User not found</p>")

conn.close()