#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
import pymysql

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
    SELECT name, id 
    FROM fabrics
""")

fab = cursor.fetchall()

for row in fab:
    name = row[0]
    fab_id = row[1]

    print(f"""
    <tr>
        <td>{name}</td>

        <td class="text-end">
            <div class="action-buttons">

                <button class="table-action-btn view"
                    title="View Profile"
                    data-bs-toggle="modal"
                    data-bs-target="#productModal"
                    value="{fab_id}"
                    onclick="viewFabric(this.value)">
                   <i class="bi bi-eye-fill"></i>
                </button>

                <!-- DELETE FORM (Automatically gets user_id from browser URL bar on submit) -->
                <form action="../py/fabric/delete_fabric.py" method="POST" style="display:inline;" 
                      onsubmit="return handleDelete(this);">

                    <input type="hidden" name="fabric_id" value="{fab_id}">
                    <input type="hidden" name="user_id" class="dynamic-user-id" value="">

                    <button type="submit" class="table-action-btn delete" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </form>

            </div>
        </td>

    </tr>
    """)

cursor.close()
conn.close()