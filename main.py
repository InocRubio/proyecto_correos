from src.services.sales_service import SaleService
import src.constants.user_constant as constraint
import schedule
import time

class Main:
    def __init__(self) -> None:
        email_data = constraint.USER_SEND_EMAIL[0]
        
        self.to = email_data["to"]
        self.title = email_data["title"]
        self.message = email_data["message"]
        self.cc = email_data["cc"]
        self.attachment = email_data["attachment"]

        self.sale_service = SaleService(
            to = self.to,
            title = self.title,
            message = self.message,
            cc = self.cc,
            attachment = self.attachment
        )
        
        
    def process (self):
        try:
            
            self.sale_service.save_excel()
            
        except Exception as e:
            raise e
        
    def schedule_email(self):
        schedule.every().monday.at("09:00").do(self.process)
        print("Programador de correos iniciado...")

        while True:
            schedule.run_pending()
            time.sleep(60) 

Main().process()
