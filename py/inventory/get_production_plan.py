#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
import cgitb

cgitb.enable()
import json
from datetime import datetime, date
import pymysql

# JSON Header
print("Content-Type: application/json; charset=utf-8\n")


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


def safe_format_view_date(d_val):
    if not d_val:
        return "N/A"
    if isinstance(d_val, (date, datetime)):
        return d_val.strftime("%d/%m/%y")
    try:
        return datetime.strptime(str(d_val).split()[0], "%Y-%m-%d").strftime(
            "%d/%m/%y"
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
user_id_param = str(form.getvalue("user_id") or "").strip()

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
        if user_id_param.upper().startswith("AMD"):
            is_admin = True
        else:
            # Check admin table
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
                # Check users table for role
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
        "SELECT COUNT(*) FROM production_plan WHERE status = 'running'"
    )
    running_plan = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT COUNT(*) FROM production_plan WHERE status = 'completed'"
    )
    completed_plan = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT COUNT(*) FROM production_plan WHERE end_date <= %s", (today,)
    )
    pending_plan = cursor.fetchone()[0] or 0

    # --- Table Rows Query with Customer Name JOIN from customer_enquiry ---
    cursor.execute("""
        SELECT 
            p.plan_no, 
            p.order_no, 
            p.machine, 
            p.start_date, 
            p.end_date, 
            COALESCE(p.created_by_name, 'N/A') AS created_by,
            COALESCE(e.customer_name, p.customer_name, 'N/A') AS customer_name,
            COALESCE(p.fabric_type, 'N/A') AS fabric_type,
            COALESCE(p.color, 'N/A') AS color,
            COALESCE(p.production_target, 'N/A') AS production_target,
            COALESCE(p.supervisor, 'N/A') AS supervisor,
            COALESCE(p.status, 'assigned') AS current_status
        FROM production_plan p
        LEFT JOIN customers_enquiries e ON p.customer_name = e.enquiry_id
        ORDER BY p.plan_no DESC
    """)
    rows = cursor.fetchall()

    table_html = ""
    for row in rows:
        plan_no = row[0] or "N/A"
        order_no = row[1] or "N/A"
        machine = row[2] or "N/A"
        start_date = safe_format_date(row[3])
        end_date = safe_format_date(row[4])
        view_start_date = safe_format_view_date(row[3])
        view_end_date = safe_format_view_date(row[4])
        created_by = row[5] or "N/A"
        customer_name = row[6] or "N/A"
        fabric_type = row[7] or "N/A"
        color = row[8] or "N/A"
        production_target = row[9] or "N/A"
        supervisor = row[10] or "N/A"
        db_status = row[11] or "assigned"

        # Auto-calculate pending status if end_date < today
        end_date_obj = get_date_obj(row[4])
        if end_date_obj and end_date_obj < today:
            status = "pending"
            status_badge = '<span class="badge bg-warning text-dark">Pending</span>'
        else:
            status = db_status.lower()
            if status == "running":
                status_badge = '<span class="badge bg-info text-dark">Running</span>'
            elif status == "completed":
                status_badge = '<span class="badge bg-primary">Completed</span>'
            elif status == "pending":
                status_badge = '<span class="badge bg-warning text-dark">Pending</span>'
            else:
                status_badge = '<span class="badge bg-success">Assigned</span>'

        # Update status in production_plan table
        if plan_no != "N/A":
            cursor.execute(
                "UPDATE production_plan SET status = %s WHERE plan_no = %s",
                (status, plan_no),
            )

        # View button HTML
        view_btn = f"""
            <button class="action-btn" 
                    title="View"
                    data-orderno="{order_no}"
                    data-customer="{customer_name}"
                    data-fabric="{fabric_type}"
                    data-color="{color}"
                    data-target="{production_target}"
                    data-enddate="{view_end_date}"
                    data-startdate="{view_start_date}"
                    data-machine="{machine}"
                    data-supervisor="{supervisor}"
                    data-status="{status.capitalize()}"
                    data-createdby="{created_by}"
                    onclick="openViewPlanModal(this)">
                <i class="bi bi-eye"></i>
            </button>
        """

        # Set action buttons according to Admin check
        if is_admin:
            # Admin sees ONLY the view button
            action_buttons_html = view_btn
        else:
            # Non-Admin sees View, Edit, and Delete buttons
            action_buttons_html = f"""
                {view_btn}
                <button class="action-btn" 
                        title="Edit"
                        data-plan="{plan_no}"
                        data-status="{status}"
                        data-expired="{ 'true' if (end_date_obj and end_date_obj < today) else 'false' }"
                        onclick="openEditPlanModal(this)">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="action-btn" title="Delete" onclick="deleteProductionPlan('{plan_no}')">
                    <i class="bi bi-trash"></i>
                </button>
            """

        # Render separated Start Date and End Date columns
        table_html += f"""
        <tr id="plan-row-{plan_no}">
            <td><span class="plan-number">{plan_no}</span></td>
            <td class="text-muted">{order_no}</td>
            <td>
                <div class="machine-indicator">
                    <span class="dot"></span>
                    {machine}
                </div>
            </td>
            <td><span>{start_date}</span></td>
            <td><span>{end_date}</span></td>
            <td>{created_by}</td>
            <td>{status_badge}</td>
            <td class="text-center">
                <div class="d-flex justify-content-center gap-1">
                    {action_buttons_html}
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