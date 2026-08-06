#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
import cgi
import pymysql

cgitb.enable()
print("Content-Type: text/html\n")

# 1. Database Connection
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="techvoltproject2"
)
cursor = conn.cursor()

# 2. Get the fabric_id AND user_id from form submission
form = cgi.FieldStorage()
fabric_id = form.getvalue("fabric_id")

# Check for both 'user_id' or 'uid' parameter
user_id = form.getvalue("user_id") or form.getvalue("uid") or ""

if fabric_id:
    try:
        # A. Delete from colors first (due to foreign key relation)
        cursor.execute("DELETE FROM fabric_colors WHERE fabric_id = %s", (fabric_id,))

        # B. Delete from fabrics
        cursor.execute("DELETE FROM fabrics WHERE id = %s", (fabric_id,))

        conn.commit()

        # 3. Construct dynamic redirect URL (Preserves user_id)
        if user_id:
            redirect_url = f"/techvoltInstituteProject/pages/admin_dashboard.html?user_id={user_id}"
        else:
            redirect_url = "/techvoltInstituteProject/pages/admin_dashboard.html"

        # Success Alert and Redirect
        print(f"""
        <script>
            alert("Fabric Deleted Successfully!");
            window.location.href = "{redirect_url}";
        </script>
        """)
    except Exception as e:
        print(f"<h3>Error: {e}</h3>")
else:
    print("<h3>Error: ID not received.</h3>")

cursor.close()
conn.close()