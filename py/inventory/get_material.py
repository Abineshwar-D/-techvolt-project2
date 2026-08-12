#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb
from datetime import date, datetime
import json
import sys
import pymysql

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

# Output Content-Type as JSON
print("Content-Type: application/json; charset=utf-8\n")

# Get query parameters from URL (e.g. ?user_id=AMD007)
form = cgi.FieldStorage()
user_id_param = form.getvalue("user_id", "").strip()


def safe_format_date(d_val):
    if not d_val:
        return "N/A"
    if isinstance(d_val, (date, datetime)):
        return d_val.strftime("%d-%m-%Y")
    try:
        return datetime.strptime(str(d_val).split()[0], "%Y-%m-%d").strftime(
            "%d-%m-%Y"
        )
    except Exception:
        return str(d_val)


def get_date_obj(d_val):
    if not d_val:
        return None
    if isinstance(d_val, datetime):
        return d_val.date()
    if isinstance(d_val, date):
        return d_val
    try:
        return datetime.strptime(str(d_val).split()[0], "%Y-%m-%d").date()
    except Exception:
        return None


today = date.today()

try:
    conn = pymysql.connect(
        host="localhost", user="root", password="", database="techvoltproject2"
    )

    cursor = conn.cursor()

    # --- Robust Check if current user is Admin ---
    is_admin = False
    if user_id_param:
        cursor.execute(
            """
            SELECT COUNT(*) FROM admin 
            WHERE employee_id = %s OR user_id = %s
        """,
            (user_id_param, user_id_param),
        )
        if cursor.fetchone()[0] > 0:
            is_admin = True
        else:
            cursor.execute(
                """
                SELECT COUNT(*) FROM users 
                WHERE (employee_id = %s OR user_id = %s) 
                  AND LOWER(role) = 'admin'
            """,
                (user_id_param, user_id_param),
            )
            if cursor.fetchone()[0] > 0:
                is_admin = True

    # --- KPI 1: Total Count of Materials ---
    cursor.execute("SELECT COUNT(*) FROM materials")
    total_materials = cursor.fetchone()[0] or 0

    # --- KPI 2: Total Available Stock ---
    cursor.execute("SELECT COALESCE(SUM(opening_stock), 0) FROM materials")
    total_stock = float(cursor.fetchone()[0])

    # --- KPI 3: Matched Materials Count ---
    cursor.execute("""
        SELECT COUNT(DISTINCT m.material_id)
        FROM materials m
        INNER JOIN purchased_order p 
            ON m.material_name = p.material
            OR m.material_name LIKE CONCAT('%', p.material, '%')
            OR p.material LIKE CONCAT('%', m.material_name, '%')
    """)
    matched_materials_count = cursor.fetchone()[0] or 0

    # --- TABLE DATA: Query Materials Table ---
    cursor.execute("""
        SELECT
            material_code,
            material_name,
            opening_stock,
            delivery_date,
            COALESCE(created_by_name, 'N/A') AS created_by
        FROM materials
        ORDER BY material_id DESC
    """)

    rows = cursor.fetchall()
    table_html = ""

    for row in rows:
        material_code = row[0]
        material_name = row[1]
        stock = float(row[2]) if row[2] else 0.0
        delivery_date_raw = row[3]
        formatted_delivery_date = safe_format_date(delivery_date_raw)
        created_by = row[4] or "N/A"

        # --- Status Calculation Logic ---
        del_date_obj = get_date_obj(delivery_date_raw)
        if del_date_obj and del_date_obj < today:
            status_badge = (
                '<span class="badge bg-warning text-dark">Pending</span>'
            )
        else:
            status_badge = '<span class="badge bg-success">Stored</span>'

        # Edit button configured with data attributes for opening the modal
        edit_btn = f"""
            <button class="action-btn edit-stock-btn" 
                    title="Edit Stock" 
                    data-code="{material_code}" 
                    data-name="{material_name}" 
                    data-stock="{stock:.2f}"
                    onclick="openStockModal(this)">
                <i class="bi bi-pencil"></i>
            </button>
        """

        # --- Action Buttons Logic based on Admin Check ---
        if is_admin:
            action_buttons = f"""
                <button class="action-btn" title="View"><i class="bi bi-eye"></i></button>
                {edit_btn}
                <button class="action-btn" title="Block"><i class="bi bi-slash-circle"></i></button>
            """
        else:
            action_buttons = f"""
                <button class="action-btn" title="View"><i class="bi bi-eye"></i></button>
                {edit_btn}
                <button class="action-btn" title="Delete"><i class="bi bi-trash"></i></button>
            """

        table_html += f"""
        <tr>
            <td>
                <div class="d-flex align-items-center gap-2">
                    <div class="material-icon">
                        <i class="bi bi-grid"></i>
                    </div>
                    <span class="material-name">
                        {material_name}
                    </span>
                </div>
            </td>

            <td class="text-right stock-value">
                {stock:,.2f} Kg
            </td>

            <td class="text-center">
                <span class="status-badge">
                    {formatted_delivery_date}
                </span>
            </td>

            <td class="text-center">
                {status_badge}
            </td>

            <td class="text-start">
                {created_by}
            </td>

            <td class="text-right">
                <div class="d-flex justify-content-end gap-1">
                    {action_buttons}
                </div>
            </td>
        </tr>
        """

    cursor.close()
    conn.close()

    response_data = {
        "total_materials": total_materials,
        "available_stock": f"{total_stock:,.2f} Kg",
        "po_matched_count": matched_materials_count,
        "table_html": table_html,
    }

    print(json.dumps(response_data))

except Exception as e:
    print(json.dumps({"error": str(e)}))