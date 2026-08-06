#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import pymysql
import cgitb
import json

cgitb.enable()

# Set JSON header
print("Content-Type: application/json\n")

try:
    con = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )

    cur = con.cursor()

    # --- KPI Queries for Quotations ---

    # Total Quotations (sample_status = 2 - Approved/Sent Quotations)
    cur.execute("SELECT COUNT(*) FROM customers_enquiries WHERE sample_status = 2")
    total_quotations = cur.fetchone()[0] or 0

    # Pending Quotations (sample_status = 1 - Sample Sent, waiting for quotation)
    cur.execute("SELECT COUNT(*) FROM customers_enquiries WHERE sample_status = 1")
    pending_quotations = cur.fetchone()[0] or 0

    # Approved Quotations (same as total quotations for now)
    cur.execute("SELECT COUNT(*) FROM customers_enquiries WHERE sample_status = 2")
    approved_quotations = cur.fetchone()[0] or 0

    # Rejected Quotations (sample_status = 3 for rejected - if not exists, set to 0)
    cur.execute("SELECT COUNT(*) FROM customers_enquiries WHERE sample_status = 3")
    rejected_quotations = cur.fetchone()[0] or 0

    # --- Fetch Quotation Records (only where sample_status = 2) ---
    cur.execute(""" 
        SELECT 
            enquiry_id,
            customer_name,
            quantity,
            price,
            sample_status,
            created_at
        FROM customers_enquiries 
        WHERE sample_status = 2
        ORDER BY id DESC
    """)

    quotations = cur.fetchall()

    # Build HTML rows
    table_rows_html = ""

    if not quotations:
        table_rows_html = """
        <tr>
            <td colspan="5" class="text-center py-4">
                <i class="bi bi-inbox fs-1 d-block mb-2 text-muted"></i>
                <span class="text-muted">No quotations found</span>
            </td>
        </tr>
        """
    else:
        for quote in quotations:
            enquiry_id = quote[0]  # enquiry_id
            customer = quote[1]  # customer_name
            quantity = quote[2]  # quantity
            price = quote[3]  # price
            status = quote[4]  # sample_status
            created_date = quote[5].strftime("%d-%m-%Y") if quote[5] else "N/A"

            # Calculate total amount
            total_amount = (price or 0) * (quantity or 0)

            # Determine status display
            if status == 2:
                status_text = "Sent"
                status_class = "converted"
            elif status == 1:
                status_text = "Pending"
                status_class = "follow-up"
            elif status == 3:
                status_text = "Rejected"
                status_class = "pending"
            else:
                status_text = "Draft"
                status_class = "draft"

            # Format total amount
            total_amount_formatted = f"₹{total_amount:,.2f}"

            table_rows_html += f"""
            <tr data-quote="{enquiry_id}" onclick="updateDetails('{enquiry_id}', '{customer}', '{total_amount_formatted}', '{status_text}', '{status_class}')">
                <td><span class="quote-number">{enquiry_id}</span></td>
                <td>{customer}</td>
                <td>{total_amount_formatted}</td>
                <td><span class="status-badge {status_class}">{status_text}</span></td>
                <td class="text-right">
                    <div class="d-flex justify-content-end gap-1">
                        <button class="table-action-btn"><i class="bi bi-pencil"></i></button>
                        <button class="table-action-btn"><i class="bi bi-printer"></i></button>
                        <button class="table-action-btn"><i class="bi bi-send"></i></button>
                    </div>
                </td>
            </tr>
            """

    con.close()

    # Return JSON response
    response_data = {
        "status": "success",
        "kpis": {
            "total_quotations": total_quotations,
            "pending_quotations": pending_quotations,
            "approved_quotations": approved_quotations,
            "rejected_quotations": rejected_quotations
        },
        "rows_html": table_rows_html
    }
    print(json.dumps(response_data))

except Exception as e:
    print(json.dumps({
        "status": "error",
        "message": str(e),
        "kpis": {
            "total_quotations": 0,
            "pending_quotations": 0,
            "approved_quotations": 0,
            "rejected_quotations": 0
        },
        "rows_html": f"<tr><td colspan='5' class='text-danger'>Error: {str(e)}</td></tr>"
    }))