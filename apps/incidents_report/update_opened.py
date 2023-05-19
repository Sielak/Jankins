from functions import connect_to_sql_server
import datetime


sql_command = """
SELECT 
    count(item_id) as items
FROM 
    [Reports].[dbo].[freshservice_tickets]
WHERE 
    item_status not in (4, 5)
"""
cursor = connect_to_sql_server('Reports').cursor()
cursor.execute(sql_command)
opened_count = cursor.fetchone()[0]
today = datetime.date.today()
cursor.execute("INSERT INTO open_yearly VALUES (?,?)", (today, opened_count))  # insert row
cursor.commit()
