import base64
import os
import sys
import json
import requests
import pyodbc
import orders
import dictdiffer
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple


@dataclass
class Config:
    """Model that represents config"""    
    integration_url: str
    customers: List[Dict[Any, Any]]


class Helpers:
    """Class with method that helps performing E2E Tests"""
    def __init__(self) -> None:
        with open('config.json') as data_file:
            config_raw = json.load(data_file) 
            self.config = Config(**config_raw)

    def get_config(self) -> Config:
        return self.config

    def fetch_db_config_from_integration(self) -> Dict[str, str]:
        """Method used to fetch information about database and server configured in test integration

        Returns:
            Dict[str, str]: Dictionary with sb server name and db name
        """        
        db_server = ''
        database = ''
        r = requests.get(self.config.integration_url + "/config",auth=("admin", "2Ljr.M!/E,Bk?}a5"))
        for item in r.json():
            if item['name'] == "database_server":
                db_server = item["value"]
            elif item['name'] == "database_name":
                database = item["value"]
        return {'db_server': db_server, 'database': database}

    def fetch_base64_string_from_file(self, filename: str) -> str:
        """Method used to read content of base64 file

        Args:
            filename (string): file name to open

        Returns:
            string: content of file
        """
        with open(f"files_base64/{filename}", 'r') as file:
            return file.read()

    def prepare_data(self, cso_email: str) -> bool:
        """Function used to prepare data about customers in integration db

        Args:
            cso_email (str): email where order result will be sent

        Returns:
            bool: True if customer was updated, False otherwise
        """        
        result = True
        for item in self.config.customers:
            item['sales_team_email'] = cso_email
            r = requests.put(self.config.integration_url + "/customers", json=item)
            if r.status_code == 404:
                r = requests.post(self.config.integration_url + "/customers", json=item)
            if r.status_code != 202:
                result = False
        return result

    def search4config(self, customer_name: str) -> Optional[Dict[str, str]]:
        """Method used to fetch customer configuration from file

        Args:
            customer_name (string): name of customer

        Returns:
            JSON: Json object with customer config. None if not found
        """
        customer_config = None
        for item in self.config.customers:
            if item['name'] == customer_name:
                customer_config = item
        return customer_config

    def create_order(self, customer_name, email_subject, filename, file_base64):
        """Method used to create order in Jeeves using integration

        Args:
            customer_name (string): name of customer
            email_subject (string): email subject
            filename (string): attachment file name with extension
            file_base64 (string): base64 string representation of file

        Returns:
            JSON: Json object with result of order creation
        """
        data = {
            "name": customer_name,
            "subject": email_subject,
            "filename": filename,
            "contentBytes": str(file_base64)
        }
        r = requests.post(f"{self.config.integration_url}/create_order", json=data)
        return r.json()

    def convert2base64(self):
        """Method used to convert all files in folder `files` to base64 in folder `files_base64`
        """
        for filename in os.listdir("files"):    
            with open(f"files/{filename}", 'rb') as file:
                file_content = file.read()
            base64_one = base64.b64encode(file_content)    
            out_file = filename.split(".")[0]
            with open(f"files_base64/{out_file}.b64", 'wb') as out_file:
                out_file.write(base64_one)

    def delete_all_base64_files(self):
        """Method used to delete all files in folder `files_base64`
        """
        for filename in os.listdir("files_base64"):    
            os.remove(f"files_base64/{filename}")

def _choose_customer(customer_name: str, pod_header: str = '') -> Dict[str, Any]:
    """Helper method to choose proper order results based on 
    customer name and PoD if many orders was created

    Args:
        customer_name (str): Name of customer
        pod_header (str, optional): Customer PoD number. Defaults to ''.

    Returns:
        Dict[str, Any]: Dictionary with expected results for header and rows
    """    
    if customer_name == "Auchan":
        expected_header = orders.Auchan.header
        expected_rows = orders.Auchan.rows
    elif customer_name == "Carrefour":
        expected_header = orders.Carrefour.header
        expected_rows = orders.Carrefour.rows
    elif customer_name == "ICA":
        expected_header = orders.ICA.header
        expected_rows = orders.ICA.rows
    elif customer_name == "SGruppen":
        expected_header = orders.SGruppen.header
        expected_rows = orders.SGruppen.rows
    elif customer_name == "SystemU":
        expected_header = orders.SystemU.header
        expected_rows = orders.SystemU.rows
    elif customer_name == "Rewe":
        if pod_header == '102188':
            expected_header = orders.Rewe.header_102188
            expected_rows = orders.Rewe.rows_102188
        elif pod_header == '93625':
            expected_header = orders.Rewe.header_93625
            expected_rows = orders.Rewe.rows_93625
        else:
            expected_header = {}
            expected_rows = []
    elif customer_name == "Willys":
        expected_header = orders.Willys.header
        expected_rows = orders.Willys.rows
    else:
        expected_header = {}
        expected_rows = []
    expected_results = {
        "header": expected_header,
        "rows": expected_rows
    }
    return expected_results


