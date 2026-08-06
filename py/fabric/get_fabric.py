#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgitb
import cgi
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

form = cgi.FieldStorage()

fab_id = form.getvalue("fab_id")

cursor.execute("""
SELECT 
    f.name,
    fc.color_name
FROM fabrics f
LEFT JOIN fabric_colors fc
ON f.id = fc.fabric_id
WHERE f.id=%s
""", (fab_id,))

row = cursor.fetchone()

if row:

    print(f"""
    <script>

        document.getElementById("fabric_id").value = "{fab_id}";

        document.getElementById("fabric_name").value = "{row[0]}";

        document.getElementById("fabric_color").value = "{row[1]}";

    </script>
    """)

else:

    print(f"""
    <script>
    alert("Received ID: {fab_id}");
    </script>
    """)

cursor.close()
conn.close()

# NOW I AM NOT USE THIS FILE ANYMORE
