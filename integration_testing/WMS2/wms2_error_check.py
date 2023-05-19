from help_functions import SqlQueries, Mail
import json
from models import BasicData


# load basic data file
with open('basic_data_prod.json') as data_file:
    json_data = json.load(data_file)
basic_data = BasicData(**json_data)

jeeves_object = SqlQueries(basic_data.database_name, basic_data.db_server)
result_1810 = jeeves_object.fetch_dp_data("1810")
result_1210 = jeeves_object.fetch_dp_data("1210")
result_1600 = jeeves_object.fetch_dp_data("1600")
recipants_1810 = [
    'pawel.nowak@hl-display.com', 
    'boguslaw.kuczynski@hl-display.com', 
    'christer.sahlen@hl-display.com', 
    'kinga.szygula@hl-display.com', 
    'krzysztof.mizielski@hl-display.com', 
    'Gliwice.Warehouse1@hl-display.com'
]
recipants_1210 = [
    'pawel.nowak@hl-display.com', 
    'dawid.wybierek@hl-display.com', 
    'ida.modigh@hl-display.com', 
    'christer.sahlen@hl-display.com',
    'Marcin.Mikolajczyk@hl-display.com'
]
recipants_1600 = [
    'pawel.nowak@hl-display.com', 
    'stephane.carrivain@hl-display.com', 
    'erwan.lardic@hl-display.com', 
    'arnaud.pichonniere@hl-display.com', 
    'christer.sahlen@hl-display.com'
]
print(Mail(recipants_1810).integration_errors(result_1810, "1810"))
print(Mail(recipants_1210).integration_errors(result_1210, "1210"))
print(Mail(recipants_1600).integration_errors(result_1600, "1600"))
