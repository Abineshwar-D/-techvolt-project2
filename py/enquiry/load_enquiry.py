#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe
import cgi
import cgitb
import json
from datetime import datetime, date
import pymysql

cgitb.enable()

print("Content-Type: application/json\n")

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
    current_user_id = str(form.getvalue("user_id") or "").strip()

    # Determine role filter (Admin vs Marketing Employee)
    is_admin = False
    if current_user_id.upper().startswith("AMD") or current_user_id == "":
        is_admin = True

    # -------------------------------------------------------------
    # 1. KPI QUERIES (Role-filtered)
    # -------------------------------------------------------------
    if is_admin:
        cursor.execute("SELECT COUNT(*) FROM customers_enquiries")
        total_enquiries = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT COUNT(*) FROM customers_enquiries WHERE sample_status = 0"
        )
        pending_enquiries = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT COUNT(*) FROM customers_enquiries WHERE sample_status = 2"
        )
        followup_required = cursor.fetchone()[0] or 0
    else:
        cursor.execute(
            "SELECT COUNT(*) FROM customers_enquiries WHERE LOWER(TRIM(created_by_id)) = %s",
            (current_user_id.lower(),),
        )
        total_enquiries = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT COUNT(*) FROM customers_enquiries WHERE sample_status = 0 AND LOWER(TRIM(created_by_id)) = %s",
            (current_user_id.lower(),),
        )
        pending_enquiries = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT COUNT(*) FROM customers_enquiries WHERE sample_status = 2 AND LOWER(TRIM(created_by_id)) = %s",
            (current_user_id.lower(),),
        )
        followup_required = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM orders")
    converted_orders = cursor.fetchone()[0] or 0

    # -------------------------------------------------------------
    # 2. ENQUIRY TABLE QUERY
    # -------------------------------------------------------------
    if is_admin:
        cursor.execute("""
            SELECT 
                enquiry_id, 
                customer_name, 
                fabric_type, 
                quantity, 
                created_at, 
                sample_status, 
                COALESCE(created_by_name, 'Unassigned') AS created_by,
                id
            FROM customers_enquiries 
            ORDER BY id DESC
        """)
    else:
        cursor.execute(
            """
            SELECT 
                enquiry_id, 
                customer_name, 
                fabric_type, 
                quantity, 
                created_at, 
                sample_status, 
                COALESCE(created_by_name, 'Unassigned') AS created_by,
                id
            FROM customers_enquiries 
            WHERE LOWER(TRIM(created_by_id)) = %s
            ORDER BY id DESC
        """,
            (current_user_id.lower(),),
        )

    rows = cursor.fetchall()

    table_rows_html = ""
    for row in rows:
        (
            enquiry_id,
            customer,
            fabric,
            qty,
            created_at,
            sample_status,
            created_by,
            db_id,
        ) = row

        display_enq_id = enquiry_id if enquiry_id else f"ENQ00{db_id}"

        # Button state logic
        if sample_status == 2:
            btn_text = "Quotation Sent"
            btn_class = "btn-secondary"
            status_val = "2"
            disabled_attr = "disabled"
        elif sample_status == 1:
            btn_text = "Send Quotation"
            btn_class = "btn-success"
            status_val = "1"
            disabled_attr = ""
        else:
            btn_text = "Send Sample"
            btn_class = "btn-primary"
            status_val = "0"
            disabled_attr = ""

        created_date = (
            created_at.strftime("%d-%m-%Y") if created_at else "N/A"
        )

        if is_admin:
            action_button = f"""<button class="table-action-btn delete" onclick="toggleStatus({db_id}, 'block')" title="Block"><i class="bi bi-slash-circle"></i></button>"""
        else:
            action_button = f"""<button class="table-action-btn delete" onclick="deleteCustomer({db_id})" title="Delete"><i class="bi bi-trash"></i></button>"""

        table_rows_html += f"""
        <tr data-enquiry="{display_enq_id}">
            <td><span class="enquiry-number">{display_enq_id}</span></td>
            <td>{customer}</td>
            <td>{fabric if fabric else 'N/A'}</td>
            <td>{qty if qty else 0} Kg</td>
            <td><span class="status-badge pending">{created_date}</span></td>
            <td>{created_by}</td>
            <td class="text-right">
                <div class="d-flex justify-content-end gap-1">
                    <button class="table-action-btn" title="Update"><i class="bi bi-pencil"></i></button>
                    {action_button}
                    <button class="btn {btn_class} btn-sm action-sample-btn" 
                            data-id="{db_id}" 
                            data-enquiry-id="{display_enq_id}"
                            data-current-status="{status_val}"
                            {disabled_attr}>
                        {btn_text}
                    </button>
                </div>
            </td>
        </tr>
        """

    conn.close()

    print(
        json.dumps({
            "status": "success",
            "kpis": {
                "total_enquiries": total_enquiries,
                "pending_enquiries": pending_enquiries,
                "followup_required": followup_required,
                "converted_orders": converted_orders,
            },
            "rows_html": table_rows_html,
        })
    )

except Exception as e:
    print(
        json.dumps({
            "status": "error",
            "message": str(e),
            "kpis": {
                "total_enquiries": 0,
                "pending_enquiries": 0,
                "followup_required": 0,
                "converted_orders": 0,
            },
            "rows_html": f"<tr><td colspan='7' class='text-danger'>Error: {str(e)}</td></tr>",
        })
    )