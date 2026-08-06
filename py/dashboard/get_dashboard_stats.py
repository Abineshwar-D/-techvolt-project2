#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe
import pymysql
import cgitb
import json

cgitb.enable()
print("Content-Type: application/json\n")

try:
    conn = pymysql.connect(host="localhost", user="root", password="", database="techvoltproject2")
    cursor = conn.cursor()

    # 1. Total Customers (count of all customer records in customers_enquiries)
    cursor.execute("SELECT COUNT(*) FROM customers_enquiries")
    total_customers = cursor.fetchone()[0] or 0

    # 2. New Enquiries (sample_status = 1)
    cursor.execute("SELECT COUNT(*) FROM customers_enquiries WHERE sample_status = 1")
    new_enquiries = cursor.fetchone()[0] or 0

    # 3. Quotation Sent (sample_status = 2)
    cursor.execute("SELECT COUNT(*) FROM customers_enquiries WHERE sample_status = 2")
    quotations_sent = cursor.fetchone()[0] or 0

    # 4. Confirmed Orders (total records from orders table)
    try:
        cursor.execute("SELECT COUNT(*) FROM orders")
        confirmed_orders = cursor.fetchone()[0] or 0
    except Exception:
        confirmed_orders = 0

    # 5. Enquiries Created Today
    cursor.execute("SELECT COUNT(*) FROM customers_enquiries WHERE DATE(created_at) = CURDATE()")
    today_enquiries = cursor.fetchone()[0] or 0

    # 6. Fetch Recent 4 Enquiries for List Display
    cursor.execute("""
        SELECT customer_name, company_name, fabric_type, quantity, sample_status
        FROM customers_enquiries 
        ORDER BY id DESC LIMIT 4
    """)
    recent_rows = cursor.fetchall()

    recent_html = ""
    for r in recent_rows:
        cust_name, comp_name, fabric, qty, status = r
        display_name = comp_name if comp_name else cust_name
        initials = "".join(word[0] for word in display_name.split()[:2]).upper() if display_name else "CU"

        if status == 2:
            badge_class = "follow-up"
            badge_text = "Quotation Sent"
            border_class = "border-gray"
        elif status == 1:
            badge_class = "in-progress"
            badge_text = "Sample Sent"
            border_class = "border-tertiary"
        else:
            badge_class = "new"
            badge_text = "New"
            border_class = "border-secondary"

        recent_html += f"""
        <div class="enquiry-card {border_class} mb-3 p-3 border rounded-3 d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center gap-3">
                <div class="avatar bg-light border fw-bold rounded-circle p-2 text-center" style="width:40px; height:40px; line-height:22px;">{initials}</div>
                <div>
                    <h6 class="fw-bold mb-0">{display_name}</h6>
                    <p class="text-muted small mb-0">{qty} Kg - {fabric}</p>
                </div>
            </div>
            <div class="d-flex align-items-center gap-3">
                <span class="status-badge {badge_class}">{badge_text}</span>
                <button class="btn btn-link text-muted p-0 text-decoration-none">
                    <i class="bi bi-three-dots-vertical"></i>
                </button>
            </div>
        </div>
        """

    # 7. Calculate Quotation Summary
    qs_sent = quotations_sent
    qs_approved = confirmed_orders
    qs_pending = max(0, qs_sent - qs_approved)

    approval_rate = round((qs_approved / qs_sent * 100), 1) if qs_sent > 0 else 0
    pending_rate = round(100 - approval_rate, 1) if qs_sent > 0 else 100

    conn.close()

    # Return JSON Output
    print(json.dumps({
        "status": "success",
        "kpis": {
            "total_customers": total_customers,
            "new_enquiries": new_enquiries,
            "quotations_sent": quotations_sent,
            "confirmed_orders": confirmed_orders,
            "today_enquiries": today_enquiries
        },
        "recent_enquiries_html": recent_html if recent_html else "<p class='text-muted small'>No recent enquiries "
                                                                 "found.</p>",
        "quotation_summary": {
            "sent": qs_sent,
            "approved": qs_approved,
            "pending": qs_pending,
            "approval_rate": approval_rate,
            "pending_rate": pending_rate
        }
    }))

except Exception as e:
    print(json.dumps({
        "status": "error",
        "message": str(e)
    }))