import datetime
import json
from help_functions import connect_to_sql_server


def prepare_data_in_jeeves():
    cnxn = connect_to_sql_server('ErpTst005', 'EW1-SQL-716')
    # Send statements to SQL
    print('Connected to SQL DB')
    cursor = cnxn.cursor()
    create_po_header = """
    EXECUTE jeeves_init_insert_bh 
        @c_foretagkod = 1810, 
        @c_ftgnr = '1190', 
        @c_perssign = 'dawy', 
        @c_businessunit = '1810'
    """
    print('Create PO header')
    cursor.execute(create_po_header)
    cursor.commit()
    search_for_po_number = """
    SELECT TOP 1
        bestnr
    FROM
        bh
    WHERE
        ForetagKod = 1810
        and PersSign = 'dawy'
        and regdat = cast(getdate() as date)
    ORDER BY
        RowCreatedDt DESC
    """
    print('Retrieve PO number')
    cursor.execute(search_for_po_number)
    po_results = cursor.fetchone()
    po_number = po_results[0]
    today = datetime.date.today()
    create_po_row = """
    EXECUTE Jeeves_Init_Insert_bp 
        @c_foretagkod = 1810, 
        @c_ftgnr = '1190', 
        @c_perssign = 'dawy', 
        @c_businessunit = '1810', 
        @c_bestnr = {0}, 
        @c_artnr = '200088', 
        @c_bestradnr = 10, 
        @c_vb_inpris = 0.77,
        @c_bestberlevdat = '{1}',
        @c_bestrestant = 500,
        @c_bestant  = 500,
        @c_bestantextqty = 500,
        @c_minantalbest  = 500,
        @c_BestRestAntExtQty = 500,
        @c_beststatkod = 10
    """.format(po_number, today.strftime("%Y-%m-%d"))
    print('Create PO row')
    cursor.execute(create_po_row)
    cursor.commit()
    create_ict = """
    EXECUTE JEEVES_ICT_StockReplenishment_SPO_To_DSO 1810, 'hlit2', 999, {0}
    """.format(po_number)
    print('Run ICT')
    cursor.execute(create_ict)
    cursor.commit()
    print('retrieve order nr from PO')
    search_for_co_number = """
        SELECT
            bestnralfa
        FROM
            bh
        WHERE
            ForetagKod = 1810
            and bestnr = {0}
    """.format(po_number)
    cursor.execute(search_for_co_number)
    co_results = cursor.fetchone()
    po_number_alfa_raw = co_results[0]
    po_number_alfa_list = po_number_alfa_raw.split('<-')
    order_nr = po_number_alfa_list[1].strip()
    order_to_entered_status = """
    UPDATE oh SET ordstat = 13 WHERE oh.ordernr = {0} AND oh.ForetagKod = 1190
    """.format(order_nr)
    add_qty_on_stock = """
    EXECUTE Jeeves_Init_Insert_arsm
        @c_foretagkod = 1190,
        @c_perssign = 'dawy',
        @c_lagtranstyp = 900,
        @c_lagstalle = 0,
        @c_artnr = 200088, 
        @c_lagplats = 'fl',
        @c_lagtransinlev = 500
    """
    book_item_qty = """
    EXECUTE q_autobooking  
        1190,
        ' and orp.ordernr = {0} ',
        0,
        'order by orderbycol asc, delta asc, delta2 asc',
        '',
        1	
    """.format(order_nr)
    change_to_dispatch_started = """
    EXECUTE Jeeves_Init_Insert_oru
        @c_foretagkod = 1190,
        @c_ordernr = {0},
        @c_ordradnr = 10,
        @c_ordradnrstrpos = 0,
        @c_ordrestnr = 0,
        @c_lagstalle = 0,
        @c_ordlevantal = 500,
        @c_lagplats = 'fl',
        @c_perssign = 'dawy'
    """.format(order_nr)
    print('Change order status to entered in factory')
    cursor.execute(order_to_entered_status)
    cursor.commit()
    print('Add 500 pcs to stock in factory')
    cursor.execute(add_qty_on_stock)
    cursor.commit()
    print('Run booking on this order')
    cursor.execute(book_item_qty)
    cursor.commit()
    print('Change order status to dispatch started')
    cursor.execute(change_to_dispatch_started)
    cursor.commit()
    print('Data in Jeeves prepared')

    return po_number


with open('basic_data.json') as data_file:
    basic_data = json.load(data_file)
results = prepare_data_in_jeeves()
print('PO number:', results)
# update po number in config file
basic_data['po_number'] = results
with open("basic_data.json", "w") as jsonFile:
    json.dump(basic_data, jsonFile, indent=4, sort_keys=True)


