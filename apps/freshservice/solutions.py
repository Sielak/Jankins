import sqlite3 as sql
import requests
import json
import csv   

# basic data
db_path = "freshservice.db"
api_key = "Zpll1RafGc3UY8CoSRV"
URL = "https://hldisplayab.freshservice.com/api/v2/"
password = "x"
conn = sql.connect(db_path)
cursor = conn.cursor()


def fetch_categories():
    r = requests.get(URL + "solutions/categories?per_page=100", auth=(api_key, password))
    if r.status_code == 200:
        response_raw = json.loads(r.content)
        response = response_raw['categories']
        for item in response:
            category_id = item['id']
            category_name = item['name']
            print("CATEGORY", category_id, category_name)
            cursor.execute("INSERT INTO solution_category VALUES (?, ?);", (category_id, category_name))
            conn.commit()
    else:
        print("Failed to read tickets, errors are displayed below,")
        print(r)
        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))

def fetch_folders(category_id):
    r = requests.get(URL + "solutions/folders?category_id={0}&per_page=100".format(category_id), auth=(api_key, password))
    if r.status_code == 200:
        response_raw = json.loads(r.content)
        response = response_raw['folders']
        for item in response:
            folder_id = item['id']
            folder_name = item['name']
            print("FOLDER", folder_id, folder_name, category_id)
            cursor.execute("INSERT INTO solution_folder VALUES (?, ?, ?);", (folder_id, folder_name, category_id))
            conn.commit()
    else:
        print("Failed to read tickets, errors are displayed below,")
        print(r)
        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))

def fetch_articles(folder_id, category_id):
    r = requests.get(URL + "solutions/articles?folder_id={0}&per_page=100".format(folder_id), auth=(api_key, password))
    if r.status_code == 200:
        response_raw = json.loads(r.content)
        response = response_raw['articles']
        for item in response:
            art_id = item['id']
            art_name = item['title']
            created_at = item['created_at']
            views = item['views']
            thumbs_up = item['thumbs_up']
            thumbs_down = item['thumbs_down']
            inserted_into_tickets = item['inserted_into_tickets']
            print("Article", art_id, art_name, created_at, views, thumbs_up, thumbs_down, inserted_into_tickets)
            cursor.execute("INSERT INTO solution_article VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", (art_id, art_name, category_id, folder_id, thumbs_up, thumbs_down, inserted_into_tickets, views, created_at))
            conn.commit()
    else:
        print("Failed to read tickets, errors are displayed below,")
        print(r)
        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))

def get_categories():
    cursor.execute("SELECT id FROM solution_category;")
    return cursor.fetchall()

def get_folders():
    cursor.execute("SELECT id, category_id FROM solution_folder;")
    return cursor.fetchall()

def clear_db():
    cursor.execute("DELETE FROM solution_category;")
    conn.commit()
    cursor.execute("DELETE FROM solution_folder;")
    conn.commit()
    cursor.execute("DELETE FROM solution_article;")
    conn.commit()

def save_result2csv(filename):
    sql_command = """
    SELECT 
        a.id,
        b.name as category_name,           
        c.name as folder_name,
        a.name,
        thumbs_up,
        thumbs_down,
        inserted_into_tickets,
        views,
        created_at,
        a.category_id,
        a.folder_id
    FROM 
        solution_article a
    JOIN 
        solution_category b on a.category_id = b.id
    JOIN 
        solution_folder c on a.folder_id = c.id;
    """
    cursor.execute(sql_command)
    res = cursor.fetchall()
    
    fields=[
    'id',
    'category_name',           
    'folder_name',
    'name',
    'thumbs_up',
    'thumbs_down',
    'inserted_into_tickets',
    'views',
    'created_at',
    'category_id',
    'folder_id'
    ]
    with open(f"{filename}.csv", 'w', newline='\n', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for item in res:
            writer.writerow(item)

clear_db()
fetch_categories()
for item in get_categories():
    fetch_folders(item[0])
for item in get_folders():
    fetch_articles(item[0], item[1])
save_result2csv("out_new")
conn.close()
