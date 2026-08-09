#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import json
import sys
import pymysql

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

print("Content-Type: application/json; charset=utf-8\n")

form = cgi.FieldStorage()
material_code = form.getvalue("material_code", "").strip()
process = form.getvalue("process", "IN").strip().upper()
input_qty_str = form.getvalue("quantity", "0").strip()
user_id = form.getvalue("user_id", "").strip()  # Capture dynamic user_id

try:
    input_qty = float(input_qty_str)
    if input_qty <= 0:
        raise ValueError("Quantity must be greater than zero.")

    conn = pymysql.connect(
        host="localhost", user="root", password="", database="techvoltproject2"
    )
    cursor = conn.cursor()

    # Get current stock
    cursor.execute(
        "SELECT opening_stock FROM materials WHERE material_code = %s",
        (material_code,),
    )
    row = cursor.fetchone()

    if not row:
        print(
            json.dumps({"status": "error", "message": "Material not found."})
        )
    else:
        current_stock = float(row[0]) if row[0] else 0.0

        # Math Logic: IN -> add, OUT -> subtract
        if process == "IN":
            new_stock = current_stock + input_qty
        elif process == "OUT":
            if input_qty > current_stock:
                raise ValueError("Insufficient stock for OUT process.")
            new_stock = current_stock - input_qty
        else:
            raise ValueError("Invalid process type.")

        # Update Database
        cursor.execute(
            "UPDATE materials SET opening_stock = %s WHERE material_code = %s",
            (new_stock, material_code),
        )
        conn.commit()

        # Generate dynamic redirect URL with current user_id
        if user_id:
            redirect_url = f"../pages/StoreKeeper.html?user_id={user_id}#page6"
        else:
            redirect_url = "../pages/StoreKeeper.html#page6"

        print(
            json.dumps(
                {
                    "status": "success",
                    "message": "Stock updated successfully!",
                    "new_stock": new_stock,
                    "redirect_url": redirect_url,
                }
            )
        )

    cursor.close()
    conn.close()

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))