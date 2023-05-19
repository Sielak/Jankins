import json
import requests
import csv
import shutil

with open("config.json") as file:
    config = json.load(file)


for item in config['data']:
    if item['name'] == 'highlight_data':
        response = requests.get(item['api_url']).json()
        columns = [
            'row_id',
            'Subject_Group',
            'Responsible_person',
            'Completion_Date',
            'Action_status',
            'row_Group',
            'row_Area',
            'row_country',
            'row_Year'
        ]
        # Write columns and rows to CSV file
        with open('out.csv', 'w', newline='', encoding='utf-8') as fout:
            csv_file = csv.writer(fout)
            csv_file.writerow(columns)
            if len(response['Data']) != 0:
                for row in response['Data']:
                    line_content = [
                        row['row_id'],
                        row['Subject_Group'],
                        row['Responsible_person'],
                        row['Completion_Date'],
                        row['Action_status'],
                        row['row_Group'],
                        row['row_Area'],
                        row['row_country'],
                        row['row_Year']
                    ]
                    csv_file.writerow(line_content)

        shutil.move('out.csv', item['filepath'])
    elif item['name'] == 'pmo_data':
        response = requests.get(item['api_url']).json()
        columns = [
            'row_id',
            'location',
            'location_type',
            'initiative_type',
            'category',
            'subcategory',
            'initiative_product',
            'status',
            'implementation_deadline',
            'total_savings_actual',
            'total_savings_budget'
        ]
        # Write columns and rows to CSV file
        with open('out2.csv', 'w', newline='', encoding='utf-8') as fout:
            csv_file = csv.writer(fout)
            csv_file.writerow(columns)
            if len(response['Data']) != 0:
                for row in response['Data']:
                    line_content = [
                        row['row_id'],
                        row['location'],
                        row['location_type'],
                        row['initiative_type'],
                        row['category'],
                        row['subcategory'],
                        row['initiative_product'],
                        row['status'],
                        row['implementation_deadline'],
                        row['total_savings_actual'],
                        row['total_savings_budget']
                    ]
                    csv_file.writerow(line_content)

        shutil.move('out2.csv', item['filepath'])
