from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import datetime

class EmailService:
    def __init__(self) -> None:
        pass
    
    def get_current_date(self):
        return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    
    def send (self, to: list[str], title: str, message: str, cc: list[str] = [] , attachment: str | None = None) -> bool: 
        try:
            email_user = "multifuncional@lindcorp.pe"
            email_pass = "Lindcorp2025*"
            email_alias = "reportes.diario@lindcorp.pe"
        
            current_date = self.get_current_date()
            message_with_date = f"{message}\n\nFecha de envío: {current_date}"
        
            msg = MIMEMultipart()
            msg.attach(MIMEText(message_with_date, 'plain'))         
            
            if attachment is not None:
                attachment_path = f"src/files/xlsx/{attachment}" 
                attachmentFile = open(attachment_path, "rb")
                part = MIMEBase("application", "octet-stream")
                part.set_payload((attachmentFile).read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={attachment}")
                msg.attach(part)
            
            msg["From"] = f"{email_alias} <{email_user}>"
            msg['To'] = ', '.join(to)
            msg['Subject'] = title
            msg['Bcc'] = ", ".join(cc)
            
            all_recipients = to + cc
            # Enviar el correo electrónico
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(email_user, email_pass)
                server.sendmail(email_user, all_recipients, msg.as_string())
                print(server)
            
            return True
        except Exception as e:
            raise e
        