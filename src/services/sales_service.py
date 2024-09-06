from src.services.email_service import EmailService
from src.databases.database import DBConnection 
import pandas as pd
from sqlalchemy import text
import os

class SaleService:
    def __init__(self, to: list[str], title: str, message: str, cc: list[str] = [], attachment: str | None = None) -> None:
        self.to = to
        self.title = title
        self.message = message
        self.cc = cc
        self.attachment = attachment
        self.email = EmailService() 
        self.db_connection = DBConnection()
        
    def get_sales_tambo (self):
        session = self.db_connection.Session()
        try:
            query = text("""
                            WITH VentaDiariaPromedio AS (
                                SELECT 
                                    A.IdTienda,
                                    TdaNombre,
                                    DATEDIFF(DAY, TdaFechaApertura, GETDATE()) AS DiasApertura,
                                    DATEPART(DAYOFYEAR, GETDATE()) AS DiasTranscurridos,
                                    SUM(VentaSinIGV) AS VentaTotal,
                                    -- Calcular el menor entre los días que la tienda ha estado abierta y los días transcurridos en el año
                                    CASE 
                                        WHEN DATEDIFF(DAY, TdaFechaApertura, GETDATE()) < DATEPART(DAYOFYEAR, GETDATE()) 
                                        THEN DATEDIFF(DAY, TdaFechaApertura, GETDATE()) 
                                        ELSE DATEPART(DAYOFYEAR, GETDATE()) 
                                    END AS DiasReferencia
                                FROM  
                                    BDBI_COM2019.dbo.Fact_Venta_2019 A
                                LEFT JOIN 
                                    BDBI.dbo.Tienda B ON A.IdTienda = B.IdTienda 
                                LEFT JOIN 
                                    BDBI.dbo.Producto C ON C.IdProducto = A.IdProducto
                                WHERE 
                                    (TdaClasifOper LIKE 'SSS%' OR TdaClasifOper = 'Nuevas')
                                    AND DptoProd NOT IN ('GASTOS', 'OFIC.MOLINA')
                                    AND IdModalidad IN (0, 106, 109)
                                    AND IdTiempo >=  (YEAR(GETDATE()) - 2000) * 10000 + 101
                                GROUP BY 
                                    A.IdTienda,
                                    TdaNombre,
                                    TdaFechaApertura
                            )
                            SELECT 
                                IdTienda,
                                TdaNombre,
                                DiasReferencia,
                                RANK() OVER (ORDER BY VentaTotal / CAST(DiasReferencia AS DECIMAL(10,2)) DESC) AS Ranking
                            FROM 
                                VentaDiariaPromedio
                            ORDER BY 
                                Ranking;
                         """)
            
            result = session.execute(query)
            df = pd.DataFrame(result.fetchall(), columns = result.keys())
            
            return df
        
        except Exception as e:
            raise e
            
    def get_sales_aruma (self):
        session = self.db_connection.Session()
        try:
            query = text("""
                            WITH VentaDiariaPromedio AS (
                                SELECT 
                                    A.IdTienda,
                                    TdaNombre,
                                    DATEDIFF(DAY, TdaFechaApertura, GETDATE()) AS DiasApertura,
                                    DATEPART(DAYOFYEAR, GETDATE()) AS DiasTranscurridos,
                                    SUM(VentaSinIGV) AS VentaTotal,
                                    -- Calcular el menor entre los días que la tienda ha estado abierta y los días transcurridos en el año
                                    CASE 
                                        WHEN DATEDIFF(DAY, TdaFechaApertura, GETDATE()) < DATEPART(DAYOFYEAR, GETDATE()) 
                                        THEN DATEDIFF(DAY, TdaFechaApertura, GETDATE()) 
                                        ELSE DATEPART(DAYOFYEAR, GETDATE()) 
                                    END AS DiasReferencia
                                FROM  
                                    BDBI_ARU.dbo.Fact_Venta A
                                LEFT JOIN 
                                    BDBI_ARU.dbo.Tienda B ON A.IdTienda = B.IdTienda 
                                LEFT JOIN 
                                    BDBI_ARU.dbo.Producto C ON C.IdProducto = A.IdProducto
                                WHERE 
                                    (TdaClasifOper LIKE 'SSS%' OR TdaClasifOper = 'Nuevas')
                                    AND DptoProd NOT IN ('GASTOS', 'OFIC.MOLINA', 'BOLSAS', 'OTROS', 'REGALOS', 'TESTERS')
                                    AND IdModalidad IN (0)
                                    AND IdTiempo >=  (YEAR(GETDATE()) - 2000) * 10000 + 101
                                GROUP BY 
                                    A.IdTienda,
                                    TdaNombre,
                                    TdaFechaApertura
                            )
                            SELECT 
                                IdTienda,
                                TdaNombre,
                                DiasReferencia,
                                RANK() OVER (ORDER BY VentaTotal / CAST(DiasReferencia AS DECIMAL(10,2)) DESC) AS Ranking
                            FROM 
                                VentaDiariaPromedio
                            ORDER BY 
                                Ranking;
                         """)
            
            result = session.execute(query)
            df = pd.DataFrame(result.fetchall(), columns = result.keys())
            
            return df
            
        except Exception as e:
            raise e
        
    def save_excel(self):
        try:
            print("Obteniendo datos Tambo ...")
            df_tambo = self.get_sales_tambo()
            print("Obteniendo datos Aruma ...")
            df_aruma = self.get_sales_aruma()

            if df_tambo.empty or df_aruma.empty:
                print("Los datos obtenidos están vacíos.")
                return
            
            output_dir = os.path.abspath("src/files/xlsx")
            os.makedirs(output_dir, exist_ok = True)

            if not self.attachment:
                self.attachment = "reporte.xlsx" 

            file_path = os.path.join(output_dir, self.attachment)
            print(f"Guardando archivo en: {file_path}")

            with pd.ExcelWriter(file_path, engine = 'openpyxl') as writer:
                df_tambo.to_excel(writer, sheet_name = "Tambo", index = False)
                df_aruma.to_excel(writer, sheet_name = "Aruma", index = False)

            self.email.send(
                self.to,
                self.title,
                self.message,
                self.cc,
                self.attachment
            )
            print("Archivo enviado correctamente")

        except Exception as e:
            raise
