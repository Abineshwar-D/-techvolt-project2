#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import pymysql
import cgitb
import sys
import json

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

# Output Content-Type as JSON
print("Content-Type: application/json; charset=utf-8\n")

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )

    cursor = conn.cursor()

    # --- KPI 1: Total Count of Materials ---
    cursor.execute("SELECT COUNT(*) FROM materials")
    total_materials = cursor.fetchone()[0] or 0

    # --- KPI 2: Total Available Stock (Sum of opening_stock) ---
    cursor.execute("SELECT COALESCE(SUM(opening_stock), 0) FROM materials")
    total_stock = float(cursor.fetchone()[0])

    # --- KPI 3: Count of Materials that exist in purchased_order table ---
    cursor.execute("""
        SELECT COUNT(DISTINCT m.material_id)
        FROM materials m
        INNER JOIN purchased_order p 
            ON m.material_name = p.material
            OR m.material_name LIKE CONCAT('%', p.material, '%')
            OR p.material LIKE CONCAT('%', m.material_name, '%')
    """)
    matched_materials_count = cursor.fetchone()[0] or 0

    # --- TABLE DATA: Query Materials Table ---
    cursor.execute("""
        SELECT
            material_code,
            material_name,
            opening_stock,
            delivery_date,
            COALESCE(created_by_name, 'N/A') AS created_by
        FROM materials
        ORDER BY material_id DESC
    """)

    rows = cursor.fetchall()
    table_html = ""

    for row in rows:
        material_code = row[0]
        material_name = row[1]
        stock = float(row[2]) if row[2] else 0.0
        delivery_date = str(row[3]) if row[3] else "N/A"
        created_by = row[4] or "N/A"

        table_html += f"""
        <tr>
            <td>
                <div class="d-flex align-items-center gap-2">
                    <div class="material-icon">
                        <i class="bi bi-grid"></i>
                    </div>
                    <span class="material-name">
                        {material_name}
                    </span>
                </div>
            </td>

            <td class="text-right stock-value">
                {stock:,.2f} Kg
            </td>

            <td class="text-center">
                <span class="status-badge">
                    {delivery_date}
                </span>
            </td>

            <td class="text-start">
                {created_by}
            </td>

            <td class="text-right">
                <div class="d-flex justify-content-end gap-1">
                    <button class="action-btn" title="Add Stock">
                        <i class="bi bi-plus-square"></i>
                    </button>
                    <button class="action-btn" title="Issue Stock">
                        <i class="bi bi-box-arrow-right"></i>
                    </button>
                    <button class="action-btn" title="View Ledger">
                        <i class="bi bi-book"></i>
                    </button>
                </div>
            </td>
        </tr>
        """

    cursor.close()
    conn.close()

    # Build response JSON
    response_data = {
        "total_materials": total_materials,
        "available_stock": f"{total_stock:,.2f} Kg",
        "po_matched_count": matched_materials_count,
        "table_html": table_html
    }

    print(json.dumps(response_data))

except Exception as e:
    print(json.dumps({"error": str(e)}))