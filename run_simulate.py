import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import sqlite3

db_path = 'explit_data/trade_money_per_day_5min.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

over_5percent_data = pd.read_excel('explit_data/trade_money_per_day_over5percent.xlsx')

# 시작 날짜, 종료 날짜, 현재 날짜
start_date = datetime(2024, 1, 3)
end_date = datetime(2024, 2, 20)
cur_date = start_date

# 주말, 공휴일 예외 처리
weekend_days = [5,6]
public_holidays = [datetime(23,12,29),datetime(2023,12,25),datetime(2024,1,1),datetime(2024,2,9),datetime(2024,2,12)]

# 시뮬레이션 총 실행 횟수, 종가 성공 횟수, 시가 성공 횟수, 종가 수익률, 시가 수익률
total_cnt = 0
close_success_cnt = 0
open_success_cnt = 0
close_chg_data = []
open_chg_data = []

            
# 시작
while cur_date < end_date:
    # 날짜 형식에 맞게 변환
    cur_date_strftime = cur_date.strftime("%Y%m%d") 
    cur_date_data = over_5percent_data[over_5percent_data['date']==int(cur_date_strftime)].reset_index(drop=True)

    nxt_date = cur_date + timedelta(days=1)    
    while nxt_date.weekday() in weekend_days or nxt_date in public_holidays:
        nxt_date = nxt_date + timedelta(days=1)
        
    for i in range(cur_date_data.shape[0]):

        code = cur_date_data['code'][i]
        date = cur_date_data['date'][i]
    
        
        cursor.execute(f"SELECT close FROM total_close WHERE code='{code}' AND day='{date}';")
        cur_close_price = cursor.fetchall()[0][0]
        
        profit = 3
        loss = -1
        
        profit_price = cur_close_price * (1 + 0.01*profit)
        loss_price = cur_close_price * (1 - 0.01*loss)
        
        cursor.execute(f"SELECT * FROM {code} WHERE date LIKE '{nxt_date.strftime("%Y%m%d")}%';")
        rows = cursor.fetchall()
        chgrate = 0
        
        if len(rows)==0:
            continue
        else:
            total_cnt += 1
        
        # for row in rows:
        #     h, l = row[2], row[3]
        #     if l < loss_price:
        #         chgrate = loss
        #         break
        #     elif h > profit_price:
        #         chgrate = profit
        #         break
        

        open_chgrate = round((rows[0][1] - cur_close_price)/cur_close_price*100, 1)
        close_chgrate = round((rows[-1][4] - cur_close_price)/cur_close_price*100, 1)
        
        open_chg_data.append(open_chgrate)
        close_chg_data.append(close_chgrate)

        # if chgrate == 0:
        #     chgrate = round((rows[-1][4] - cur_close_price)/cur_close_price*100, 1)
        #     print(rows[-1][4], cur_close_price)
        
        # if chgrate > 0:
        #     close_success_cnt += 1
        
        # close_chg_data.append(chgrate)
        
        if open_chgrate > 0:
            print(f"{cur_date}, {code}, 결과 : {open_chgrate}%")
            open_success_cnt +=1
        if close_chgrate > 0:
            close_success_cnt += 1 
            
        # print(f"{cur_date}, {code}, 목표가 : {profit_price}, 손절가 : {loss_price}, 결과 : {chgrate}%")
    
    cur_date = nxt_date
        

    
    
    



# 결과 출력
print(f"총 횟수: {total_cnt}")
print(f"시가 성공 횟수: {open_success_cnt}")
print(f"종가 성공 횟수: {close_success_cnt}")
print(f"시가 승률: {open_success_cnt/total_cnt*100:.1f}")
print(f"종가 승률: {close_success_cnt/total_cnt*100:.1f}")

data1_m = 100
data2_m = 100

data1_sum = 0
data2_sum = 0

for i in close_chg_data:
    data1_m = data1_m*(1+i*0.01)    
    data1_sum += i
    
for i in open_chg_data:
    data2_m = data2_m*(1+i*0.01)    
    data2_sum += i
    
print(f"close++: {data1_m}, close_fixed: {data1_sum}")
print(f"open++: {data2_m}, open_fixed: {data2_sum}")

print(close_chg_data)
print(open_chg_data)


# 결과 시각화
plt.subplot(1, 2, 1)
plt.hist(close_chg_data, edgecolor='black', alpha=0.7, label='Data 1')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('Histogram of Close Data')

plt.subplot(1, 2, 2)
plt.hist(open_chg_data, label='Data 2')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('Histogram of Open Data')


plt.tight_layout()
plt.show()