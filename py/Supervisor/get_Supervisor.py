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
    cursor.execute("SELECT id, Supervisor_code, Supervisor_name, status FROM supervisor ORDER BY id DESC")
    rows = cursor.fetchall()

    table_html = ""

    if not rows:
        table_html = '<tr><td colspan="2" class="text-center text-muted py-3">No supervisor found</td></tr>'
    else:
        for row in rows:
            s_id = row[0]
            s_code = row[1]
            s_name = row[2]

            # Generating table rows displaying Machine Name (and Machine Code under it)
            table_html += f"""
            <tr>
                <td>
                    <div class="fw-semibold text-dark">{s_name}</div>
                    <small class="text-muted">{s_code}</small>
                </td>
                <td class="text-end">
                    <button class="btn btn-sm btn-light text-primary" title="Edit" onclick="editMachine({s_id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-light text-danger" title="Delete" onclick="deleteMachine({s_id})">
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