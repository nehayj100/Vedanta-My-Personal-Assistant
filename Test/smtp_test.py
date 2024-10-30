import smtplib
from email.mime.text import MIMEText

password_path = "confidential/pass.txt"
# Open and read the file
with open(password_path, 'r') as file:
    passkey = file.read()  # Read the entire content of the file
print(passkey)

smtp_server = "smtp.gmail.com"
smtp_port = 587
username = "nehayjoshi98@gmail.com"
password = f"{passkey}"
from_addr = "nehayjoshi98@gmail.com"
to_addr = "vedantjoshi370@gmail.com"
subject = "Test Email"
body = "This is a test email."

message = MIMEText(body)
message["From"] = from_addr
message["To"] = to_addr
message["Subject"] = subject

try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(username, password)
        server.sendmail(from_addr, to_addr, message.as_string())
        print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
