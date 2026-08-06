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

# ========================================
# ACTION: GET DASHBOARD DATA
# ========================================
if action == "get_dashboard_data":
    try:
        today = datetime.now().strftime('%Y-%m-%d')

        # ========================================
        # KPI 1: Today's Production
        # Sum of all production_target from production_plan
        # WHERE today's date is between start_date and end_date
        # ========================================
        cursor.execute("""
            SELECT COALESCE(SUM(production_target), 0) 
            FROM production_plan 
            WHERE DATE(start_date) <= %s AND DATE(end_date) >= %s
        """, (today, today))
        today_production = cursor.fetchone()[0]

        # ========================================
        # KPI 2: Production Target
        # Sum of ALL production_target from production_plan
        # ========================================
        cursor.execute("""
            SELECT COALESCE(SUM(production_target), 0) 
            FROM production_plan
        """)
        production_target = cursor.fetchone()[0]

        # ========================================
        # KPI 3: Running Orders
        # Count of DISTINCT plan_no from machine_allocations
        # WHERE status = 'Running'
        # ========================================
        cursor.execute("""
            SELECT COUNT(DISTINCT plan_no) 
            FROM machine_allocations 
            WHERE status = 'Running' AND DATE(allocation_date) = %s
        """, (today,))
        running_orders = cursor.fetchone()[0] or 0

        # ========================================
        # KPI 4: Pending Production
        # Sum of (order_quantity - production_target) from production_plan
        # WHERE end_date >= today (not completed)
        # ========================================
        cursor.execute("""
            SELECT COALESCE(SUM(order_quantity - production_target), 0) 
            FROM production_plan 
            WHERE DATE(end_date) >= %s
        """, (today,))
        pending_production = cursor.fetchone()[0] or 0

        # ========================================
        # Production Performance Metrics
        # ========================================

        # For Target: Same as production_target
        target_value = production_target

        # For Produced: Same as today_production
        produced_value = today_production

        # For Pending: Same as pending_production
        pending_value = pending_production

        # Calculate Completion Percentage
        completion_percentage = 0
        if target_value > 0:
            completion_percentage = round((produced_value / target_value) * 100)

        # ========================================
        # Prepare Response
        # ========================================
        result = {
            "success": True,
            "data": {
                # KPI Cards
                "today_production": str(today_production),
                "production_target":str(production_target),
                "running_orders": str(running_orders),
                "pending_production": str(pending_production),

                # Production Performance
                "target_value": str(target_value),
                "produced_value": str(produced_value),
                "pending_value": str(pending_value),
                "completion_percentage": str(completion_percentage)
            }
        }
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))

    finally:
        cursor.close()
        conn.close()
    exit()

# ========================================
# DEFAULT RESPONSE
# ========================================
else:
    print(json.dumps({
        "success": False,
        "error": "Invalid action. Use action=get_dashboard_data"
    }))
    exit()