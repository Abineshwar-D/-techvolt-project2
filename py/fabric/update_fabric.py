#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import cgi
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

form = cgi.FieldStorage()


fab_id = form.getvalue("fab_id")
fabric_name = form.getvalue("fabric_name")


print(f"""
<script>
console.log("ID: {fab_id}");
console.log("NAME: {fabric_name}");
</script>
""")


result1 = cursor.execute(
    """
    UPDATE fabrics 
    SET name=%s 
    WHERE id=%s
    """,
    (fabric_name, fab_id)
)


conn.commit()


print(f"""
<script>
alert("Fabric Updated\\nID={fab_id}\\nRows: {result1}");
</script>
""")


cursor.close()
conn.close()