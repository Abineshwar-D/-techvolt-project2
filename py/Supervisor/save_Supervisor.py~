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


# Read Supervisor_name
Supervisor_name = form.getvalue("Supervisor_name")

# 1. Validation
if not Supervisor_name or not Supervisor_name.strip():
    alert_and_redirect("Supervisor Name is required!")
    sys.exit()

Supervisor_name = Supervisor_name.strip()

# ==================== DATABASE OPERATION ====================

try:
    conn = pymysql.connect(
        host="localhost", user="root", password="", database="techvoltproject2"
    )
    cursor = conn.cursor()

    # 2. Check for Duplicate Supervisor Name
    check_query = "SELECT id FROM Supervisor WHERE LOWER(Supervisor_name) = LOWER(%s)"
    cursor.execute(check_query, (Supervisor_name,))

    if cursor.fetchone():
        cursor.close()
        conn.close()
        alert_and_redirect(f"Error: Supervisor '{Supervisor_name}' already exists!")
        sys.exit()

    # 3. Auto-generate Supervisor Code (e.g. SUP001, SUP002)
    cursor.execute("SELECT MAX(id) FROM Supervisor")
    max_id_row = cursor.fetchone()
    next_id = (max_id_row[0] + 1) if max_id_row and max_id_row[0] else 1
    Supervisor_code = f"SUP{next_id:03d}"

    # 4. Insert into DB
    insert_query = """
        INSERT INTO Supervisor (Supervisor_code, Supervisor_name, status)
        VALUES (%s, %s, 'Available')
    """
    cursor.execute(insert_query, (Supervisor_code, Supervisor_name))
    conn.commit()

    cursor.close()
    conn.close()

    alert_and_redirect(
        f"Success! Supervisor '{Supervisor_name}' saved with Code: {Supervisor_code}",
        success=True,
    )

except Exception as e:
    alert_and_redirect(f"Database Error: {str(e)}")