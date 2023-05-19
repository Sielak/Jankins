import pyodbc


def connect_to_sql_server(database_name, db_server):
    # Connects to SQL server DB
    server = db_server
    database = database_name
    cnxn = pyodbc.connect(driver='{SQL Server}', server=server, database=database, trusted_connection='yes')
    return cnxn


def check_results(po_number):
    cnxn = connect_to_sql_server('ErpTst005', 'EW1-SQL-716')
    # Send statements to SQL
    cursor = cnxn.cursor()
    search_for_po_number = """
    SELECT
        bh.beststatkod 
    FROM
        bh
    WHERE
        foretagkod = 1810
        and bestnr = '{0}'
    """.format(po_number)
    cursor.execute(search_for_po_number)
    po_info = cursor.fetchone()

    return po_info[0]


def check_info_about_item(item_no):
    cnxn = connect_to_sql_server('ErpTst005', 'EW1-SQL-716')
    # Send statements to SQL
    cursor = cnxn.cursor()
    search_for_item_balances = """
    SELECT
        ars.LagStalle
        ,xb.lagplatsnamn
        ,1 
        ,ars.lagsaldo 
    FROM
        ars
        join xb on ars.ForetagKod = xb.ForetagKod and ars.LagStalle = xb.LagStalle
    WHERE
        ars.foretagkod = 1810
        and ars.ArtNr = '{0}'
        and ars.LagStalle = 0
    """.format(item_no)
    cursor.execute(search_for_item_balances)
    balance_info = cursor.fetchone()
    search_for_bin_info = """
    SELECT
        arsi.LagPlats
        ,arsi.lagsaldo
        ,arsi.bokatantal
    FROM
        arsi
    WHERE
        arsi.lagstalle = 0 AND 
        arsi.artnr = '{0}' AND  
        arsi.foretagkod = 1810 AND
        arsi.lagsaldo > 0
        """.format(item_no)
    cursor.execute(search_for_bin_info)
    bin_info = cursor.fetchone()
    item_info = {'balance_info': balance_info, 'bin_info': bin_info}

    return item_info


def compare_item_bin_info(wms_balance_info, jvs_balance_info):
    test_results_list = []
    for wms, jvs in zip(wms_balance_info, jvs_balance_info):
        if wms != jvs:  # compare wms and jeeves data
            if type(jvs) == 'int':  # sometimes there is mismatch in types so we need to change type
                if int(wms) != jvs:
                    print('NOT equal')
                    print('WMS:', wms, 'JVS', jvs)
                    test_results_list.append('NOK')
            elif type(jvs) == 'decimal.Decimal':  # sometimes there is mismatch in types so we need to change type
                if int(wms.replace(" ", "")) != int(jvs):
                    print('NOT equal')
                    print('WMS:', wms, 'JVS', jvs)
                    test_results_list.append('NOK')
    if 'NOK' in test_results_list:
        test_results = 'NOK'
    else:
        test_results = 'OK'

    return test_results
