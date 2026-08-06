#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe
import cgi
import cgitb
import json
import pymysql

cgitb.enable()

# Output JSON header
print("Content-Type: application/json\n\n")


# Helper function to execute query across possible table name variations safely
def safe_count(cursor, possible_tables, where_clause=""):
    for table_name in possible_tables:
        try:
            query = f"SELECT COUNT(*) FROM {table_name} {where_clause}"
            cursor.execute(query)
            return cursor.fetchone()[0]
        except Exception:
            continue
    return 0


try:
    con = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2",
    )
    cur = con.cursor()

    # 1. Total Active Users (users table where status = Active)
    active_users = safe_count(
        cur, ["users"], "WHERE LOWER(TRIM(status)) = 'active'"
    )

    # 2. Total Customers (customers_enquiries table)
    total_customers = safe_count(
        cur, ["customers_enquiries", "customer_enquiries", "enquiries"]
    )

    # 3. Total Orders (orders table)
    total_orders = safe_count(cur, ["orders", "order"])

    # 4. Total Suppliers (supplier / suppliers table)
    total_suppliers = safe_count(cur, ["supplier", "suppliers"])

    # 5. Running Machine Allocations (machine_allocations table where status = running)
    running_orders = safe_count(
        cur,
        ["machine_allocations", "machine_allocation"],
        "WHERE LOWER(TRIM(status)) = 'running'",
    )

    # 6. Purchase Orders (purchased_order table)
    total_po = safe_count(
        cur, ["purchased_order", "purchase_orders", "purchase_order"]
    )

    # --- System Roles Counts (from users table) ---
    # Marketing Executive
    marketing_users = safe_count(
        cur, ["users"], "WHERE TRIM(role) = 'Marketing' AND status = 'Active'"
    )

    # Merchandising
    merchandiser_users = safe_count(
        cur, ["users"], "WHERE TRIM(role) = 'Merchandising' AND status = 'Active'"
    )

    # Production Executive
    production_users = safe_count(
        cur, ["users"], "WHERE TRIM(role) = 'production' AND status = 'Active'"
    )

    # Store Keeper
    storekeeper_users = safe_count(
        cur, ["users"], "WHERE TRIM(role) = 'Storekeeper' AND status = 'Active'"
    )

    con.close()

    # Output JSON Payload
    response = {
        "status": "success",
        "active_users": active_users,
        "total_customers": total_customers,
        "total_orders": total_orders,
        "total_suppliers": total_suppliers,
        "running_orders": running_orders,
        "total_po": total_po,
        "marketing_users": marketing_users,
        "merchandiser_users": merchandiser_users,
        "production_users": production_users,
        "storekeeper_users": storekeeper_users,
    }

    print(json.dumps(response))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))