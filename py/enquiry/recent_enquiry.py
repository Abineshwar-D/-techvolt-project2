#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import pymysql
import cgitb

cgitb.enable()

print("Content-Type: text/html\n")

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="techvoltproject2"
)

cursor = conn.cursor()

cursor.execute("""
SELECT
    e.enquiry_no,
    c.customer_name
FROM enquiries e
JOIN customers c
ON e.customer_id = c.id
WHERE DATE(e.created_at) = CURDATE()
ORDER BY e.created_at DESC
""")

rows = cursor.fetchall()

for row in rows:

    enquiry_no = row[0]
    customer_name = row[1]

    print(f"""
    <tr>
        <td><span class="enquiry-id">{enquiry_no}</span></td>
        <td>{customer_name}</td>
        <td><span class="status-badge new">New</span></td>
        <td class="text-right">
            <div class="d-flex justify-content-end align-items-center gap-1 flex-wrap">
                <button class="table-action-btn">
                    <i class="bi bi-eye"></i>
                </button>

                <button class="table-action-btn">
                    <i class="bi bi-pencil"></i>
                </button>

                <button class="btn-convert-sample">
                    Convert to Sample
                </button>

                <button class="btn-convert-quotation">
                    Convert to Quotation
                </button>
            </div>
        </td>
    </tr>
    """)

cursor.close()
conn.close()