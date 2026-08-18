#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
from datetime import datetime

cgitb.enable()
import json
import pymysql

# JSON Header
print("Content-Type: application/json; charset=utf-8\n")


def format_date(d_val):
    if not d_val:
        return "N/A"
    if isinstance(d_val, datetime):
        return d_val.strftime("%d/%m/%Y")
    try:
        return datetime.strptime(str(d_val).split()[0], "%Y-%m-%d").strftime(
            "%d/%m/%Y"
        )
    except Exception:
        return str(d_val)


try:
    conn = pymysql.connect(
        host="localhost", user="root", password="", database="techvoltproject2"
    )
    cursor = conn.cursor()

    # Query supervisor details including email, phone, created_at
    cursor.execute("""
        SELECT id, Supervisor_code, Supervisor_name, Supervisor_email, Supervisor_phone, created_at, status 
        FROM supervisor 
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()

    table_html = ""

    if not rows:
        table_html = '<tr><td colspan="2" class="text-center text-muted py-3">No supervisor found</td></tr>'
    else:
        for row in rows:
            s_id = row[0]
            s_code = row[1] or "N/A"
            s_name = row[2] or "N/A"
            s_email = row[3] or "N/A"
            s_phone = row[4] or "N/A"
            formatted_created_at = format_date(row[5])

            # Generating table rows displaying Supervisor Name and Code with View, Edit, and Delete buttons
            table_html += f"""
            <tr id="supervisor-row-{s_id}">
                <td>
                    <div class="fw-semibold text-dark">{s_name}</div>
                    <small class="text-muted">{s_code}</small>
                </td>
                <td class="text-end">
                    <div class="action-buttons">
                        <button class="table-action-btn view" 
                                title="View" 
                                data-name="{s_name}"
                                data-email="{s_email}"
                                data-phone="{s_phone}"
                                data-created="{formatted_created_at}"
                                onclick="viewSupervisor(this)">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="table-action-btn edit" 
                                title="Edit" 
                                data-id="{s_id}"
                                data-email="{s_email}"
                                data-phone="{s_phone}"
                                onclick="openEditSupervisorModal(this)">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="table-action-btn delete" 
                                title="Delete" 
                                onclick="deleteSupervisor({s_id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
            """

    cursor.close()
    conn.close()

    print(json.dumps({"status": "success", "table_html": table_html}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))