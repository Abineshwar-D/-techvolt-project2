#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb

cgitb.enable()
import json
import pymysql

# JSON Header
print("Content-Type: application/json\n")

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor()

    # Query machine details
    cursor.execute("SELECT id, machine_code, machine_name, status FROM machines ORDER BY id DESC")
    rows = cursor.fetchall()

    table_html = ""

    if not rows:
        table_html = '<tr><td colspan="2" class="text-center text-muted py-3">No machines found</td></tr>'
    else:
        for row in rows:
            m_id = row[0]
            m_code = row[1]
            m_name = row[2]

            # Generating table rows with unique id for each <tr>
            table_html += f"""
            <tr id="machine-row-{m_id}">
                <td>
                    <div class="fw-semibold text-dark">{m_name}</div>
                    <small class="text-muted">{m_code}</small>
                </td>
                <td class="text-end">
                    <button class="btn btn-sm btn-light text-danger" title="Delete" onclick="deleteMachine({m_id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
            """

    cursor.close()
    conn.close()

    print(json.dumps({"status": "success", "table_html": table_html}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))