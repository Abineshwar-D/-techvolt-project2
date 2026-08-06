#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import pymysql

cgitb.enable()

# Output HTTP header (Requires double newline \n\n)
print("Content-Type: text/html\n\n")

form = cgi.FieldStorage()

fabric_name = form.getvalue("fabric_name")
fabric_color = form.getvalue("fabric_color")
fabric_price = form.getvalue("fabric_price")

# 1. Read logged-in user ID passed from the hidden form field
logged_in_user_id = form.getvalue("admin_id") or form.getvalue("user_id")

# 2. Dynamic Redirect URL logic
if logged_in_user_id and logged_in_user_id.strip():
    redirect_url = f"/techvoltInstituteProject/pages/admin_dashboard.html?user_id={logged_in_user_id.strip()}#page12"
else:
    # Redirect to login page if session parameter is completely missing
    redirect_url = "/techvoltInstituteProject/pages/login.html"

try:
    # Database Connection
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor()

    # --- STEP 1: Check if the fabric name already exists in the 'fabrics' table ---
    cursor.execute("SELECT id FROM fabrics WHERE name = %s", (fabric_name,))
    existing_fabric = cursor.fetchone()

    if existing_fabric:
        # --- STEP 2a: Fabric exists, so we just grab the existing ID ---
        fabric_id = existing_fabric[0]
        message = f"New color '{fabric_color}' added to existing fabric '{fabric_name}'."
    else:
        # --- STEP 2b: Fabric does not exist, create a new record in 'fabrics' ---
        cursor.execute("INSERT INTO fabrics (name) VALUES (%s)", (fabric_name,))
        fabric_id = cursor.lastrowid  # Get the ID created for this new fabric
        message = f"Created new fabric '{fabric_name}' and added color '{fabric_color}'."

    # --- STEP 3: Always insert the color and price into 'fabric_colors' table ---
    cursor.execute(
        "INSERT INTO fabric_colors (fabric_id, color_name, price) VALUES (%s, %s, %s)",
        (fabric_id, fabric_color, fabric_price)
    )

    # --- Employee / Color ID logic ---
    cursor.execute("SELECT employee_id FROM users ORDER BY user_id DESC LIMIT 1")
    row = cursor.fetchone()
    if row:
        num = int(row[0].replace("EMP", ""))
        new_id = f"COL{num + 1:03}"
    else:
        new_id = "COL001"

    conn.commit()

    # 3. Print Alert and redirect preserving logged_in_user_id
    if not logged_in_user_id:
        print("""
        <script>
            alert("Fabric updated successfully, but session ID was missing. Redirecting to login.");
            window.location.href = "/techvoltInstituteProject/pages/login.html";
        </script>
        """)
    else:
        print(f"""
        <script>
            alert("{message}");
            window.location.href = "{redirect_url}";
        </script>
        """)

except Exception as e:
    # On database failure, alert and step back
    print(f"""
    <script>
        alert("Database Error: {str(e)}");
        window.history.back();
    </script>
    """)

finally:
    if 'conn' in locals() and conn.open:
        cursor.close()
        conn.close()