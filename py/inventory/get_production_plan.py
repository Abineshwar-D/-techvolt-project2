#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb

cgitb.enable()
import json
from datetime import datetime, date
import pymysql

# JSON Header
print("Content-Type: application/json\n")


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

# Get query parameters from URL (e.g. ?user_id=EMP003)
form = cgi.FieldStorage()
user_id_param = form.getvalue("user_id", "")

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2",
        autocommit=False,
    )
    cursor = conn.cursor()

    # --- Check if current user is Admin ---
    is_admin = False
    if user_id_param:
        cursor.execute(
            """
            SELECT role FROM users 
            WHERE employee_id = %s OR user_id = %s
        """,
            (user_id_param, user_id_param),
        )
        user_row = cursor.fetchone()
        if user_row and str(user_row[0]).strip().lower() == "admin":
            is_admin = True

    # --- KPI Queries ---
    cursor.execute("SELECT COUNT(*) FROM production_plan")
    total_plan = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT COUNT(*) FROM machine_allocations WHERE status = 'running'"
    )
    running_plan = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT COUNT(*) FROM machine_allocations WHERE status = 'completed'"
    )
    completed_plan = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT COUNT(*) FROM production_plan WHERE end_date >= %s", (today,)
    )
    pending_plan = cursor.fetchone()[0] or 0

    # --- Table Rows Query ---
    cursor.execute("""
        SELECT plan_no, order_no, machine, start_date, end_date, COALESCE(created_by_name, 'N/A') AS created_by
        FROM production_plan
        ORDER BY plan_no DESC
    """)
    rows = cursor.fetchall()

    table_html = ""
    for row in rows:
        plan_no = row[0] or "N/A"
        order_no = row[1] or "N/A"
        machine = row[2] or "N/A"
        start_date = safe_format_date(row[3])
        end_date = safe_format_date(row[4])
        created_by = row[5] or "N/A"

        # Calculate status based on end_date > today
        end_date_obj = get_date_obj(row[4])
        if end_date_obj and end_date_obj < today:
            status = "pending"
            status_badge = (
                '<span class="badge bg-warning text-dark">Pending</span>'
            )
        else:
            status = "assigned"
            status_badge = '<span class="badge bg-success">Assigned</span>'

        # Update status in production_plan table
        if plan_no != "N/A":
            cursor.execute(
                "UPDATE production_plan SET status = %s WHERE plan_no = %s",
                (status, plan_no),
            )

        # Set 3rd action button according to Admin check
        if is_admin:
            action_btn = '<button class="action-btn" title="Block"><i class="bi bi-slash-circle"></i></button>'
        else:
            action_btn = '<button class="action-btn" title="Delete"><i class="bi bi-trash"></i></button>'

        # Render 7 <td> items to match 7 <th> headers
        table_html += f"""
        <tr>
            <td><span class="plan-number">{plan_no}</span></td>
            <td class="text-muted">{order_no}</td>
            <td>
                <div class="machine-indicator">
                    <span class="dot"></span>
                    {machine}
                </div>
            </td>
            <td>
                <div class="date-range">
                    <span>{start_date}</span>
                    <span class="sub">to {end_date}</span>
                </div>
            </td>
            <td>{created_by}</td>
            <td>{status_badge}</td>
            <td class="text-center">
                <div class="d-flex justify-content-center gap-1">
                    <button class="action-btn" title="View"><i class="bi bi-eye"></i></button>
                    <button class="action-btn" title="Edit"><i class="bi bi-pencil"></i></button>
                    {action_btn}
                </div>
            </td>
        </tr>
        """

    # Commit DB updates
    conn.commit()

    cursor.close()
    conn.close()

    # Send data as JSON
    response = {
        "total_plan": total_plan,
        "running_plan": running_plan,
        "completed_plan": completed_plan,
        "pending_plan": pending_plan,
        "table_html": table_html,
    }
    print(json.dumps(response))

except Exception as e:
    print(json.dumps({"error": str(e)}))