#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe

import pymysql
import cgitb

cgitb.enable()

print("Content-Type: text/html\n")

con = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="techvoltproject2"
)

cur = con.cursor()

cur.execute("""SELECT sample_no FROM samples""")

sample = cur.fetchall()

for i in sample:
    print(f"""<option value="{i[0]}">{i[0]}</option>""")
    

