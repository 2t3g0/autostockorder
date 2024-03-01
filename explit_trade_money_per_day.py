'''DB에서 원하는 기간동안 거래대금 상위 20개 종목 추출'''

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# 엑셀 저장 여부
save_excel = True

# fillna, ffillm bfill 경고 메세지 출력X
pd.set_option('future.no_silent_downcasting', True)

# SQLite 데이터베이스 연결
db_file_path = '../total_price.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()


# 종목코드들 추출
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'A%';")
tables = cursor.fetchall()

code_list = []
for table in tables:
    code_list.append(table[0])

# 시작/종료 날짜 설정
start_date = datetime(2024,1,2)
end_date = datetime(2024,2,27)
cur_date = start_date

# 결과 데이터 프레임 생성
res = pd.DataFrame(columns =['trade_money', 'code', 'date'])


# 해당 날짜의 종목의 거래대금을 계산해서 데이터프레임에 저장
while cur_date <= end_date:
    
    # 날짜 형식에 맞게 변환
    cur_date_strftime = cur_date.strftime("%Y%m%d") 
    
    # 공휴일, 주말 제외 처리
    weekend_days = [5,6]
    public_holidays = [datetime(23,12,29),datetime(2023,12,25),datetime(2024,1,1),datetime(2024,2,9),datetime(2024,2,12)]
    
    if cur_date.weekday() in weekend_days or cur_date in public_holidays:
        print(f"{cur_date.strftime("%Y-%m-%d")}/{end_date.strftime("%Y-%m-%d")} // 주말 or 공휴일")
        cur_date = cur_date + timedelta(days=1)
        continue
    
    df_list = []
    day_proceed = 0
    
    print(f"{cur_date.strftime("%Y-%m-%d")}/{end_date.strftime("%Y-%m-%d")}")
    for code in code_list:
        
        # 진행률
        day_proceed+=1
        print(f"{round(day_proceed/len(code_list)*100,2)}%", end='\r')
        
        # 해당하는 날짜의 해당 종목의 거래대금 계산 후 내림차순으로 정렬하여 상위 20개 저장
        query1 = f"SELECT SUM(volume*close) FROM {code} WHERE date LIKE '{cur_date_strftime}%'"
        df1 = pd.read_sql(query1, conn)
        df1['code'] = code
        df1['date'] = cur_date_strftime
        df1 = df1.rename(columns= {'SUM(volume*close)':'trade_money'})
        df1 = df1.fillna(0)
        df_list.append(df1)

    df_list = sorted(df_list, key=lambda df: df['trade_money'].iloc[0], reverse=True)
    df1 = df_list[:20] + [res]
    res = pd.concat(df1, ignore_index=True)
             
    cur_date = cur_date + timedelta(days=1)


if save_excel:
    # 데이터베이스 엑셀로 저장
    res.to_excel('explit_data/trade_money_per_day.xlsx', index=False)

# 연결 닫기
conn.close()