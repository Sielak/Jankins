from ping3 import ping
from datetime import datetime, date, timedelta
import time
import json


with open('config.json') as data_file:
    config = json.load(data_file)

def make_ping(filename):
    host = config['host']
    ping_result = ping(host, unit='ms')
    with open(f"data/{filename}.csv", "a") as myfile:
        myfile.write("{0};{1};{2}\n".format(datetime.now(), host, ping_result))


start_time = datetime.now()
finish_time = start_time + timedelta(hours=config['duration'])

print("### Initialize script ####")
print("Start time:", start_time)
print("Finish time:", finish_time)
print("Ping START")
print("___________________________")
while True:
    if finish_time < datetime.now():
        print("Finish time exceeded.")
        break
    else:
        make_ping(finish_time.strftime("%Y-%m-%d"))
        time.sleep(1)
