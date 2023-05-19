import smartsheet
import json
import pandas as pd
import plotly.figure_factory as ff
import shutil
from datetime import date, timedelta


# basic data
with open('config.json') as data_file:
    config = json.load(data_file)

def fetch_new_file():
    # Initialize client
    smartsheet_client = smartsheet.Smartsheet(config['smartsheet_api_key'])

    # Make sure we don't miss any errors
    smartsheet_client.errors_as_exceptions(True)

    smartsheet_client.Sheets.get_sheet_as_csv(
    config['sheet_id'], config['file_path'])

def prepare_data(debug=False):
    # prepare data freame
    df = pd.read_csv('IT Project list.csv')
    if debug is True:
        print(df)
    df = df.dropna(subset=['Start'])
    df = df.dropna(subset=['Project Name'])
    df = df.dropna(subset=['Prio'])
    df['Start'] = pd.to_datetime(df.Start, format="%d/%m/%y")
    df['Finish'] = pd.to_datetime(df.Finish, format="%d/%m/%y")
    df = df.fillna('NA')

    df1 = df[['Project Name', 'Start', 'Finish', 'Status', 'Prio', 'Sponsor']]
    df1 = df1[(df1.Status != 'Closed')]
    df1 = df1.sort_values('Prio', ascending=True)

    return df1
  
def create_chart():    
    df = prepare_data()
    df.rename(columns={'Project Name': 'Task'}, inplace=True)
    colors = {
        'Define/Planning': 'rgb(242, 200, 15)',
        'Executing': 'rgb(1, 184, 170)',
        'Review/Closing': 'rgb(74, 197, 187)',
        'Not Started': 'rgb(253, 98, 94)',
        'Pre-Study': 'rgb(166, 105, 153)',
        'Closed': 'rgb(53, 153, 184)',
        'NA': 'rgb(55, 70, 73)',
        'Proposal': 'rgb(223, 191, 191)',
        'Project Decision': 'rgb(223, 191, 191)',
        'On Hold': 'rgb(223, 191, 191)',
        'Pre Cab': 'rgb(223, 191, 191)',
        'Rumor': 'rgb(138, 212, 235)',
        'Rejected': 'rgb(55, 70, 73)'
    }
    colors_human_redable = {
        'Define/Planning': 'yellow',
        'Executing': 'green',
        'Review/Closing': 'greener',
        'Not Started': 'red',
        'Pre-Study': 'purple',
        'Closed': 'Boston blue',
        'NA': 'black',
        'Proposal': 'pink Flare',
        'Project Decision': 'pink Flare',
        'On Hold': 'pink Flare',
        'Pre Cab': 'pink Flare',
        'Rumor': 'light_blue',
        'Rejected': 'black'
    }
    fig = ff.create_gantt(df, colors=colors, index_col='Status', show_colorbar=True,
                      group_tasks=True, title="IT Project List")
    fig.update_xaxes(showgrid=True)
    # date for todays line
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    yesterday = today - timedelta(days=1) 
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    fig.add_shape(
        # Line Vertical
        dict(
            type="line",
            x0=yesterday_str,
            y0=0,
            x1=today_str,
            y1=13,
            line=dict(
                color="gray",
                width=3,
                dash="dot"
            )
    ))
    fig.layout.xaxis.rangeselector = None
    fig.write_image("images/IT_projects_status.png", width=1204, height=677)


def copy2sharepoint():
    shutil.move("images/IT_projects_status.png", config['onedrive_path'])


fetch_new_file()
# print(prepare_data(debug=True))
create_chart()
copy2sharepoint()
