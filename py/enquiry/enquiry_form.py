#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe
import cgi
import cgitb
import json
import pymysql

cgitb.enable()

# Detect parameters sent via AJAX
form = cgi.FieldStorage()
selected_fabric_id = form.getvalue("fabric_id")

# --- 1. Handle AJAX Request for Colors ---
if selected_fabric_id:
    print("Content-Type: application/json\n")
    try:
        con = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="techvoltproject2",
        )
        cur = con.cursor()

        # Query colors matching ONLY the selected fabric_id
        cur.execute(
            "SELECT DISTINCT color_name FROM fabric_colors WHERE fabric_id = %s ORDER BY color_name ASC",
            (selected_fabric_id,),
        )
        colors = [r[0] for r in cur.fetchall()]

        print(json.dumps(colors))
    except Exception as e:
        print(json.dumps([]))
    finally:
        con.close()
    exit()

# --- 2. Render HTML Output ---
print("Content-Type: text/html\n")

try:
    con = pymysql.connect(
        host="localhost", user="root", password="", database="techvoltproject2"
    )
    cur = con.cursor()

    # Fetch Fabrics (id and name)
    cur.execute("SELECT id, name FROM fabrics ORDER BY name ASC")
    fabrics = cur.fetchall()

    # value = fabric_id (for colors search)
    # data-name = fabric_name (for form submission)
    fabric_options = "".join(
        [
            f'<option value="{r[0]}" data-name="{r[1]}">{r[1]}</option>'
            for r in fabrics
        ]
    )

    print(f"""
        <div class="col-md-6">
            <label class="form-label-custom">Fabric Type</label>
            <!-- Select dropdown DOES NOT have name="fabric_type" now -->
            <select class="form-select-custom" id="fabric_type_select" onchange="fetchColors(this)" required>
                <option value="">Select Fabric</option>
                {fabric_options}
            </select>

            <!-- THIS hidden field will store and submit the actual NAME ("Cotton", "Silk") -->
            <input type="hidden" name="fabric_type" id="fabric_type_name">
        </div>

        <div class="col-md-6">
            <label class="form-label-custom">Color</label>
            <select class="form-select-custom" name="color" id="color1" required>
                <option value="">Select Color</option>
            </select>
        </div>
    """)
except Exception as e:
    print(f"Error loading options: {e}")
finally:
    con.close()