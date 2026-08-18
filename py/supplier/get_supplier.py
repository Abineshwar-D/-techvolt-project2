#!C:\Users\Abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
import json
import sys
import pymysql

cgitb.enable()

# Force UTF-8 stdout encoding for CGI JSON response
sys.stdout.reconfigure(encoding="utf-8")

# Required CGI JSON Header
print("Content-Type: application/json; charset=utf-8\n")

try:
    form = cgi.FieldStorage()
    user_id_param = form.getvalue("user_id", "").strip()
    action = form.getvalue("action", "").strip()

    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2",
        charset="utf8mb4",
        autocommit=True
    )
    cursor = conn.cursor()

    # -------------------------------------------------------------
    # HANDLE BLOCK / UNBLOCK TOGGLE ACTION (ADMIN ONLY)
    # -------------------------------------------------------------
    if action == "toggle_status":
        supplier_code = form.getvalue("supplier_code", "").strip()
        new_status = form.getvalue("new_status", "").strip()

        if supplier_code and new_status:
            cursor.execute(
                "UPDATE supplier SET status = %s WHERE supplier_code = %s",
                (new_status, supplier_code),
            )
            cursor.close()
            conn.close()
            print(json.dumps({
                "status": "success",
                "message": f"Supplier status successfully updated to {new_status}!"
            }))
            sys.exit()

    is_admin = False
    current_user_fullname = ""

    if user_id_param:
        # 1. Check if user is in admin table
        cursor.execute(
            """
            SELECT COUNT(*) FROM admin 
            WHERE LOWER(employee_id) = LOWER(%s) OR LOWER(user_id) = LOWER(%s)
            """,
            (user_id_param, user_id_param),
        )
        if cursor.fetchone()[0] > 0:
            is_admin = True
        else:
            # 2. Get user's role and fullname from users table
            cursor.execute(
                """
                SELECT fullname, LOWER(role) FROM users 
                WHERE LOWER(employee_id) = LOWER(%s) OR LOWER(user_id) = LOWER(%s)
                """,
                (user_id_param, user_id_param),
            )
            user_row = cursor.fetchone()
            if user_row:
                current_user_fullname = (user_row[0] or "").strip()
                user_role = (user_row[1] or "").strip().lower()
                if user_role == "admin":
                    is_admin = True

    # 1. Fetch KPI Counts
    cursor.execute("""
        SELECT 
            COUNT(*) AS total,
            SUM(CASE WHEN LOWER(status) = 'active' THEN 1 ELSE 0 END) AS active,
            SUM(CASE WHEN LOWER(status) = 'inactive' THEN 1 ELSE 0 END) AS inactive
        FROM supplier
    """)
    kpi = cursor.fetchone()

    total_count = kpi[0] if kpi and kpi[0] else 0
    active_count = int(kpi[1]) if kpi and kpi[1] else 0
    inactive_count = int(kpi[2]) if kpi and kpi[2] else 0

    # 2. Fetch Supplier Rows
    cursor.execute("""
        SELECT supplier_code,
               supplier_name,
               contact_person,
               phone,
               email,
               city,
               status,
               COALESCE(created_by_name, 'N/A') AS created_by_name,
               COALESCE(created_by_id, 'N/A') AS created_by_id,
               COALESCE(gst_number, 'N/A') AS gst_number,
               COALESCE(state, 'N/A') AS state,
               COALESCE(material_supplied, '') AS material_supplied
        FROM supplier
        ORDER BY supplier_code DESC
    """)

    rows = cursor.fetchall()

    # 3. Generate Table HTML
    table_html = ""
    for i in rows:
        s_code = i[0]
        s_name = i[1] if i[1] else "N/A"
        contact_person = i[2] if i[2] else "N/A"
        phone = i[3] if i[3] else "N/A"
        email = i[4] if i[4] else "N/A"
        city = i[5] if i[5] else "N/A"
        status_val = i[6] if i[6] else "N/A"
        created_by_name = i[7]
        created_by_id = i[8]
        gst_number = i[9]
        state = i[10]
        material_supplied = i[11]

        first_letter = s_name[0].upper() if s_name and s_name != "N/A" else "S"
        badge = "active" if str(status_val).strip().lower() == "active" else "inactive"

        # View Button
        view_btn = f"""
            <button class="action-btn view-btn"
                    data-supplier-code="{s_code}"
                    data-supplier-name="{s_name}"
                    data-phone="{phone}"
                    data-email="{email}"
                    data-gst="{gst_number}"
                    data-city="{city}"
                    data-state="{state}"
                    data-materials="{material_supplied}"
                    data-created-by="{created_by_name}">
                <i class="bi bi-eye"></i>
            </button>
        """

        # --- Dynamic Edit Button Check ---
        show_row_edit = False

        if is_admin:
            show_row_edit = True
        elif user_id_param:
            if current_user_fullname and current_user_fullname.lower() == str(created_by_name).strip().lower():
                show_row_edit = True
            elif user_id_param.lower() == str(created_by_id).strip().lower():
                show_row_edit = True

        edit_btn = ""
        if show_row_edit:
            edit_btn = f"""
                <button class="action-btn edit" 
                        title="Edit" 
                        data-code="{s_code}"
                        data-phone="{phone}"
                        data-email="{email}"
                        data-materials="{material_supplied}"
                        data-status="{status_val}"
                        onclick="openEditSupplierModal(this)">
                    <i class="bi bi-pencil"></i>
                </button>
            """

        # --- Admin Block / Unblock Toggle Button ---
        block_unblock_btn = ""
        if is_admin:
            if str(status_val).strip().lower() == "active":
                block_unblock_btn = f"""
                    <button class="action-btn text-danger" 
                            title="Block Supplier" 
                            onclick="toggleSupplierStatus('{s_code}', 'Inactive')">
                        <i class="bi bi-slash-circle"></i>
                    </button>
                """
            else:
                block_unblock_btn = f"""
                    <button class="action-btn text-success" 
                            title="Unblock Supplier" 
                            onclick="toggleSupplierStatus('{s_code}', 'Active')">
                        <i class="bi bi-check-circle"></i>
                    </button>
                """

        table_html += f"""
        <tr id="supplier-row-{s_code}">
            <td>
                <div class="d-flex align-items-center gap-2">
                    <div class="supplier-avatar">{first_letter}</div>
                    <span class="supplier-name">{s_name}</span>
                </div>
            </td>

            <td>{contact_person}</td>

            <td>{phone}</td>

            <td>{email}</td>

            <td>{city}</td>

            <td>
                <span class="status-badge {badge}">
                    {status_val}
                </span>
            </td>

            <td>{created_by_name}</td>

            <td class="text-end">
                <div class="d-flex justify-content-end gap-1">
                    {view_btn}
                    {edit_btn}
                    {block_unblock_btn}
                </div>
            </td>
        </tr>
        """

    cursor.close()
    conn.close()

    # Print JSON Response
    response_data = {
        "total": total_count,
        "active": active_count,
        "inactive": inactive_count,
        "table_html": table_html
    }
    print(json.dumps(response_data))

except Exception as e:
    print(json.dumps({
        "error": str(e),
        "total": 0,
        "active": 0,
        "inactive": 0,
        "table_html": f"<tr><td colspan='8' class='text-danger text-center'>Backend Error: {str(e)}</td></tr>"
    }))