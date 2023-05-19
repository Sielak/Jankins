import pyodbc
import datetime
from decimal import Decimal
import time


class SqlQueries:
    def __init__(self, database_name, db_server):
        # Connects to SQL server DB
        self.server = db_server
        self.database = database_name
        cnxn = pyodbc.connect(driver='{SQL Server}', server=self.server,
                              database=self.database, trusted_connection='yes')
        self.cursor = cnxn.cursor()

    def _change_customer_order_number(self, order_number):
        query = """
        UPDATE
            oh
        SET
            kundbestnr = '30000876_test_old'
        WHERE
            oh.ordernr = '{order_number}'
            and oh.ForetagKod = 1710
        """.format(order_number=order_number)
        self.cursor.execute(query)
        self.cursor.commit()

    def prepare_data_in_jeeves(self):
        query = """
        SELECT
            ordernr
        FROM
            oh
        WHERE
            oh.ordstat = 10
            AND oh.kundbestnr = '30000876_test'
            AND oh.foretagkod = 1710
        """
        self.cursor.execute(query)
        order_list = self.cursor.fetchall()
        for item in order_list:
            self._change_customer_order_number(item[0])
        return 'OK'

    def _fetch_order_number(self, customer_order_number):
        query = """
        SELECT
            ordernr
        FROM
            oh
        WHERE
            oh.ordstat = 10
            AND oh.kundbestnr = '{customer_order_number}'
            AND oh.foretagkod = 1710
        """.format(customer_order_number=customer_order_number)
        self.cursor.execute(query)
        results = self.cursor.fetchone()
        if results is not None:
            return results[0]
        return results

    def _fetch_order_header_data(self, order_number):
        query = """
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
            ,oh.q_ordbeglevdat_cust 
            ,oh.q_ordberlevdat_cust
            ,oh.q_ordlovlevdat_cust
            ,oh.kundbestdat
        FROM
            oh
        WHERE
            oh.ordstat = 10
            AND oh.OrderNr = '{order_number}'
            AND oh.foretagkod = 1710
        """.format(order_number=order_number)
        self.cursor.execute(query)
        columns = [column[0] for column in self.cursor.description]
        results = []
        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results[0]

    def _fetch_order_rows_data(self, order_number):
        query = """
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
            orp.OrderNr = '{order_number}'
            AND orp.foretagkod = 1710
        """.format(order_number=order_number)
        self.cursor.execute(query)
        columns = [column[0] for column in self.cursor.description]
        results = []
        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results

    def _check_order_header(self, order_number, customer_order_number):
        order_data = self._fetch_order_header_data(order_number)
        date1 = order_data['q_ordbeglevdat_cust']
        date2 = order_data['q_ordberlevdat_cust']
        date3 = order_data['q_ordlovlevdat_cust']
        date4 = order_data['kundbestdat']
        for key in ['q_ordbeglevdat_cust', 'q_ordberlevdat_cust', 'q_ordlovlevdat_cust', 'kundbestdat']:
            order_data.pop(key)
        expected_header = {
            "ftgnr": "19604",
            "kundbestnr": customer_order_number,
            "kundref2": "2271",
            "OrdLevPlats1": "29260",
            "ordstat": 10,
            "salestype": "17",
            "kundfraktdeb": "0",
            "ordertextkod": None,
            "godsmarke1": None,
            "godsmarke2": None,
            "edit": None,
            "prislista": 3,
            "q_hl_sendttlinkemail": None,
            "lagstalle": "0",
            "ordtyp": 1,
            "momskod": 0,
            "q_salesmarket_code": "UK",
            "q_hl_emailtt": None
        }
        if order_data != expected_header:
            print("Data on order header is not correct")
            print("----------------LOG----------------")
            print("Jeeves data:")
            print(order_data)
            print("Expected data:")
            print(expected_header)
            return False
        if date4 is None:
            print("Field kundbestdat is empty")
            return False
        if date1 == date2 == date3:
            return True
        else:
            print("Fields with dates are not equal")
            print("----------------LOG----------------")
            print("q_ordbeglevdat_cust", date1)
            print("q_ordberlevdat_cust", date2)
            print("q_ordlovlevdat_cust", date3)

    def _check_order_rows(self, order_number):
        order_data = self._fetch_order_rows_data(order_number)
        expected_rows = [
            {
                "artnr": "596394",
                "ordantal": Decimal("100.000000"),
                "vb_pris": Decimal("29.5000"),
                "fsgprisper": 50.0,
                "ordradst": 10,
                "artnrkund": None,
                "ordtyp": 1,
                "lagstalle": "0",
                "q_hl_ord_comefrom": None,
                "momskod": 0,
                "altenhetkod": None,
                "ordantalaltenh": Decimal("0.000000"),
                "bestallas": "0"
            }
        ]
        if order_data == expected_rows:
            return True
        else:
            print("Data on order rows is not correct")
            print("----------------LOG----------------")
            print("Jeeves data:")
            print(order_data)
            print("Expected data:")
            print(expected_rows)
            return False

    def check_created_order(self, customer_order_number):
        max_retries = 5
        for run in range(0, max_retries):
            order_number = self._fetch_order_number(customer_order_number)
            if order_number is not None:
                break
            print("order not found. Sleeping for 60 sek...")
            time.sleep(60)
        if order_number is None:
            print("order not found")
            return [False]
        print("Order number found, checking order...")
        results = [
            self._check_order_header(order_number, customer_order_number),
            self._check_order_rows(order_number)
        ]
        return results


