#!C:\Users\Abi\AppData\Local\Programs\Python\Python311\python.exe

import json
import pymysql

# Set header response as JSON
print("Content-Type: application/json\n")

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="techvoltproject2"
)

cursor = conn.cursor()

# 1. Fetch KPI Counts
cursor.execute("""
    SELECT 
        COUNT(*) AS total,
        SUM(CASE WHEN LOWER(status) = 'active' THEN 1 ELSE 0 END) AS active,
        SUM(CASE WHEN LOWER(status) = 'inactive' THEN 1 ELSE 0 END) AS inactive
    FROM supplier
""")
kpi = cursor.fetchone()

total_count = kpi[0] if kpi[0] else 0
active_count = int(kpi[1]) if kpi[1] else 0
inactive_count = int(kpi[2]) if kpi[2] else 0

# 2. Fetch Supplier Rows (Added created_by_name)
cursor.execute("""
SELECT supplier_name,
       contact_person,
       phone,
       email,
       city,
       status,
       COALESCE(created_by_name, 'N/A') AS created_by
FROM supplier
ORDER BY supplier_code DESC
""")

rows = cursor.fetchall()

# 3. Generate Table HTML
table_html = ""
for i in rows:
    first_letter = i[0][0].upper() if i[0] else ""
    badge = "active" if str(i[5]).strip().lower() == "active" else "inactive"
    created_by = i[6]

    table_html += f"""
    <tr>
        <td>
            <div class="d-flex align-items-center gap-2">
                <div class="supplier-avatar">{first_letter}</div>
                <span class="supplier-name">{i[0]}</span>
            </div>
        </td>

        <td>{i[1]}</td>

        <td>{i[2]}</td>

        <td>{i[3]}</td>

        <td>{i[4]}</td>

        <td>
            <span class="status-badge {badge}">
                {i[5]}
            </span>
        </td>

        <td>{created_by}</td>

        <td class="text-end">
            <div class="d-flex justify-content-end gap-1">
                <button class="action-btn">
                    <i class="bi bi-eye"></i>
                </button>

                <button class="action-btn">
                    <i class="bi bi-pencil"></i>
                </button>

                <button class="action-btn delete">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </td>
    </tr>
    """

cursor.close()
conn.close()

# 4. Construct response dictionary and print JSON
response_data = {
    "total": total_count,
    "active": active_count,
    "inactive": inactive_count,
    "table_html": table_html
}

print(json.dumps(response_data))