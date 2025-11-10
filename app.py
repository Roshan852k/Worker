import json
import smtplib as s
from email.message import EmailMessage
from credential import cred_username, cred_password

from redis_conn import rc

pubsub = rc.pubsub()
pubsub.subscribe('email_channel')

print("Email worker started. Listening for tasks...")

for message in pubsub.listen():
    if message['type'] == 'message':
        task = json.loads(message['data'])
        email = task['email']
        order_id = task['order_id']
        customer_name = task['customer_name']
        store_name = task['store_name']
        tracking_link = task['tracking_link']

        try:
            msg = EmailMessage()
            msg['Subject'] = 'Your {store_name} Order Placed : {order_id}'.format(store_name = store_name, order_id = order_id)
            # msg['From'] = cred_username
            msg['From'] = "{store_name} <{cred_username}>".format(store_name = store_name, cred_username = cred_username)
            msg['To'] =  email
            msg['Cc'] = [""]

            msg.add_alternative('''\
                    <!DOCTYPE html>
                    <html>
                    <body style="font-family: Arial, sans-serif; color: #333;">
                        <p>Dear {customer_name},</p>

                        <p>Thank you for shopping at <strong>{store_name}</strong>.</p>

                        <p>Your order <strong>{order_id}</strong> has been successfully placed.</p>

                        <p>To track your order status, please click the link below:</p>
                        <p><a href="{tracking_link}" target="_blank">{tracking_link}</a></p>

                        <p>You can also view order details anytime in your account's <strong>Order History</strong> section on <strong>{store_name}</strong>.</p>

                        <p style="color: gray; font-size: 0.9em;">
                            Note: This is a system-generated email. Please do not reply to this email.
                        </p>

                        <p>Warm regards,<br>{store_name} Team</p>
                    </body>
                    </html>
                    '''.format(customer_name = customer_name, store_name = store_name, order_id = order_id, tracking_link = tracking_link), subtype='html')

            # Mail Parameters
            with s.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(cred_username, cred_password)
                smtp.send_message(msg)
                print("Sent Mail Successfully")
                smtp.quit()

        except Exception as e:
            print(f"Failed to send email to {email}: {e}")
            # Push back into Redis for retry
            rc.publish('email_channel', json.dumps(task))