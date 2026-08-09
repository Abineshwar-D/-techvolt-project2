#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe
import cgi
import cgitb
from datetime import date, datetime
import json
import os
import pymysql

cgitb.enable()

# 1. SET HEADER TO APPLICATION/JSON
print("Content-Type: application/json\n")

# Extract user_id dynamically from CGI FieldStorage, HTTP Headers, or Environment
form = cgi.FieldStorage()
user_id = form.getvalue("user_id", None)

# Fallback check from environment HTTP header (in case sent via JS Headers)
if not user_id:
    user_id = os.environ.get("HTTP_USER_ID", "").strip()
else:
    user_id = str(user_id).strip()


# Helper function for dates
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


today = date.today()

try:
    conn = pymysql.connect(
        host="localhost", user="root", password="", database="techvoltproject2"
    )
    cursor = conn.cursor()

    # Step 1: Check role and admin status from users or admin table
    is_admin = False
    user_role = ""

    if user_id:
        # Check admin table first
        cursor.execute(
            "SELECT COUNT(*) FROM admin WHERE employee_id = %s OR user_id = %s",
            (user_id, user_id),
        )
        if cursor.fetchone()[0] > 0:
            is_admin = True
            user_role = "Admin"

        # If not admin, get user role from users table
        if not is_admin:
            cursor.execute(
                "SELECT role FROM users WHERE employee_id = %s OR user_id = %s",
                (user_id, user_id),
            )
            role_row = cursor.fetchone()
            if role_row and role_row[0]:
                user_role = str(role_row[0]).strip()

    # Step 2: Order Table Filtering Condition
    # Marketing role can ONLY view orders created by them.
    # Admin and all other roles (Merchandising, Management, etc.) can view ALL orders.
    if user_role.lower() == "marketing":
        filter_clause = "created_by_id = %s"
        user_params = [user_id if user_id else "NON_EXISTENT_USER"]
    else:
        filter_clause = "1=1"
        user_params = []

    # --- KPI Queries ---
    cursor.execute(
        f"SELECT COUNT(*) FROM orders WHERE {filter_clause}", user_params
    )
    total_orders = cursor.fetchone()[0] or 0

    cursor.execute(
        f"SELECT COUNT(*) FROM orders WHERE delivery_date >= %s AND {filter_clause}",
        [today] + user_params,
    )
    running_orders = cursor.fetchone()[0] or 0

    cursor.execute(
        f"SELECT COUNT(*) FROM orders WHERE delivery_date < %s AND {filter_clause}",
        [today] + user_params,
    )
    completed_orders = cursor.fetchone()[0] or 0

    cursor.execute(
        f"SELECT COUNT(*) FROM orders WHERE delivery_date IS NULL AND {filter_clause}",
        user_params,
    )
    pending_orders = cursor.fetchone()[0] or 0

    # --- Order Table Query ---
    query = f"""
        SELECT 
            order_number, customer, contact, fabric_type, 
            gsm, color, quantity, total_amount, 
            remarks, delivery_date, order_date,
            COALESCE(created_by_name, 'N/A') AS created_by
        FROM orders 
        WHERE {filter_clause}
        ORDER BY id DESC
    """
    cursor.execute(query, user_params)
    rows = cursor.fetchall()

    table_rows_html = ""

    if not rows:
        table_rows_html = "<tr><td colspan='6' class='text-center text-muted py-4'>No orders found for this user.</td></tr>"
    else:
        for row in rows:
            (
                order_no,
                cust,
                phone,
                fabric,
                gsm,
                color,
                qty,
                total,
                rem,
                del_date,
                ord_date,
                created_by,
            ) = row

            ord_date_str = safe_format_date(ord_date)
            del_date_str = safe_format_date(del_date)
            cust_name = cust if cust else "Unknown"
            initials = "".join(word[0] for word in cust_name.split()[:2]).upper()
            display_remarks = rem if rem else "No remarks provided."

            # View Button (Always visible for all roles)
            view_btn = f"""
                <button type="button" class="action-btn view-details-btn" 
                        data-bs-toggle="modal" 
                        data-bs-target="#detailsModal"
                        data-customer="{cust_name}"
                        data-contact="{phone or ''}"
                        data-order="{order_no}"
                        data-fabric="{fabric or ''}"
                        data-gsm="{gsm or ''}"
                        data-color="{color or ''}"
                        data-total="{total or ''}"
                        data-remarks="{display_remarks}"
                        >
                    <i class="bi bi-eye"></i>
                </button>
            """

            # Build Action Buttons depending on user role:
            # Non-Marketing & Non-Admin roles see ONLY the View button.
            if is_admin or user_role.lower() == "marketing":
                action_buttons = f"""
                    {view_btn}
                    <button class="action-btn"><i class="bi bi-pencil"></i></button>
                    <button class="action-btn"><i class="bi bi-geo-alt"></i></button>
                """
            else:
                action_buttons = f"{view_btn}"

            table_rows_html += f"""
            <tr class="order-row">
                <td>
                    <span class="order-number">{order_no}</span>
                    <p class="order-date mb-0">Ordered: {ord_date_str}</p>
                </td>
                <td>
                    <div class="d-flex align-items-center gap-2">
                        <div class="customer-avatar">{initials}</div>
                        <span class="fw-medium">{cust_name}</span>
                    </div>
                </td>
                <td>{qty} Kg</td>
                <td>{del_date_str}</td>
                <td>{created_by}</td>
                <td class="text-end">
                    <div class="d-flex justify-content-end gap-1">
                        {action_buttons}
                    </div>
                </td>
            </tr>
            """

    # Return Output as JSON
    response_data = {
        "status": "success",
        "kpis": {
            "total": total_orders,
            "running": running_orders,
            "completed": completed_orders,
            "pending": pending_orders,
        },
        "rows_html": table_rows_html,
    }
    print(json.dumps(response_data))

except Exception as e:
    print(
        json.dumps(
            {
                "status": "error",
                "message": str(e),
                "kpis": {"total": 0, "running": 0, "completed": 0, "pending": 0},
                "rows_html": f"<tr><td colspan='6' class='text-danger'>Error: {str(e)}</td></tr>",
            }
        )
    )

finally:
    if "conn" in locals() and conn.open:
        cursor.close()
        conn.close()