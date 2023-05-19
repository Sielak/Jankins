import csv
import pandas as pd
import os
from tqdm import tqdm
from datetime import datetime, date


def rows2list(filename):
    results = []
    with open(filename) as file:
        csv_reader = csv.reader(file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if row[2] == 'None':
                results.append(line_count-1)
                results.append(line_count)
                results.append(line_count+1)
            line_count += 1
        # print(f'Processed {line_count} lines.')

    return results

def save2csv(filename, row_list):
    df = pd.read_csv(filename, header=None, delimiter=";")
    df = df.iloc[row_list]
    # print(df)
    df.to_csv('timeouts.csv', mode = 'a', index = False, header=False)


# mass conversion
# for item in tqdm(os.listdir('C:/jenkins/apps/ping_info/data/')):
#     row_locations = rows2list(f'data/{item}')
#     save2csv(f'data/{item}', row_locations)
    
# convert 1 file
filename = date.today().strftime("%Y-%m-%d")
try:
    row_locations = rows2list(f'data/{filename}.csv')
    save2csv(f'data/{filename}.csv', row_locations)
except FileNotFoundError:
    pass
