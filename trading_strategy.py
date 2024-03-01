import FinanceDataReader as fdr
from datetime import datetime, timedelta

def find_all_time_high(symbol, start_date, end_date):
    # 주식 데이터 불러오기
    data = fdr.DataReader(symbol, start_date, end_date)

    # 종가 기준으로 전고점 찾기
    high_price = data['Close'].max()
    high_date = data['Close'].idxmax()

    return {'price':high_price, 'date': high_date}

# 전고점 찾는 코드
# 구간을 나누어서 이전 구간 고점보다 크면 전고점이라고 판단
def find_prev_high_point(code, start_date):

    #start_date = '2024-01-15'
    start_date = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    querter1_date = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
    querter2_date = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=14)).strftime('%Y-%m-%d')
    querter3_date = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=21)).strftime('%Y-%m-%d')
    end_date = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=28)).strftime('%Y-%m-%d')

    res = []

    res.append(find_all_time_high(code, querter1_date, start_date))
    res.append(find_all_time_high(code, querter2_date, querter1_date))
    res.append(find_all_time_high(code, querter3_date, querter2_date))
    res.append(find_all_time_high(code, end_date, querter3_date))


    if res[0]['price'] > res[1]['price']:
        high_point = res[0]
    elif res[1]['price'] > res[2]['price']:
        high_point = res[1]
    elif res[2]['price'] > res[3]['price']:
        high_point = res[2]
    else:
        high_point = res[3]
    
    return high_point


def find_prev_close_price(code, today):
    start_date = (datetime.strptime(today, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    data = fdr.DataReader(code, start_date, start_date)
    return data['Close']


print(find_prev_close_price('005380','2024-02-02'))
