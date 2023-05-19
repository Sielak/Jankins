import pyodbc


def connect_to_sql_server(database_name, db_server):
    # Connects to SQL server DB
    server = db_server
    database = database_name
    cnxn = pyodbc.connect(driver='{SQL Server}', server=server, database=database, trusted_connection='yes')
    return cnxn


def fetch_data_from_jeeves(reference_number):
    select_order = """
    SELECT
        ordernr
        ,xsal.salestypedescr
        ,x7.ordstatbeskr
    FROM
        oh
        join x7 on oh.ForetagKod = x7.ForetagKod and oh.OrdStat = x7.OrdStat
        join xsal on oh.ForetagKod = xsal.ForetagKod and oh.SalesType = xsal.SalesType
    WHERE
        oh.ForetagKod = 1600
        and oh.kundbestnr = '{0}'
    """.format(reference_number)
    cnxn = connect_to_sql_server('ErpTst001', 'EW1-SQL-711')
    cursor = cnxn.cursor()
    cursor.execute(select_order)
    order_info = cursor.fetchall()
    if len(order_info) == 0:
        order_info = ('xxx', 'ERROR', 'Order not found')
        return order_info
    elif len(order_info) > 1:
        order_info = ('xxx', 'ERROR', 'Too many orders')
        return order_info
    elif len(order_info) == 1:
        return order_info[0]
    else:
        order_info = ('xxx', 'ERROR', 'Unknown error')
        return order_info
        
def count_order_rows(order_nr):
    count_rows = """
    SELECT
        artnr
    FROM
        orp
    WHERE
        OrderNr = '{order_number}'
        and ForetagKod = 1600
        -- get rid of fright cost  
        and artnr <> '900000'
        -- get rid of bom items
        and OrdRadNrStrPos = 0   
    """.format(order_number=order_nr)
    cnxn = connect_to_sql_server('ErpTst001', 'EW1-SQL-711')
    cursor = cnxn.cursor()
    cursor.execute(count_rows)
    row_info = cursor.fetchall()
    rows_list = [elem for elem in row_info]
    if len(row_info) == 2:
        return 'OK'
    elif len(row_info) == 3 :
        if row_info[2][0] == '900000':
            return 'OK'
        else:
            row_info = ('ERROR', 'Too many rows', order_nr)
            return row_info
    elif len(row_info) < 2:
        row_info = ('ERROR', 'Rows not created', order_nr)
        return row_info
    else:
        row_info = ('ERROR', 'Too many rows', order_nr)
        return row_info

def check_pricelist():
    price_list = """
    SELECT
        kus.prislista
    FROM
        kus
    WHERE
        kus.ftgnr = 147990 AND 
        kus.foretagkod = 1600
    """
    update_price_list = """
    UPDATE
        kus
    SET
        kus.prislista = 174
    WHERE
        kus.ftgnr = 147990 AND 
        kus.foretagkod = 1600
    """
    cnxn = connect_to_sql_server('ErpTst001', 'EW1-SQL-711')
    cursor = cnxn.cursor()
    cursor.execute(price_list)
    price_list_info = cursor.fetchone()
    if price_list_info[0] != 174:
        print("price list is wrong, changing")
        cursor.execute(update_price_list)
        cursor.commit()
    else:
        print("price list is ok")

    
        
        
# a = count_order_rows('171559')
# print(a)
# check_pricelist()
