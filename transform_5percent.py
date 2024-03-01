import pandas as pd
import sqlite3
from datetime import datetime, timedelta

df = pd.read_excel('explit_data/trade_money_per_day.xlsx')

# db 연결
db_file_path = '../total_price.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

over_5percent = []

i=0
for index, row in df.iterrows():
    i+=1
    print(f"{round(i/df.shape[0]*100,2)}%", end='\r')
    cur_date = pd.to_datetime(row['date'], format='%Y%m%d')
    prev_date = cur_date - timedelta(days=1)
    
    cursor.execute(f"SELECT * FROM {row['code']} WHERE date LIKE '{prev_date.strftime("%Y%m%d")+'15'}%';")
    prev_close = cursor.fetchall()
    
    cursor.execute(f"SELECT * FROM {row['code']} WHERE date LIKE '{cur_date.strftime("%Y%m%d")+'15'}%';")
    cur_close = cursor.fetchall()
    
    if len(prev_close)==0 or len(cur_close)==0:
        chgrate = 0
    else:
        chgrate = round((cur_close[-1][4] - prev_close[-1][4])/prev_close[-1][4]*100,1)
    
    if chgrate > 5.0:
        over_5percent.append(pd.DataFrame({'date':[row['date']], 'code':[row['code']], 'trade_money':[row['trade_money']], 'chgrate':[chgrate]}))

df = pd.concat(over_5percent)
df.to_excel('explit_data/trade_money_per_day_over5percent.xlsx', index=False)