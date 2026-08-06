#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
import pymysql

cgitb.enable()
print("Content-Type: text/html\n")

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="techvoltproject2"
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            p.po_number, 
            COALESCE(s.supplier_name, p.supplier) AS supplier_name, 
            p.material, 
            p.required_qty,
            COALESCE(p.created_by_name, 'N/A') AS created_by
        FROM purchased_order p
        LEFT JOIN supplier s ON p.supplier = s.supplier_code
        ORDER BY p.id DESC
    """)

    rows = cursor.fetchall()

    for row in rows:
        print(f"""
        <tr>
            <td class="po-number">{row[0]}</td>
            <td class="supplier-name">{row[1]}</td>
            <td>{row[2]}</td>
            <td>{row[3]} kg</td>
            <td>{row[4]}</td>
            <td class="text-end">
                <div class="d-flex justify-content-end gap-1">
                    <button class="action-btn view">
                        <i class="bi bi-eye"></i>
                    </button>
                </div>
            </td>
        </tr>
        """)

    cursor.close()
    conn.close()

except Exception as e:
    print(f"<tr><td colspan='6' class='text-danger'>Error: {str(e)}</td></tr>")