tesco_order = """
<cXML xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" payloadID="637606965229903994.8ecfead7a4d246bd9e704258fb5d42f1@RD00155D676FA7." timestamp="2021-07-01T00:35:22.9903994+00:00" xml:lang="en-us" version="1.2.025">
    <Header>
        <From>
            <Credential domain="30527">
                <Identity>30527</Identity>
            </Credential>
        </From>
        <To>
            <Credential domain="71222">
                <Identity>71222</Identity>
            </Credential>
        </To>
        <Sender>
            <Credential domain="30527">
                <Identity>30527</Identity>
                <SharedSecret/>
            </Credential>
            <UserAgent/>
        </Sender>
    </Header>
    <Request deploymentMode="PROD">
        <OrderRequest>
            <OrderRequestHeader orderID="{customer_order_number}" orderDate="2021-07-01T00:34:38.4870000+00:00" orderType="regular" type="new">
                <Total>
                    <Money currency="GBP">59.0000</Money>
                </Total>
                <ShipTo>
                    <Address addressID="2271">
                        <Name xml:lang="en-us">Cheshunt Metro</Name>
                        <PostalAddress>
                            <DeliverTo>Denise Hannam</DeliverTo>
                            <Street>64-66 Turners Hill</Street>
                            <Street>Cheshunt</Street>
                            <City>Waltham Cross</City>
                            <State>Other</State>
                            <PostalCode>EN8 8LQ</PostalCode>
                            <Country isoCountryCode="GB">GB</Country>
                        </PostalAddress>
                        <Email>UK2271@tesco.com</Email>
                        <Phone>
                            <TelephoneNumber>
                                <CountryCode isoCountryCode="GB">00</CountryCode>
                                <AreaOrCityCode>00</AreaOrCityCode>
                                <Number>000</Number>
                            </TelephoneNumber>
                        </Phone>
                    </Address>
                </ShipTo>
                <BillTo>
                    <Address addressID="BU3">
                        <Name xml:lang="en-us">UK</Name>
                        <PostalAddress>
                            <Street>Shire Park</Street>
                            <Street>Kestral Way</Street>
                            <City>Welwyn Garden City</City>
                            <State>Other</State>
                            <PostalCode>AL7 1GA</PostalCode>
                            <Country isoCountryCode="GB"/>
                        </PostalAddress>
                    </Address>
                </BillTo>
                <Shipping>
                    <Money currency="GBP">0.0000</Money>
                    <Description xml:lang="en-us">Total Shipping</Description>
                </Shipping>
                <Tax>
                    <Money currency="GBP">0.0000</Money>
                    <Description xml:lang="en-us">Total Tax</Description>
                </Tax>
                <PaymentTerm payInNumberOfDays="30"/>
                <Contact role="buyer">
                    <Name xml:lang="en-us">Denise Hannam</Name>
                    <Email>UK2271@tesco.com</Email>
                    <Phone>
                        <TelephoneNumber>
                            <CountryCode isoCountryCode="">00</CountryCode>
                            <AreaOrCityCode>00</AreaOrCityCode>
                            <Number>000</Number>
                        </TelephoneNumber>
                    </Phone>
                </Contact>
                <Contact role="orderingLocation" addressID="GBP-5112-HRL1">
                    <Name xml:lang="en-us">UK</Name>
                    <PostalAddress>
                        <Street>1-2 Horsecroft Road</Street>
                        <Street>The Pinnacles</Street>
                        <City>Harlow</City>
                        <State>Other</State>
                        <PostalCode>CM19 5BH</PostalCode>
                        <Country isoCountryCode="GB">United Kingdom</Country>
                    </PostalAddress>
                    <Email>Kay.Phillips@hl-display.com</Email>
                    <Phone>
                        <TelephoneNumber>
                            <CountryCode isoCountryCode="GB">00</CountryCode>
                            <AreaOrCityCode>00</AreaOrCityCode>
                            <Number>01652 682148</Number>
                        </TelephoneNumber>
                    </Phone>
                </Contact>
                <Comments xml:lang="en-us"/>
                <Extrinsic name="HeaderExtrinsic">
                    <HeaderExtrinsic>
                        <BUCode>2271</BUCode>
                        <IsPCardSupported>false</IsPCardSupported>
                        <Barcode>30000876_test123</Barcode>
                    </HeaderExtrinsic>
                </Extrinsic>
            </OrderRequestHeader>
            <ItemOut quantity="2.0000" lineNumber="1" requestedDeliveryDate="2021-07-11T12:00:00.0000000+00:00">
                <ItemID>
                    <SupplierPartID>596394</SupplierPartID>
                </ItemID>
                <ItemDetail>
                    <UnitPrice>
                        <Money currency="GBP">29.5000</Money>
                    </UnitPrice>
                    <Description xml:lang="en-us">AEROFOIL BUBBLE CLIP PK50</Description>
                    <UnitOfMeasure>PK</UnitOfMeasure>
                    <Classification domain="UNSPSC">0</Classification>
                    <Extrinsic name="PR No.">REQUK00000000443</Extrinsic>
                    <Extrinsic name="IsCatalog">false</Extrinsic>
                </ItemDetail>
                <ShipTo>
                    <Address addressID="2271">
                        <Name xml:lang="en-us">Cheshunt Metro</Name>
                        <PostalAddress>
                            <DeliverTo>Denise Hannam</DeliverTo>
                            <Street>64-66 Turners Hill</Street>
                            <Street>Cheshunt</Street>
                            <City>Waltham Cross</City>
                            <State>Other</State>
                            <PostalCode>EN8 8LQ</PostalCode>
                            <Country isoCountryCode="GB">GB</Country>
                        </PostalAddress>
                        <Email>UK2271@tesco.com</Email>
                        <Phone>
                            <TelephoneNumber>
                                <CountryCode isoCountryCode="GB">00</CountryCode>
                                <AreaOrCityCode>00</AreaOrCityCode>
                                <Number>000</Number>
                            </TelephoneNumber>
                        </Phone>
                    </Address>
                </ShipTo>
                <Shipping trackingDomain="Best Available">
                    <Money currency="GBP">0.0000</Money>
                    <Description xml:lang="en-us">Total Shipping</Description>
                </Shipping>
                <Tax>
                    <Money currency="GBP">0.0000</Money>
                    <Description xml:lang="en-us">Total Tax</Description>
                </Tax>
                <Comments xml:lang="en-us"/>
            </ItemOut>
        </OrderRequest>
    </Request>
</cXML>
"""
