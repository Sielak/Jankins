import pyodbc
from datetime import date
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from playwright.sync_api import sync_playwright
from PIM_playwright import check_product_in_pim, change_product_in_pim, test


class SqlQueries:
    def __init__(self, config):
        # Connects to SQL server DB
        self.server = config['server']
        self.database = config['env']
        cnxn = pyodbc.connect(driver='{SQL Server}', server=self.server, database=self.database,
                              trusted_connection='yes')
        self.cursor = cnxn.cursor()
        self.process_id = ""

    def _delete_rows_in_dp_data(self):
        query = """
        DELETE FROM 
            q_hl_dp_data 
        WHERE 
            ProcesName = 'PIM2.0' 
            AND RowCreationDate >= CAST(GETDATE() AS DATE)
        """
        self.cursor.execute(query)
        self.cursor.commit()
        return 'OK'

    def clear_dp_data(self):
        query = """
        SELECT
            ProcesId
        FROM 
            q_hl_dp_data 
        WHERE 
            ProcesName = 'PIM2.0' 
            --AND ProcesType = 'PIMto1J' 
            AND RowCreationDate >= CAST(GETDATE() AS DATE)
        ORDER BY 
            RowCreationDate DESC
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        if len(results) > 0:
            self._delete_rows_in_dp_data()
        return 'OK'

    def change_product_data_in_jeeves(self, original_value=False):
        # q_productid = 346099
        # q_productnumber = 100550
        q_productdescription = "Auto test to PIM"
        q_hl_assortmenttypeid = "OTHER"
        q_hl_productstatusid = 	"Sellable"
        q_hl_productownerid = 51
        q_hl_trademarkid = "Next"
        artkod = 200
        q_product_func_id = "Alarm"
        itemtypecd1 = 1008
        if original_value is True:
            q_productdescription = "AS-ARM-SCSW-KIT"
            q_hl_assortmenttypeid = "GLOBAL"
            q_hl_productstatusid = 	"SellableAndMarketed"
            q_hl_productownerid = 3
            q_hl_trademarkid = "NONE"
            artkod = 200
            q_product_func_id = "Posterholder"
            itemtypecd1 = 1
        query = f"""
        UPDATE
            q_product
        SET
            q_product.q_productdescription = '{q_productdescription}'
            ,q_product.q_hl_assortmenttypeid = '{q_hl_assortmenttypeid}'
            ,q_product.q_hl_productstatusid = '{q_hl_productstatusid}'
            ,q_product.q_hl_productownerid = {q_hl_productownerid}
            ,q_product.q_hl_trademarkid = '{q_hl_trademarkid}'
            ,q_product.artkod = {artkod}
            ,q_product.q_product_func_id = '{q_product_func_id}'
            ,q_product.itemtypecd1 = {itemtypecd1}
        WHERE
            q_product.q_productid = '346099'
            AND q_product.foretagkod = 1
        """
        self.cursor.execute(query)
        self.cursor.commit()
        return 'OK'

    def check_product_data_in_jeeves(self):
        to_add = "q_hl_productheadline.sprakkod"
        query = """
        SELECT
            q_product.q_productdescription
            ,q_product.q_hl_assortmenttypeid
            ,q_product.q_hl_productstatusid
            ,q_product.q_hl_productownerid
            ,q_product.q_hl_trademarkid
            ,q_product.artkod
            ,q_product.q_hl_keyconceptid
            ,q_product.q_systemid
            ,q_hl_productheadline.q_hl_productHeadline
        FROM
            q_product
            join q_hl_productheadline 
            ON 
                q_product.ForetagKod = q_hl_productheadline.ForetagKod
                AND q_product.q_ProductID = q_hl_productheadline.q_ProductID
        WHERE
            q_product.q_productid = '346099'
            AND q_product.foretagkod = 1
            AND q_hl_productheadline.SprakKod = 999
        """
        self.cursor.execute(query)
        results = self.cursor.fetchone()
        jeeves_data = {
            "Name": results[0],
            "Assortment": results[1],
            "Status": results[2],
            "Owner": results[3],
            "Trademark": results[4],
            "ItemClass": results[5],
            "KeyConcept": results[6],
            "System": results[7],
            "ProductHeadline": results[8]
        }
        return jeeves_data

    def check_dp_data_created(self, pim2jeeves=False):
        proces_type = "1JtoPIM"
        text2 = "AND Text2 = '346099'"
        if pim2jeeves is True:
            proces_type = "PIMto1J"
            text2 = ""
        query = """
        SELECT top 1
            ProcesId
            ,Text2
            ,RowCreationDate
            ,ResultXML.value('(/Response/StatusNumber)[1]', 'varchar(max)') AS status
            ,EI
        FROM 
            q_hl_dp_data 
        WHERE 
            ProcesName = 'PIM2.0' 
            AND ProcesType = '{proces_type}' 
            {text2}
        ORDER BY 
            RowCreationDate DESC
        """.format(proces_type=proces_type, text2=text2)
        self.cursor.execute(query)
        results = self.cursor.fetchone()
        if results is None:
            print("Row in dp data not found")
            return False
        if len(results) != 5:
            print("Row in dp data not found")
            return False
        row_date = results[2].date()
        if date.today() != row_date:
            print("There is no row in dp data with todays date.")
            return False
        self.process_id = results[0]
        return True

    def check_dp_data_posted(self, pim2jeeves=False):
        # column = "ResultXML.value('(/Response/StatusNumber)[1]', 'varchar(max)') AS status"
        column = "ResultXML AS status"
        proces_type = "1JtoPIM"
        if pim2jeeves is True:
            column = "EI"
            proces_type = "PIMto1J"
        query = """
        SELECT
            {column}
        FROM 
            q_hl_dp_data 
        WHERE 
            ProcesName = 'PIM2.0' 
            AND ProcesType = '{proces_type}' 
            AND ProcesId = '{process_id}' 
        ORDER BY 
            RowCreationDate DESC
        """.format(column=column, proces_type=proces_type, process_id=self.process_id)
        self.cursor.execute(query)
        results = self.cursor.fetchone()
        if results is not None:
            return results[0]
        else:
            return results

class PimChecker:
    def __init__(self, config):
        self.config = config

    def check_product_data(self):
        with sync_playwright() as playwright:
            result = check_product_in_pim(playwright, self.config)
        print("Product in PIM have name: #{0}#".format(result["Name"]))

        return result

    def change_product_data(self, original_value=False):
        with sync_playwright() as playwright:
            change_product_in_pim(playwright, self.config, original_value)
        print("Product name changed to: Auto test to Jeeves")

    def test(self):
        with sync_playwright() as playwright:
            test(playwright, self.config)

# import json

# with open('config.json') as data_file:
#     config = json.load(data_file)

# test = PimChecker(config).test()
# query_object = SqlQueries(config)
# query_object.process_id = "865E714E-0D45-480B-AC95-E439B381EA0E"
# res = query_object.check_dp_data_posted()
# if res != None:
#     print("OK")
# else:
#     print("Field is empty")