#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import json
import pymysql

cgitb.enable()

# Set Header to return JSON
print("Content-Type: application/json\n\n")

form = cgi.FieldStorage()
action = form.getvalue("action")
enquiry_id = form.getvalue("enquiry_id")

response_data = {}

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2",
        autocommit=True
    )
    cursor = conn.cursor()

    # -------------------------------------------------------------
    # ACTION 1: FETCH ENQUIRY & MARKETING USERS FOR MODAL
    # -------------------------------------------------------------
    if action == "get_data" and enquiry_id:
        # Fetch current enquiry details
        cursor.execute(
            "SELECT id, created_by_id, created_by_name FROM customers_enquiries WHERE id = %s",
            (enquiry_id,)
        )
        enquiry_row = cursor.fetchone()

        # Fetch all Marketing employees from users table
        cursor.execute(
            "SELECT employee_id, fullname FROM users WHERE LOWER(role) = 'marketing' AND (status IS NULL OR LOWER("
            "status) = 'active') ORDER BY fullname ASC"
        )
        marketing_users = cursor.fetchall()

        marketing_list = []
        for user in marketing_users:
            marketing_list.append({
                "employee_id": user[0],
                "fullname": user[1]
            })

        if enquiry_row:
            response_data = {
                "status": "success",
                "enquiry_id": enquiry_row[0],
                "created_by_id": enquiry_row[1] or "",
                "created_by_name": enquiry_row[2] or "",
                "marketing_users": marketing_list
            }
        else:
            response_data = {"status": "error", "message": "Enquiry record not found"}

    # -------------------------------------------------------------
    # ACTION 2: UPDATE ASSIGNED MARKETING PERSON IN DATABASE
    # -------------------------------------------------------------
    elif action == "update_assignment" and enquiry_id:
        marketing_emp_id = form.getvalue("marketing_emp_id")

        if marketing_emp_id:
            # Fetch fullname of selected marketing employee
            cursor.execute(
                "SELECT fullname FROM users WHERE employee_id = %s OR user_id = %s",
                (marketing_emp_id, marketing_emp_id)
            )
            user_row = cursor.fetchone()

            if user_row:
                emp_name = user_row[0]

                # Update created_by_id and created_by_name in customers_enquiries
                cursor.execute(
                    """
                    UPDATE customers_enquiries 
                    SET created_by_id = %s, created_by_name = %s 
                    WHERE id = %s
                    """,
                    (marketing_emp_id, emp_name, enquiry_id)
                )

                response_data = {
                    "status": "success",
                    "message": "Assigned Marketing Executive updated successfully!"
                }
            else:
                response_data = {"status": "error", "message": "Selected Marketing Executive not found"}
        else:
            response_data = {"status": "error", "message": "Marketing Executive not selected"}

    else:
        response_data = {"status": "error", "message": "Invalid action or parameters"}

    cursor.close()
    conn.close()

except Exception as e:
    response_data = {"status": "error", "message": str(e)}

# Return single JSON response
print(json.dumps(response_data))