import pyodbc

class SqlQueries:
    def __init__(self, database_name, db_server):
        # Connects to SQL server DB
        self.server = db_server
        self.database = database_name
        cnxn = pyodbc.connect(driver='{SQL Server}', server=self.server, database=self.database, trusted_connection='yes')
        self.cursor = cnxn.cursor()

    def update_item(self):
        query =  """
        UPDATE
            ar
        SET
            q_hl_es_pickclass = ''
            ,q_hl_es_vau = ''
            ,q_hl_es_stockeditem = 0
        WHERE
            ar.ArtNr = '200088'
            and ar.ForetagKod = 1600
        """
        self.cursor.execute(query)
        self.cursor.commit()
        results = 'OK'
        return results

    def fetch_po_data(self, filename_po): 
        query = """
        SELECT
            bp.artnr
            ,bp.bestantextqty
        FROM
            bp
            join bh on bp.ForetagKod = bh.ForetagKod and bp.BestNr = bh.BestNr
        WHERE
            bh.q_hl_es_filename = '{0}'
            AND bh.foretagkod = 1600
        """.format(filename_po)
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return results
