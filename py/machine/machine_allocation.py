#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb

cgitb.enable()

import cgi
import pymysql
import json
from datetime import datetime

print("Content-Type: application/json\n")

# Database connection
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="techvoltproject2"
)
cursor = conn.cursor()

form = cgi.FieldStorage()
action = form.getvalue("action", "")
today_date = datetime.now().strftime('%Y-%m-%d')

# ===================== 1. GET KPI DATA =====================
if action == "get_kpi":
    try:
        # Get count of machines with status 'Available' from machine_allocations
        cursor.execute(
            "SELECT COUNT(DISTINCT machine_name) FROM machine_allocations WHERE status = 'Available' AND DATE("
            "allocation_date) = %s",
            (today_date,))
        available = cursor.fetchone()[0]

        # Get count of machines with status 'Running' from machine_allocations
        cursor.execute(
            "SELECT COUNT(DISTINCT machine_name) FROM machine_allocations WHERE status = 'Running' AND DATE("
            "allocation_date) = %s",
            (today_date,))
        running = cursor.fetchone()[0]

        # Get count of machines with status 'Maintenance' from machine_allocations
        cursor.execute(
            "SELECT COUNT(DISTINCT machine_name) FROM machine_allocations WHERE status = 'Maintenance' AND DATE("
            "allocation_date) = %s",
            (today_date,))
        maintenance = cursor.fetchone()[0]

        # Get count of all allocations for today
        cursor.execute("SELECT COUNT(*) FROM machine_allocations WHERE DATE(allocation_date) = %s", (today_date,))
        today_allocations = cursor.fetchone()[0]

        result = {
            "available": available,
            "running": running,
            "maintenance": maintenance,
            "today_allocations": today_allocations
        }
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
    exit()

    # ===================== NEW ACTION: MACHINE KPI =====================
elif action == "machine_kpi":
    try:
        # Card 1: Total machines from 'machines' table
        cursor.execute("SELECT COUNT(*) FROM machines")
        total_machines = cursor.fetchone()[0]

        # Card 2: Count of machines with status 'Running'
        cursor.execute(
            "SELECT COUNT(DISTINCT machine_name) FROM machine_allocations WHERE LOWER(status) = 'running'"
        )
        running = cursor.fetchone()[0]

        # Card 3: Count of machines with status 'Assigned'
        cursor.execute(
            "SELECT COUNT(DISTINCT machine_name) FROM machine_allocations WHERE LOWER(status) = 'assigned'"
        )
        assigned = cursor.fetchone()[0]

        # Card 4: Count of machines with status 'Maintenance'
        cursor.execute(
            "SELECT COUNT(DISTINCT machine_name) FROM machine_allocations WHERE LOWER(status) = 'maintenance'"
        )
        maintenance = cursor.fetchone()[0]

        result = {
            "total_machines": total_machines,
            "running": running,
            "assigned": assigned,
            "maintenance": maintenance
        }
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
    exit()

# ===================== 2. GET PRODUCTION PLAN DETAILS =====================
elif action == "get_plan_details":
    plan_id = form.getvalue("plan_id")
    try:
        cursor.execute("""
            SELECT order_no, customer_name, fabric_type, order_quantity, 
                   machine, supervisor, start_date, end_date, production_target
            FROM production_plan 
            WHERE plan_no = %s
        """, (plan_id,))

        row = cursor.fetchone()
        if row:
            result = {
                "order_no": row[0] if row[0] else "-",
                "customer": row[1] if row[1] else "-",
                "fabric": row[2] if row[2] else "-",
                "qty_required": row[3] if row[3] else 0,
                "machine": row[4] if row[4] else "",
                "operator": row[5] if row[5] else "",
                "start_date": str(row[6]) if row[6] else "",
                "end_date": str(row[7]) if row[7] else "",
                "production_target": row[8] if row[8] else 0
            }
        else:
            result = {"error": "Plan not found"}
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
    exit()

# ===================== 3. GET ALL PRODUCTION PLANS =====================
elif action == "get_plans":
    try:
        # Fetch only production plans that are NOT YET allocated in machine_allocations
        cursor.execute("""
            SELECT plan_no 
            FROM production_plan 
            WHERE plan_no NOT IN (
                SELECT DISTINCT plan_no 
                FROM machine_allocations 
                WHERE plan_no IS NOT NULL AND plan_no != ''
            )
            ORDER BY plan_no DESC
        """)
        plans = cursor.fetchall()
        plan_list = [plan[0] for plan in plans]
        print(json.dumps(plan_list))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
    exit()

# ===================== 4. GET TODAY'S ALLOCATIONS =====================
elif action == "get_allocations":
    try:
        # Fix: Use DATE() to compare only the date part
        cursor.execute("""
            SELECT allocation_no, machine_name, plan_no, operator_name, status
            FROM machine_allocations 
            WHERE DATE(allocation_date) = %s
            ORDER BY allocation_no DESC
        """, (today_date,))

        rows = cursor.fetchall()
        allocations = []
        for row in rows:
            allocations.append({
                "allocation_no": row[0],
                "machine": row[1],
                "plan": row[2] if row[2] else "-",
                "operator": row[3] if row[3] else "-",
                "status": row[4] if row[4] else "Assigned"
            })
        print(json.dumps(allocations))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
    exit()

