#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import pymysql
import cgitb
import json

cgitb.enable()
print("Content-Type: text/html\n")

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # Use DictCursor for easier mapping

    # Fetch all details needed for the modal
    cursor.execute("""
        SELECT 
            id, enquiry_id, customer_name, company_name, email, 
            phone_number, fabric_type, fabric_gsm, color, 
            price, quantity, remarks, sample_status 
        FROM customers_enquiries 
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    if not rows:
        print("<tr><td colspan='5' class='text-center'>No customer records found</td></tr>")

    for row in rows:
        # Status Badge Logic
        if row['sample_status'] == 2:
            status_text, status_class, modal_badge = "Quoted", "active", "bg-success"
        elif row['sample_status'] == 1:
            status_text, status_class, modal_badge = "Sample Sent", "pending", "bg-primary"
        else:
            status_text, status_class, modal_badge = "New", "inactive", "bg-secondary"

        # Prepare data for JavaScript (escaping quotes to prevent HTML break)
        # We store the data as attributes on the button
        print(f"""
        <tr>
            <td><span class="customer-name">{row['customer_name']}</span></td>
            <td class="customer-info">{row['company_name']}</td>
            <td class="customer-info">{row['phone_number']}</td>
            <td><span class="status-badge {status_class}">{status_text}</span></td>
            <td class="text-end">
                <div class="d-flex justify-content-end gap-1">
                    <button class="action-btn view-details-btn" 
                        title="View"
                        data-name="{row['customer_name']}"
                        data-email="{row['email']}"
                        data-phone="{row['phone_number']}"
                        data-company="{row['company_name']}"
                        data-fabric="{row['fabric_type']}"
                        data-gsm="{row['fabric_gsm']}"
                        data-color="{row['color']}"
                        data-price="{row['price']}"
                        data-qty="{row['quantity']}"
                        data-remarks="{row['remarks']}"
                        data-status="{status_text}"
                        data-badge="{modal_badge}">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="action-btn" title="Edit"><i class="bi bi-pencil"></i></button>
                    <button class="action-btn delete" onclick="deleteCustomer({row['id']})" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
        """)

except Exception as e:
    print(f"<tr><td colspan='5'>Error: {str(e)}</td></tr>")
finally:
    if 'conn' in locals(): conn.close()
