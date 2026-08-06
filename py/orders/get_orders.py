#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe
import pymysql
import cgitb
import json
from datetime import datetime, date

cgitb.enable()

# 1. SET HEADER TO APPLICATION/JSON
print("Content-Type: application/json\n")


# Helper function for dates
def safe_format_date(d_val):
    if not d_val:
        return "N/A"
    if isinstance(d_val, (date, datetime)):
        return d_val.strftime("%d-%m-%Y")
    try:
        return datetime.strptime(str(d_val).split()[0], "%Y-%m-%d").strftime("%d-%m-%Y")
    except Exception:
        return str(d_val)


today = date.today()

try:
    conn = pymysql.connect(host="localhost", user="root", password="", database="techvoltproject2")
    cursor = conn.cursor()

    # --- KPI Queries ---
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM orders WHERE delivery_date >= %s", (today,))
    running_orders = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM orders WHERE delivery_date < %s", (today,))
    completed_orders = cursor.fetchone()[0] or 0

    # Dynamic query for pending/high priority orders
    cursor.execute("SELECT COUNT(*) FROM orders WHERE delivery_date IS NULL")
    pending_orders = cursor.fetchone()[0] or 0

    # --- Order Table Query (Fetched created_by_name) ---
    cursor.execute("""
        SELECT 
            order_number, customer, contact, fabric_type, 
            gsm, color, quantity, total_amount, 
            remarks, delivery_date, order_date,
            COALESCE(created_by_name, 'N/A') AS created_by
        FROM orders 
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()

    table_rows_html = ""
    for row in rows:
        order_no, cust, phone, fabric, gsm, color, qty, total, rem, del_date, ord_date, created_by = row

        ord_date_str = safe_format_date(ord_date)
        del_date_str = safe_format_date(del_date)
        cust_name = cust if cust else "Unknown"
        initials = "".join(word[0] for word in cust_name.split()[:2]).upper()
        display_remarks = rem if rem else "No remarks provided."

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
                    <button class="action-btn"><i class="bi bi-pencil"></i></button>
                    <button class="action-btn"><i class="bi bi-geo-alt"></i></button>
                </div>
            </td>
        </tr>
        """
    conn.close()

    # 2. RETURN EVERYTHING AS JSON
    response_data = {
        "status": "success",
        "kpis": {
            "total": total_orders,
            "running": running_orders,
            "completed": completed_orders,
            "pending": pending_orders
        },
        "rows_html": table_rows_html
    }
    print(json.dumps(response_data))

except Exception as e:
    print(json.dumps({
        "status": "error",
        "message": str(e),
        "kpis": {"total": 0, "running": 0, "completed": 0, "pending": 0},
        "rows_html": f"<tr><td colspan='6' class='text-danger'>Error: {str(e)}</td></tr>"
    }))