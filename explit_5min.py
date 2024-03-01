'''DB에서 원하는 종목의 원하는 날의 종가 데이터와 다음날의 데이터 정보를 5분봉으로 추출'''

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# 추출 종목코드 파일
data_code_df = pd.read_excel('explit_data/trade_money_per_day_over5percent.xlsx')
print(data_code_df)

# SQLite 데이터베이스 연결
db_file_path = '../total_price.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# 새로운 데이터베이스 연결
conn_new = sqlite3.connect('explit_data/trade_money_per_day_5min.db')
cursor_new = conn_new.cursor()

# 테이블 초기화
cursor_new.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor_new.fetchall()
for table in tables:
    cursor_new.execute(f"DROP TABLE {table[0]};")

cursor_new.execute(f"""CREATE TABLE IF NOT EXISTS total (
                            code TEXT,
                            day TEXT,
                            time TEXT,
                            open REAL,
                            high REAL,
                            low REAL,
                            close REAL,
                            volume REAL
                        );""")

cursor_new.execute(f"""CREATE TABLE IF NOT EXISTS total_close (
                            code TEXT,
                            day TEXT,
                            close REAL
                        );""")

# 데이터 종목 수만큼 분봉 추출 
for i in range(data_code_df.shape[0]):
    
    # 테이블 이름
    table_name = data_code_df.loc[i]['code']
    table_date = data_code_df.loc[i]['date']
    
    try:
        cursor.execute(f"SELECT date, close FROM {table_name} WHERE date LIKE '{table_date}%';")
        rows = cursor.fetchall()
        cursor_new.execute(f"INSERT INTO total_close VALUES (?, ?, ?);", (table_name, str(rows[-1][0])[:8], rows[-1][1]))
    except sqlite3.Error as e:
        print("no such code")

    table_date = pd.to_datetime(table_date, format='%Y%m%d')
    table_date = table_date + timedelta(days=1)
    weekend_days = [5,6]
    public_holidays = [datetime(23,12,29),datetime(2023,12,25),datetime(2024,1,1),datetime(2024,2,9),datetime(2024,2,12)]
    while table_date.weekday() in weekend_days or table_date in public_holidays:
        table_date = table_date + timedelta(days=1)
    table_date = table_date.strftime('%Y%m%d')
    
 
    
    # 테이블 생성
    cursor_new.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
                            date TEXT,
                            open REAL,
                            high REAL,
                            low REAL,
                            close REAL,
                            volume REAL
                        );""")

    # 기존 데이터베이스에서 데이터 추출하여 새로운 데이터베이스에 삽입

    try:
        cursor.execute(f"SELECT date, open, high, low, close, volume FROM {table_name} WHERE date LIKE '{table_date}%';")
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        print("no such code")
    # print(rows)
    
    # 추출한 데이터(1분봉)을 5분봉으로 합쳐서 삽입
    for i in range(0, len(rows)-5, 5):
        day = str(rows[i][0])[:8]
        time = str(rows[i][0])[-4:]
        date = rows[i][0]
        open = rows[i][1]
        high = max(rows[i][2], rows[i+1][2], rows[i+2][2], rows[i+3][2], rows[i+4][2])
        low = min(rows[i][3], rows[i+1][3], rows[i+2][3], rows[i+3][3], rows[i+4][3])
        close = rows[i+4][4]
        volume = rows[i][5] + rows[i+1][5] + rows[i+2][5] + rows[i+3][5] + rows[i+4][5]
        try:
            cursor_new.execute(f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?, ?);", (date, open, high, low, close, volume))
        except sqlite3.Error as e:
            print("new error")
            
        try:
            cursor_new.execute(f"INSERT INTO total VALUES (?, ?, ?, ?, ?, ?, ?, ?);", (table_name, day, time, open, high, low, close, volume))
        except sqlite3.Error as e:
            print("total error")
    

        

        


# # 테이블 목록 가져오기
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()

# print("Tables:")
# for table in tables:
#     print(table[0])


# # 테이블 내용 가져오기
# cursor.execute(f"SELECT * FROM {table_name};")
# rows = cursor.fetchall()

# # 헤더 출력
# cursor.execute(f"PRAGMA table_info({table_name});")
# columns = cursor.fetchall()
# header = [col[1] for col in columns]
# print(" | ".join(header))

# # 내용 출력
# for row in rows:
#     print(" | ".join(str(cell) for cell in row))



# 변경사항 저장
conn_new.commit()

# 데이터베이스에서 데이터를 가져와 데이터프레임으로 변환
query = "SELECT * FROM total;"
df = pd.read_sql_query(query, conn_new)

# 데이터베이스 엑셀로 저장
df.to_excel('explit_data/trade_money_per_day_5min.xlsx', index=False)

# 연결 닫기
conn.close()
conn_new.close()