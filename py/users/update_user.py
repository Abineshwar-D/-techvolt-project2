#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import pymysql

cgitb.enable()

# 1. Output HTTP Header for HTML rendering
print("Content-Type: text/html\n\n")

form = cgi.FieldStorage()

employee_id = form.getvalue("employee_id")  # User being updated
email = form.getvalue("email")
phone = form.getvalue("phone")
state = form.getvalue("state")
city = form.getvalue("city")

# 2. Read logged-in user ID passed from the hidden form field
logged_in_user_id = form.getvalue("admin_id") or form.getvalue("user_id")

# 3. Dynamic Redirect URL logic
if logged_in_user_id and logged_in_user_id.strip():
    redirect_url = f"/techvoltInstituteProject/pages/admin_dashboard.html?user_id={logged_in_user_id.strip()}"
else:
    # Redirect to login if session parameter is completely missing
    redirect_url = "/techvoltInstituteProject/pages/login.html"

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET 
            email=%s,
            phonenumber=%s,
            state=%s,
            city=%s
        WHERE employee_id=%s
    """, (email, phone, state, city, employee_id))

    conn.commit()

    # 4. Print JS Alert and redirect preserving logged_in_user_id
    if not logged_in_user_id:
        print("""
        <script>
            alert("User updated successfully, but session ID was missing. Redirecting to login.");
            window.location.href = "/techvoltInstituteProject/pages/login.html";
        </script>
        """)
    else:
        print(f"""
        <script>
            alert("User updated successfully!");
            window.location.href = "{redirect_url}";
        </script>
        """)

except Exception as e:
    # On failure, return to previous page without breaking form inputs
    print(f"""
    <script>
        alert("Error updating user: {str(e)}");
        window.history.back();
    </script>
    """)

finally:
    if 'conn' in locals() and conn.open:
        conn.close()