from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import socket
    
host = socket.gethostname()
fromaddr = "crawler@janalasser.at"
toaddr = "jana.lasser@tugraz.at"
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = f"[WARNING] sampled stream terminated on {host}!"

body = ""
with open("get_sampled_stream_err.txt", "r") as f:
    for l in f.readlines():
        body += l + "\n"

msg.attach(MIMEText(body, 'plain'))

email_credentials = {}
with open("email_credentials.txt", "r") as f:
    for line in f.readlines():
        line = line.strip("\n")
        email_credentials[line.split("=")[0]] = line.split("=")[1]

server = smtplib.SMTP(email_credentials["server"], int(email_credentials["port"]))
server.ehlo()
server.starttls()
server.ehlo()
server.login(email_credentials["user"], email_credentials["password"])
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)