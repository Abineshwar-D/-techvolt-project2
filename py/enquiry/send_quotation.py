#!C:\Users\abi\AppData\Local\Programs\Python\Python311\python.exe
import cgi
import pymysql
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("Content-Type: application/json\n")

form = cgi.FieldStorage()
enq_id = form.getvalue("enquiry_id")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abineshwar68@gmail.com"
SENDER_PASSWORD = "pjlo yemf queh tfrl"


def calculate_quotation(enq_data):

    color_price = float(enq_data['price']) if enq_data['price'] else 0.0
    quantity = float(enq_data['quantity']) if enq_data['quantity'] else 0.0

    subtotal = color_price * quantity
    gst_half = subtotal * 0.9
    gst_secondhalf = subtotal * 0.9
    gst_amount = subtotal * 0.18
    total_amount = subtotal + gst_amount

    return {
        "unit_price": color_price,
        "subtotal": subtotal,
        "gst": gst_amount,
        "gst_half": gst_half,
        "gst_secondhalf": gst_secondhalf,
        "total": total_amount
    }


try:
    db = pymysql.connect(host="localhost", user="root", password="", database="techvoltproject2",
                         cursorclass=pymysql.cursors.DictCursor)
    cursor = db.cursor()

    cursor.execute("SELECT * FROM customers_enquiries WHERE enquiry_id = %s", (enq_id,))
    enq = cursor.fetchone()

    if not enq:
        print(json.dumps({"status": "error", "message": "Enquiry not found"}))
        exit()

    prices = calculate_quotation(enq)

    msg = MIMEMultipart()
    msg['From'] = f"Techvolt Sales <{SENDER_EMAIL}>"
    msg['To'] = enq['email']
    msg['Subject'] = f"Official Quotation - {enq['enquiry_id']}"

    # Updated HTML content with Quotation Details appended
    html_content = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; border: 1px solid #eee; padding: 30px; max-width: 700px; color: #333;">
        <h2 style="text-align: center; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">QUOTATION</h2>

        <table style="margin-bottom: 20px; border-collapse: collapse; text-align: left; width: 100%; max-width: 600px;">
    <tr>
        <!-- Left Column: Sender Details -->
        <td style="padding: 5px 30px 5px 0; vertical-align: top; width: 50%;">
            <p style="margin: 5px 0;"><strong>Sender:</strong> {SENDER_EMAIL}</p>
            <p style="margin: 5px 0;"><strong>Sender Company:</strong>TechVolt</p>
            <p style="margin: 5px 0;"><strong>Sender GST No:</strong>45HSJQ5381SH5BS3Z7</p>
        </td>
        <!-- Right Column: Customer Details -->
        <td style="padding: 5px 0; vertical-align: top; width: 50%;">
            <p style="margin: 5px 0;"><strong>Customer:</strong> {enq['customer_name']}</p>
            <p style="margin: 5px 0;"><strong>GST No:</strong> {enq['gst_number']}</p>
            <p style="margin: 5px 0;"><strong>Company:</strong> {enq['company_name']}</p>
        </td>
    </tr>
</table>

        <table style="width:100%; border-collapse: collapse; margin-top: 20px; font-size: 14px;">
            <thead>
                <tr style="background-color: #f8f9fa; border-bottom: 2px solid #dee2e6; text-align: left;">
                    <th style="padding: 12px; border: 1px solid #ddd;">Fabric Type</th>
                    <th style="padding: 12px; border: 1px solid #ddd;">Quantity</th>
                    <th style="padding: 12px; border: 1px solid #ddd;">Price Per Kg</th>
                    <th style="padding: 12px; border: 1px solid #ddd;">Total Price</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 12px; border: 1px solid #ddd;">{enq['fabric_type']} ({enq['color']})</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">{enq['quantity']} Kg</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">₹{prices['unit_price']:.2f}</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">₹{prices['subtotal']:.2f}</td>
                </tr>
            </tbody>
        </table>

        <div style="margin-top: 30px; border-top: 1px solid #eee; padding-top: 15px;">
            <table style="width: 100%; text-align: right;">
                <tr>
                    <td style="padding: 5px 0; color: #7f8c8d;">Subtotal:</td>
                    <td style="padding: 5px 0; width: 120px;"><strong>₹{prices['subtotal']:.2f}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 5px 0; color: #7f8c8d;">GST (9%):</td>
                    <td style="padding: 5px 0;"><strong>₹{prices['gst_half']:.2f}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 5px 0; color: #7f8c8d;">GST (9%):</td>
                    <td style="padding: 5px 0;"><strong>₹{prices['gst_half']:.2f}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 5px 0; color: #7f8c8d;">GST (18%):</td>
                    <td style="padding: 5px 0;"><strong>₹{prices['gst']:.2f}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 15px 0; font-size: 18px; color: #27ae60;">Grand Total:</td>
                    <td style="padding: 15px 0; font-size: 18px; color: #27ae60;"><strong>₹{prices['total']:.2f}</strong></td>
                </tr>
            </table>
        </div>

        <!-- Footer Section -->
        <div style="margin-top: 40px; font-size: 12px; color: #95a5a6; text-align: center; border-top: 1px solid #eee; padding-top: 10px;">
            <p>This is an electronically generated quotation. Terms and conditions apply.</p>
            <p style="margin-top: 5px;">For any queries, please contact us at {SENDER_EMAIL}</p>
        </div>
    </div>
    """
    msg.attach(MIMEText(html_content, 'html'))

    # Send Email
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, enq['email'], msg.as_string())
    server.quit()

    # Update status to 2 (Quotation Sent)
    cursor.execute("UPDATE customers_enquiries SET sample_status = 2 WHERE enquiry_id = %s", (enq_id,))
    db.commit()

    print(json.dumps({"status": "success", "email": enq['email']}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
finally:
    if 'db' in locals(): db.close()