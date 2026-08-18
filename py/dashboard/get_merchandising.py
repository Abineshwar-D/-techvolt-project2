#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
import json
import pymysql

cgitb.enable()
print("Content-Type: application/json\n")

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )
    cursor = conn.cursor()

    # ---------------------------------------------------------
    # CARD 1: Total Orders Count from 'orders' table
    # ---------------------------------------------------------
    cursor.execute("SELECT COUNT(*) FROM orders")
    card1_total_orders = cursor.fetchone()[0]

    # ---------------------------------------------------------
    # CARD 2: Machine Allocations count where status = 'completed'
    # ---------------------------------------------------------
    cursor.execute("SELECT COUNT(*) FROM production_plan WHERE LOWER(status) = 'completed'")
    card2_completed_allocations = cursor.fetchone()[0]

    # ---------------------------------------------------------
    # CARD 3: Total count from 'purchased_order' table
    # ---------------------------------------------------------
    cursor.execute("SELECT COUNT(*) FROM purchased_order")
    card3_purchased_orders = cursor.fetchone()[0]

    # ---------------------------------------------------------
    # CARD 4: Running Orders count
    # (orders -> production_plan -> machine_allocations where status = 'running')
    # ---------------------------------------------------------
    card4_sql = """
        SELECT COUNT(DISTINCT o.order_number) 
        FROM orders o
        JOIN production_plan p ON o.order_number = p.order_no
        WHERE LOWER(p.status) = 'running'
    """
    cursor.execute(card4_sql)
    card4_running_orders = cursor.fetchone()[0]

    # ---------------------------------------------------------
    # CARD 5: Total Suppliers Count from 'supplier' table
    # ---------------------------------------------------------
    cursor.execute("SELECT COUNT(*) FROM supplier")
    card5_total_suppliers = cursor.fetchone()[0]

    # ---------------------------------------------------------
    # CARD 6: Machine Allocations count where end_date <= TODAY
    # ---------------------------------------------------------
    cursor.execute("SELECT COUNT(*) FROM purchased_order WHERE expected_delivery < CURDATE()")
    card6_pending_allocations = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    # Prepare JSON response
    response_data = {
        "status": "success",
        "card1": card1_total_orders,
        "card2": card2_completed_allocations,
        "card3": card3_purchased_orders,
        "card4": card4_running_orders,
        "card5": card5_total_suppliers,
        "card6": card6_pending_allocations
    }

    print(json.dumps(response_data))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))