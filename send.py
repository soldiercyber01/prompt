import smtplib
from email.mime.text import MIMEText

sender = "hardikv682@gmail.com"
receiver = "sgnarutokun@gmail.com"
password = "tdowmwwzregmftcb"  # ⚠️ space hata do

msg = MIMEText("This is a test email from Python using Gmail App Password.")
msg["Subject"] = "SMTP Test"
msg["From"] = sender
msg["To"] = receiver

# Use SSL (port 465)
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(sender, password)
    server.send_message(msg)

print("✅ Email sent successfully!")
