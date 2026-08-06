#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb

cgitb.enable()
import json
import pymysql

print("Content-Type: application/json\n")

try:
    conn = pymysql.connect(
        host="localhost", user="root", password="", database="techvoltproject2"
    )
    cursor = conn.cursor()

    # -------------------------------------------------------------
    # LOGIC 1: Fetch Machines NOT in production_plan
    # -------------------------------------------------------------
    sql_machines = """
        SELECT m.id, m.machine_code, m.machine_name 
        FROM machines m
        LEFT JOIN production_plan pp 
            ON LOWER(TRIM(m.machine_name)) = LOWER(TRIM(pp.machine))
        WHERE m.status = 'Available' 
          AND pp.plan_no IS NULL
        ORDER BY m.machine_name ASC
    """
    cursor.execute(sql_machines)
    machines = cursor.fetchall()

    machine_options = (
        '<option value="" disabled selected>Select Machine</option>'
    )
    for m in machines:
        m_name = m[2]
        machine_options += f'<option value="{m_name}">{m_name}</option>'

    # -------------------------------------------------------------
    # LOGIC 2: Fetch Supervisors NOT in production_plan
    # -------------------------------------------------------------
    sql_supervisors = """
        SELECT s.id, s.Supervisor_code, s.Supervisor_name 
        FROM supervisor s
        LEFT JOIN production_plan pp 
            ON LOWER(TRIM(s.Supervisor_name)) = LOWER(TRIM(pp.supervisor))
        WHERE s.status = 'Available' 
          AND pp.plan_no IS NULL
        ORDER BY s.Supervisor_name ASC
    """
    cursor.execute(sql_supervisors)
    supervisors = cursor.fetchall()

    supervisor_options = (
        '<option value="" disabled selected>Select Supervisor</option>'
    )
    for s in supervisors:
        s_name = s[2]
        supervisor_options += f'<option value="{s_name}">{s_name}</option>'

    cursor.close()
    conn.close()

    # -------------------------------------------------------------
    # Return both options as JSON response
    # -------------------------------------------------------------
    response = {
        "status": "success",
        "machine_options": machine_options,
        "supervisor_options": supervisor_options,
    }
    print(json.dumps(response))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))