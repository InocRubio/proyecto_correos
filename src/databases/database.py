from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SERVER = config('REPORT_BD_SERVER')
DATABASE = config('REPORT_BD_DATABASE')
USERNAME = config('REPORT_BD_USER')
PASSWORD = config('REPORT_BD_PASS')
DRIVER = 'ODBC Driver 11 for SQL Server'
URI = f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}"


class DBConnection:
    def __init__(self):
        self.engine = create_engine(URI)
        self.Session = sessionmaker(bind=self.engine)
