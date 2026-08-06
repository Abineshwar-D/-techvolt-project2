#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import json
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
    redirect_url = f"/techvoltInstituteProject/pages/Production.html?user_id={logged_in_user_id.strip()}#page12"
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


# Read machine_name
machine_name = form.getvalue("machine_name")

# 1. Validation
if not machine_name or not machine_name.strip():
    alert_and_redirect("Machine Name is required!")
    sys.exit()

machine_name = machine_name.strip()

# ==================== DATABASE OPERATION ====================

try:
    conn = pymysql.connect(
        host="localhost", user="root", password="", database="techvoltproject2"
    )
    cursor = conn.cursor()

    # 2. Check for Duplicate Machine Name
    check_query = "SELECT id FROM machines WHERE LOWER(machine_name) = LOWER(%s)"
    cursor.execute(check_query, (machine_name,))

    if cursor.fetchone():
        cursor.close()
        conn.close()
        alert_and_redirect(f"Error: Machine '{machine_name}' already exists!")
        sys.exit()

    # 3. Auto-generate Machine Code (e.g. MAC001, MAC002)
    cursor.execute("SELECT MAX(id) FROM machines")
    max_id_row = cursor.fetchone()
    next_id = (max_id_row[0] + 1) if max_id_row and max_id_row[0] else 1
    machine_code = f"MAC{next_id:03d}"

    # 4. Insert into DB
    insert_query = """
        INSERT INTO machines (machine_code, machine_name, status)
        VALUES (%s, %s, 'Available')
    """
    cursor.execute(insert_query, (machine_code, machine_name))
    conn.commit()

    cursor.close()
    conn.close()

    alert_and_redirect(
        f"Success! Machine '{machine_name}' saved with Code: {machine_code}",
        success=True,
    )

except Exception as e:
    alert_and_redirect(f"Database Error: {str(e)}")