# ===================== 5. SUBMIT MACHINE ALLOCATION =====================
elif action == "submit_allocation":
    plan_no = form.getvalue("plan_no")
    machine = form.getvalue("machine")
    operator = form.getvalue("operator")
    shift = form.getvalue("shift")
    status = form.getvalue("status")
    start_date = form.getvalue("start_date")
    end_date = form.getvalue("end_date")
    remarks = form.getvalue("remarks")

    # Validation
    if not plan_no or not machine or not operator:
        print(json.dumps({"success": False, "error": "Plan, Machine and Operator are required"}))
        exit()

    try:
        # Generate allocation number
        cursor.execute("SELECT allocation_no FROM machine_allocations ORDER BY allocation_no DESC LIMIT 1")
        row = cursor.fetchone()

        if row:
            num = int(row[0].replace("MA", ""))
            new_allocation = f"MA{num + 1:03}"
        else:
            new_allocation = "MA001"

        # Insert into database
        cursor.execute("""
            INSERT INTO machine_allocations (
                allocation_no, plan_no, machine_name, operator_name, 
                shift, status, start_date, end_date, remarks, allocation_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (new_allocation, plan_no, machine, operator, shift, status,
              start_date, end_date, remarks, today_date))

        conn.commit()

        print(json.dumps({
            "success": True,
            "message": "Machine allocated successfully",
            "allocation_no": new_allocation
        }))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
    exit()

# ===================== 6. GET MACHINES LIST =====================
elif action == "get_machines":
    try:
        # Get unique machines from production_plan that have machine value
        cursor.execute("""
            SELECT DISTINCT machine 
            FROM production_plan 
            WHERE machine IS NOT NULL AND machine != ''
            ORDER BY machine
        """)
        rows = cursor.fetchall()
        machines = []
        for row in rows:
            machines.append({
                "name": row[0],
                "status": "Available"  # Default status
            })

        # If no machines found, return defaults
        if not machines:
            machines = [
                {"name": "Machine A", "status": "Available"},
                {"name": "Machine B", "status": "Available"},
                {"name": "Machine C", "status": "Available"},
                {"name": "Machine D", "status": "Available"}
            ]
        print(json.dumps(machines))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
    exit()

# ===================== 7. GET OPERATORS LIST =====================
elif action == "get_operators":
    try:
        # Get unique supervisors from production_plan
        cursor.execute("""
            SELECT DISTINCT supervisor 
            FROM production_plan 
            WHERE supervisor IS NOT NULL AND supervisor != ''
            ORDER BY supervisor
        """)
        rows = cursor.fetchall()
        operators = [row[0] for row in rows]

        # If no operators found, return defaults
        if not operators:
            operators = ["Ramesh", "Suresh", "Amit", "Rajesh", "Priya"]
        print(json.dumps(operators))
    except Exception as e:
        # Return default operators on error
        print(json.dumps(["Ramesh", "Suresh", "Amit", "Rajesh", "Priya"]))
    exit()

    # ===================== 8. GET ALL ALLOCATIONS (FOR TABLE VIEW) =====================
elif action == "get_all_allocations":
    try:
        cursor.execute("""
                SELECT 
                    machine_name,
                    plan_no,
                    operator_name,
                    status,
                    allocation_no,
                    start_date,
                    end_date
                FROM machine_allocations 
                ORDER BY allocation_no DESC
            """)

        rows = cursor.fetchall()
        allocations = []
        for row in rows:
            # Get order_no from production_plan
            cursor.execute("SELECT order_no FROM production_plan WHERE plan_no = %s", (row[1],))
            order_row = cursor.fetchone()
            order_no = order_row[0] if order_row else "-"

            allocations.append({
                "machine_name": row[0] if row[0] else "-",
                "plan_no": row[1] if row[1] else "-",
                "operator_name": row[2] if row[2] else "-",
                "status": row[3] if row[3] else "Assigned",
                "allocation_no": row[4] if row[4] else "-",
                "start_date": str(row[5]) if row[5] else "",
                "end_date": str(row[6]) if row[6] else "",
                "order_no": order_no
            })
        print(json.dumps(allocations))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
    exit()

# ===================== 9. DELETE ALLOCATION =====================
elif action == "delete_allocation":
    allocation_no = form.getvalue("allocation_no")

    if not allocation_no:
        print(json.dumps({"success": False, "error": "Allocation number is required"}))
        exit()

    try:
        cursor.execute("DELETE FROM machine_allocations WHERE allocation_no = %s", (allocation_no,))
        conn.commit()

        if cursor.rowcount > 0:
            print(json.dumps({
                "success": True,
                "message": "Allocation deleted successfully"
            }))
        else:
            print(json.dumps({
                "success": False,
                "error": "Allocation not found"
            }))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
    exit()

# ===================== DEFAULT =====================
else:
    print(json.dumps({"error": "Invalid action"}))
    exit()
