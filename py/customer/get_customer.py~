#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import pymysql

cgitb.enable()

print("Content-Type: text/html\n")

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2",
        autocommit=True,
    )

    cursor = conn.cursor()
    form = cgi.FieldStorage()

    # Get URL parameters
    current_user_id = str(form.getvalue("user_id") or "").strip()
    action = form.getvalue("action")
    target_id = form.getvalue("id")
    assigned_emp_id = form.getvalue("assigned_emp_id")

    # 1. Process Actions (Assign / Block / Unblock / Delete)
    if action == "assign" and target_id and assigned_emp_id:
        cursor.execute(
            "SELECT fullname FROM users WHERE employee_id = %s OR user_id = %s",
            (assigned_emp_id, assigned_emp_id),
        )
        emp = cursor.fetchone()
        emp_name = emp[0] if emp else assigned_emp_id

        cursor.execute(
            """
            UPDATE customers_enquiries 
            SET created_by_id = %s, created_by_name = %s 
            WHERE id = %s
        """,
            (assigned_emp_id, emp_name, target_id),
        )

    elif action == "block" and target_id:
        cursor.execute(
            "UPDATE customers_enquiries SET sample_status = 0 WHERE id = %s",
            (target_id,),
        )

    elif action == "unblock" and target_id:
        cursor.execute(
            "UPDATE customers_enquiries SET sample_status = 2 WHERE id = %s",
            (target_id,),
        )

    elif action == "delete" and target_id:
        cursor.execute(
            "DELETE FROM customers_enquiries WHERE id = %s", (target_id,)
        )

    # 2. Check Role (Admin vs Marketing)
    is_admin = False
    if current_user_id.upper().startswith("AMD") or current_user_id == "":
        is_admin = True
    else:
        cursor.execute(
            "SELECT role FROM users WHERE LOWER(employee_id) = %s OR LOWER(user_id) = %s",
            (current_user_id.lower(), current_user_id.lower()),
        )
        role_res = cursor.fetchone()
        if role_res and str(role_res[0]).strip().lower() in [
            "admin",
            "administrator",
        ]:
            is_admin = True

    # 3. Fetch Enquiries Based on Role
    if is_admin:
        # Admin sees ALL enquiries
        cursor.execute("""
            SELECT customer_name, company_name, phone_number, sample_status, created_by_name, id, created_by_id
            FROM customers_enquiries 
            ORDER BY id DESC
        """)
    else:
        # Marketing person sees ONLY their assigned enquiries
        cursor.execute(
            """
            SELECT customer_name, company_name, phone_number, sample_status, created_by_name, id, created_by_id
            FROM customers_enquiries 
            WHERE LOWER(TRIM(created_by_id)) = %s
            ORDER BY id DESC
        """,
            (current_user_id.lower(),),
        )

    rows = cursor.fetchall()

    if not rows:
        print(
            "<tr><td colspan='6' class='text-center text-muted'>No customer records found</td></tr>"
        )

    # 4. Output HTML Rows
    for row in rows:
        name = row[0]
        company = row[1]
        phone = row[2]
        sample_status = row[3]
        created_by = row[4]
        db_id = row[5]

        # Status badge mapping
        if sample_status == 2:
            status_text = "Quoted"
            status_class = "active"
        elif sample_status == 1:
            status_text = "Sample Sent"
            status_class = "pending"
        else:
            status_text = "New Enquiry"
            status_class = "inactive"

        # Created By Display / Assign Button
        if not created_by or str(created_by).strip().upper() in [
            "NULL",
            "NONE",
            "",
        ]:
            if is_admin:
                created_by_display = f"""
                <button class="btn btn-sm btn-outline-primary py-0 px-2 fw-semibold" onclick="openAssignModal({db_id})" title="Assign to Marketing">
                    <i class="bi bi-person-plus-fill me-1"></i> Assign
                </button>
                """
            else:
                created_by_display = (
                    "<span class='text-muted italic'>Unassigned</span>"
                )
        else:
            created_by_display = created_by

        if not is_admin:
            toggle_action = f"""
            <button class="action-btn delete" onclick="deleteCustomer({db_id})" title="Delete">
                <i class="bi bi-trash"></i>
            </button>
            """

        print(f"""
        <tr>
            <td><span class="customer-name">{name}</span></td>
            <td class="customer-info">{company}</td>
            <td class="customer-info">{phone}</td>
            <td><span class="status-badge {status_class}">{status_text}</span></td>
            <td class="customer-info">{created_by_display}</td>
            <td class="text-end">
                <div class="d-flex justify-content-end gap-1">
                    <button class="action-btn" title="View" onclick="viewCustomer({db_id})"><i class="bi bi-eye"></i></button>
                    <button 
    class="action-btn"
    value="{row[5]}" 
    data-bs-toggle="modal"
    data-bs-target="#editMarketingModal"
    onclick="editEnquiry(this.value)">
    <i class="bi bi-pencil"></i>
</button>
                </div>
            </td>
        </tr>
        """)

except Exception as e:
    print(f"<tr><td colspan='6'>Error loading data: {str(e)}</td></tr>")

finally:
    if "conn" in locals():
        cursor.close()
        conn.close()
