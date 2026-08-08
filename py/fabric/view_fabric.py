#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe
import cgi
import cgitb
import pymysql
import datetime

cgitb.enable()

print("Content-Type: text/html\n")

# 1. Database Connection
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="techvoltproject2"
)

cursor = conn.cursor()
form = cgi.FieldStorage()
fab_id = form.getvalue("fab_id")

# 2. Execute Query
# This will return multiple rows if one fabric has multiple colors
cursor.execute("""
    SELECT 
        f.name,
        fc.created_at,
        fc.color_name,
        fc.price,
        fc.id
    FROM fabrics f
    LEFT JOIN fabric_colors fc
    ON f.id = fc.fabric_id
    WHERE f.id=%s
""", (fab_id,))

rows = cursor.fetchall()

if rows:
    # Since name, price, and date are the same for all these rows,
    # we just grab them from the first row (index 0)
    fabric_name = rows[0][0]
    price = rows[0][3]
    entry_date = rows[0][1]

    # 4. Extract all colors into a list
    # We loop through every row and take the 4th column (index 3)
    colors_list = []
    color_name = ""
    color_price = []
    color_entry_date = []
    color_id_list = []
    for r in rows:
        if r[2]:  # Ensure the color isn't NULL
            if not color_name:
                color_name = r[2]
            colors_list.append(r[2])
            color_price.append(r[3])
            color_entry_date.append(r[1])
            color_id_list.append(r[4])

    # 5. Print the HTML for each row
    for i, (c, p, d, color_id) in enumerate(zip(colors_list, color_price, color_entry_date, color_id_list), start=1):
        print(f"""
        <tr>
             <td>{c}</td>
            <td>{p}</td>
           <td>{d.strftime('%d-%m-%Y')}</td>

            <td class="text-end">

             <div class="d-flex justify-content-end gap-2"> 
             <button class="table-action-btn" 
              title="Edit"
                    data-bs-toggle="modal"
                    data-bs-target="#editColorModal"
                    value="{color_id}"
                    onclick="setEditModalData('{color_id}', '{c}', '{p}')"> <i class="bi bi-pencil"></i> </button> 
                    
                    <button class="table-action-btn" onclick="deleteFabric('{color_id}')">
                    <i class="bi bi-trash"></i></button> </div> </td> </tr> """)
else:
    print("""
    <div class="alert alert-danger">
        Fabric not found
    </div>
    """)

cursor.close()
conn.close()