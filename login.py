#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import pymysql
import urllib.parse

cgitb.enable()
print("Content-Type: text/html\n")

form = cgi.FieldStorage()
username = form.getvalue("username")
password = form.getvalue("password")

# Match exact filenames from your screenshot
ROLE_PAGES = {
    "marketing": "/techvoltInstituteProject/pages/Marketing.html",
    "merchandising": "/techvoltInstituteProject/pages/Merchandising.html",
    "production": "/techvoltInstituteProject/pages/Production.html",
    "storekeeper": "/techvoltInstituteProject/pages/StoreKeeper.html"
}


def send_alert(message, redirect_url=None, go_back=False):
    print("<script>")
    print(f'alert("{message}");')
    if redirect_url:
        print(f'window.location.href="{redirect_url}";')
    if go_back:
        print("window.history.back();")
    print("</script>")


if not username or not password:
    send_alert("Please enter User ID and Password", go_back=True)
else:
    try:
        con = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="techvoltproject2"
        )
        cur = con.cursor()

        encoded_user_id = urllib.parse.quote(username)

        # STEP 1: Check 'users' table with CASE SENSITIVITY using BINARY
        cur.execute(
            "SELECT role, status FROM users WHERE BINARY employee_id=%s AND BINARY password=%s",
            (username, password)
        )
        user_data = cur.fetchone()

        if user_data:
            role, status = user_data[0].strip(), user_data[1]
            role_clean = role.lower()  # Converts "Marketing" to "marketing"

            if status and status.lower() == 'inactive':
                send_alert("You are blocked by Admin.", go_back=True)
            elif role_clean in ROLE_PAGES:
                redirect_target = f"{ROLE_PAGES[role_clean]}?user_id={encoded_user_id}"
                send_alert("Login Successfully!", redirect_url=redirect_target)
            else:
                send_alert(f"Role '{role}' not recognized. Contact Admin.", go_back=True)

        else:
            # STEP 2: Check 'admin' table with CASE SENSITIVITY using BINARY
            cur.execute(
                "SELECT role FROM admin WHERE BINARY employee_id=%s AND BINARY password=%s",
                (username, password)
            )
            admin_data = cur.fetchone()

            if admin_data:
                redirect_target = f"/techvoltInstituteProject/pages/admin_dashboard.html?user_id={encoded_user_id}"
                send_alert("Login Successfully!", redirect_url=redirect_target)
            else:
                send_alert("Invalid User ID or Password", go_back=True)

    except Exception as e:
        print(f"<h3>Database Error: {e}</h3>")

    finally:
        if 'con' in locals():
            con.close()