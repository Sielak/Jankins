import pandas as pd

df = pd.read_csv("timeouts.csv", delimiter=";")
df['time'] = pd.to_datetime(df['time'])
df['date'] = pd.to_datetime(df['date'])
# print(df)
print(f"Analysis from {str(df['date'].min())[:10]} to {str(df['date'].max())[:10]}")
print("Data frame length:", len(df))
print("Avarage:", str(df['time'].mean())[11:])
print("Max:", str(df['time'].max())[11:])
print("Min:", str(df['time'].min())[11:])