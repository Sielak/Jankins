import pandas as pd


# config
filename = "C:/Users/poca/HL Display AB/IT Documentation Repository - CAB/CAB REQUESTS.xlsx"
# script 
pd.options.mode.chained_assignment = None
excel_file = pd.ExcelFile(filename)
print(excel_file.sheet_names)

sheet_names = ['Production', 'Supply Chain', 'Sales and Quotation', 'Marketing', 'Finance', 'HR', 'IT']


def excel2csv(filename, sheet_name):
    """
    Function to convert dataframe to csv with tab name
    """
    print(f"### Start conversion of {sheet_name} ###")
    out_filename = f"results/{sheet_name}.csv"
    data_frame = pd.read_excel(filename, sheet_name=sheet_name, header=2)
    data_frame = data_frame.replace('\n',' ', regex=True)
    data_frame = data_frame.dropna(how='all')
    values=['IMPLEMENTED','REJECTED', 'SENT TO PROJECT OFFICE', 'MOVED/DUPLICATED']
    mask = data_frame['Status'].isin(values)
    df = data_frame[~mask]
    # df = data_frame
    # convert dates
    try:
        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y")
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    except Exception as e:
        print("Cant convert column Date to proper format. Skipping")
        print("error:", e)
    try:
        df['Decision date'] = pd.to_datetime(df['Decision date'], format="%d/%m/%Y")
        df['Decision date'] = df['Decision date'].dt.strftime('%Y-%m-%d')
    except Exception as e:
        print("Cant convert column Decision date to proper format. Skipping")
        print("error:", e)
    try:
        df['Est Deliv\nDate'] = pd.to_datetime(df['Est Deliv\nDate'], format="%d/%m/%Y")
        df['Est Deliv\nDate'] = df['Est Deliv\nDate'].dt.strftime('%Y-%m-%d')
    except Exception as e:
        print("Cant convert column Est Deliv Date to proper format. Skipping")
        print("error:", e)
    columns = ['Status', 'Date', 'Requested By', 'Approved By', 'HL Unit', 'Product', 'Prio', 'Est Dev (hrs)', 'Est Cost\n(EUR)', 'Decision', 'Decision date', 'Est Deliv\nDate', 'Feature ID', 'Description', 'Justification', 'RFC Link']
    # print(df[columns])
    # print(df.columns)
    df = df.replace('\n',' ', regex=True)
    df[columns].to_csv(out_filename, index=False, header=['Status', 'Date', 'Requested By', 'Approved By', 'HL Unit', 'Product', 'Prio', 'Est Dev (hrs)', 'Est Cost (EUR)', 'Decision', 'Decision date', 'Est Deliv Date', 'Feature ID', 'Description', 'Justification','RFC Link'])


for item in sheet_names:
    excel2csv(filename, item)