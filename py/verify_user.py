#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import json
import pymysql

cgitb.enable()

# Print header first
print("Content-Type: application/json\n")

# 1. READ URL PARAMETERS (From GET request sent by router.js)
form = cgi.FieldStorage()
user_id = form.getvalue("user_id")
current_page = form.getvalue("page")  # e.g., "admin_dashboard.html" or "landing.html"

# ===== BYPASS USER_ID CHECK FOR LANDING PAGE =====
if current_page and "landing.html" in current_page.lower():
    response = {
        "status": "success",
        "message": "Public access granted for Landing Page",
        "role": "public"
    }
    print(json.dumps(response))
    exit()
# =================================================

# 2. MATCH EXACT FILENAMES
ROLE_PAGES = {
    "admin": "admin_dashboard.html",
    "merchandising": "Merchandising.html",
    "marketing": "Marketing.html",
    "production": "Production.html",
    "storekeeper": "StoreKeeper.html"
}

response = {"status": "error", "message": "Access Denied"}

# 3. CHECK IF PARAMETERS ARE RECEIVED
if not user_id or not current_page:
    response["message"] = f"Missing parameters: user_id='{user_id}', page='{current_page}'"
    print(json.dumps(response))
    exit()

try:
    con = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cur = con.cursor()

    # 4. STEP 1: Check 'admin' table first
    cur.execute("SELECT role FROM admin WHERE employee_id=%s", (user_id,))
    admin_data = cur.fetchone()

    if admin_data:
        admin_role = admin_data[0] if admin_data[0] else "Admin"
        response = {
            "status": "success",
            "message": "Admin Authorized",
            "role": admin_role.strip()
        }
    else:
        # 5. STEP 2: Check 'users' table
        cur.execute("SELECT role, status FROM users WHERE employee_id=%s", (user_id,))
        user_data = cur.fetchone()

        if user_data:
            db_role, db_status = user_data[0].strip(), user_data[1]

            # Check if user status is blocked/inactive
            if db_status and db_status.lower() == 'inactive':
                response["message"] = "Your account is blocked by Admin."
            else:
                db_role_clean = db_role.lower()
                expected_page = ROLE_PAGES.get(db_role_clean)

                # Validate if user is visiting their permitted page
                if expected_page and expected_page.lower() in current_page.lower():
                    response = {
                        "status": "success",
                        "message": "Authorized access",
                        "role": db_role
                    }
                else:
                    response["message"] = f"Access Blocked: Your assigned role ({db_role}) does not have permission for this page."
        else:
            response["message"] = f"Invalid User ID '{user_id}' or user does not exist."

except Exception as e:
    response = {"status": "error", "message": f"Database Error: {str(e)}"}

finally:
    if 'con' in locals():
        con.close()

# Return JSON response back to router.js
print(json.dumps(response))