class Jeeves:
    def __init__(self, db_config: Dict[str, str]) -> None:
        """Class used to communicate with Jeeves DB

        Args:
            db_config (Dict): Dictionary with db server name and database name
        """        
        self.db_server = db_config['db_server']
        self.database = db_config['database']
        self.orders = {
            "1810":[
                "EP3341592",
                "PL200-CDA1042150",
                "PL200-CDA1042726",
                "22BPT/400732"
            ],
            "1210": ["IO590110", "PO00150958", "F40090152/D221100"],
            "1600": ["000205088"]
        }
    
    def _connect_to_sql_server(self) -> pyodbc.connect:
        """Method used to connect to MS SQL DB

        Returns:
            pyodbc.connection: Connection object used for query db
        """
        # Connects to SQL server DB
        if sys.platform == 'linux':
            cnxn = pyodbc.connect(driver='{ODBC Driver 17 for SQL Server}',server=self.db_server, database=self.database, uid='hlit2', pwd='hlit2')
        else:
            cnxn = pyodbc.connect(driver='{SQL Server}', server=self.db_server, database=self.database, trusted_connection='yes')
        return cnxn

    def _fetch_orders(self, ForetagKod: str, order_number: str) -> List[Tuple[Any]]:
        """Method used to fetch order numbers with given customer order number

        Args:
            ForetagKod (string): id of company where search will be done
            order_number (string): customer order number

        Returns:
            list: List of pyodbc.row
        """        
        cnxn = self._connect_to_sql_server()
        cursor = cnxn.cursor()
        sql = """
        SELECT 
            ordernr 
        FROM 
            oh 
        WHERE 
            ForetagKod = {ForetagKod} 
            and KundBestNr = '{order_number}'
        """.format(ForetagKod=ForetagKod, order_number=order_number)
        cursor.execute(sql)
        orders = cursor.fetchall()

        return orders

    def _change_customer_order_number(self, ForetagKod: str, order_number: str) -> None:
        """Method used to change customer order number for given order in Jeeves

        Args:
            ForetagKod (string): id of company where update will be done
            order_number (string): order number
        """
        cnxn = self._connect_to_sql_server()
        cursor = cnxn.cursor()
        sql = """
        UPDATE 
            oh
        SET
            KundBestNr = 'test_order'
        WHERE
            ForetagKod = {ForetagKod}
            AND OrderNr = '{order_number}'
        """.format(ForetagKod=ForetagKod, order_number=order_number)
        cursor.execute(sql)
        cnxn.commit()

    def prepare_data_in_jeeves(self, print_only: bool = False) -> None:
        """Main method used to prepare data in Jeeves for test
        """
        for foretagkod, order_list in self.orders.items():
            for order in order_list:
                orders = self._fetch_orders(foretagkod, order)
                for item in orders:
                    if item[0] is not None:
                        if print_only is True:
                            print(item[0], foretagkod)
                        else:
                            self._change_customer_order_number(foretagkod, item[0])
        print("Database used:", self.database)
        print("data in jeeves prepared")

    def _fetch_data_about_order_heder(self, ForetagKod:str, order_number: str) -> Dict[str, Any]:
        """Method used to fetch data from Jeeves about given order header

        Args:
            ForetagKod (string): id of company where search will be done
            order_number (string): order number to check

        Returns:
            dict: dict with column names as keys and data as values
        """        
        cnxn = self._connect_to_sql_server()
        cursor = cnxn.cursor()
        sql = """
        SELECT 
            ftgnr
            ,kundbestnr
            ,kundref2
            ,OrdLevPlats1
            ,ordstat
            ,salestype
            ,kundfraktdeb
            ,ordertextkod
            ,godsmarke1
            ,godsmarke2
            ,edit
            ,prislista
            ,q_hl_sendttlinkemail
            ,lagstalle
            ,ordtyp
            ,momskod
            ,q_salesmarket_code
            ,q_hl_emailtt
        FROM
            oh
        WHERE
            ForetagKod = {ForetagKod}
            AND OrderNr = '{order_number}'
        """.format(ForetagKod=ForetagKod, order_number=order_number)
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results[0]

    def _fetch_data_about_order_rows(self, ForetagKod: str, order_number: str) -> List[Dict[str, Any]]:
        """Method used to fetch data from Jeeves about given order rows

        Args:
            ForetagKod (string): id of company where search will be done
            order_number (string): order number to check

        Returns:
            list: list of dicts with column names as keys and data as values
        """          
        cnxn = self._connect_to_sql_server()
        cursor = cnxn.cursor()
        sql = """
        SELECT 
            artnr
            ,ordantal 
            ,vb_pris 
            ,fsgprisper
            ,ordradst 
            ,artnrkund
            ,ordtyp
            ,lagstalle
            ,q_hl_ord_comefrom
            ,momskod
            ,altenhetkod
            ,ordantalaltenh
            ,bestallas
        FROM
            orp
        WHERE
            ForetagKod = {ForetagKod}
            AND OrderNr = '{order_number}'
        """.format(ForetagKod=ForetagKod, order_number=order_number)
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def check_order(self, order_info: str) -> bool:
        """Method used to check if order was created as expected in Jeeves  

        Args:
            order_info (string): order info with proper format (customer_name:ForetagKod:order_number)

        Return:
            bool: True if order was created correctly False if not.  
        """
        customer_name, ForetagKod, order_number = order_info.split(':')
        result = {
            "header": self._fetch_data_about_order_heder(ForetagKod, order_number),
            "rows": self._fetch_data_about_order_rows(ForetagKod, order_number)
        }
        expected_results = _choose_customer(customer_name, result['header']['OrdLevPlats1'])
        if expected_results == result:
            return True
        else:
            print(f"[ERROR] Diff for order {order_number} vs expected results")
            for diff in list(dictdiffer.diff(result, expected_results)):         
                print(diff)
            print("-------------------------")
            return False
