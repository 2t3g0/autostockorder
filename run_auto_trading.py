from stockorder import *
from stock_data import *
from stock_strategy import *
auth(svr='vps')
# do_buy("005930", 1, 0, order_type="01")

# 거래 대금 상위 항목 추출
df = get_trade_rank()

#상위 15개
df = df.head(15)
df.index = range(1,16)

# df에 섹터 정보를 추가
code_array =  df['code']
name_array = []
for i in code_array:
    name_array.append(find_sector_name(find_sector(i)))
df['sector'] = name_array
theme_array = []
for i in code_array:
    theme_array.append(find_theme(i))
df['theme'] = theme_array

# df 리턴 함수

def df_name(code):
    return df.loc[df['code']==code, 'name'].values[0]

def df_chgrate(code):
    return round(float((df.loc[df['code']==code, 'chgrate'].values[0]).strip()),1)

def df_trade_amt(code):
    return round(float(df.loc[df['code']==code, 'trade_amt'].values[0]),2)

# 거래대금 상위 종목 중 5% 이상인 것만 저장
df_code = df.copy()
df_code['chgrate'] = df_code['chgrate'].astype(float)
df_code = df_code[df_code['chgrate']>5]
df_code = df_code[['code','name']]
print(df_code)
df_sector_list = []
theme_rank_dic_list = []

# 5% 이상인 종목들의 테마를 정리
for code in df_code['code']:
    code_theme = find_theme(code)
    
    
    for part_code_theme in code_theme:
        found_thema = False
        for theme_rank_dic in theme_rank_dic_list:
            if theme_rank_dic['theme']==part_code_theme:
                theme_rank_dic['count'] += 1
                theme_rank_dic['code'].append(code)
                theme_rank_dic['trade_money'] += float(df.loc[df['code']==code, 'trade_amt'].values[0])
                found_thema = True
    
        if not found_thema:
            theme_rank_dic_list.append({'theme':part_code_theme, 'count':1, 'code':[code], 'trade_money': float(df.loc[df['code']==code, 'trade_amt'].values[0])})
                

# print(theme_rank_dic_list)
# 2개 이상인 테마에 한하여 거래대금이 가장 큰 테마를 주도 테마로 설정
# 주도 테마의 종목들중 상승률이 가장 큰 종목을 주도 종목으로 설정
leader_theme = []
for d in theme_rank_dic_list:
    if d['count'] >= 2:
        leader_theme.append(d)
        
for d in leader_theme:
    print(f'테마명: {d['theme']} 종목: ', end="")
    for code in d['code']:
        print(f'{df_name(code)}|{df_chgrate(code)}%', end=" ")
    print()
    
# print(leader_theme)
D0_stock_list=[]
D1_day_stock_list=[]
D1_overnight_stock_list=[]
D2_day_stock_list=[]
D2_overnight_stock_list=[]

if len(leader_theme):                                                   # 2개 이상의 테마가 있다면
    leader_theme.sort(key=lambda x: x['trade_money'], reverse=True)     # 테마들을 거래대금순으로 정렬
    leader_stock_list = []  
    for code in leader_theme[0]['code']:                                # 주도테마(거래대금이 가장 큰 테마)의 종목들을 변화율 크기로 정렬
        leader_stock_list.append({'code' :code, 'chgrate': df_chgrate(code)})
    leader_stock_list.sort(key=lambda x:x['chgrate'], reverse=True)

    print(f'현재 주도 테마는 {leader_theme[0]['theme']}입니다.')
    print(f'대장주는 {df_name(leader_stock_list[0]['code'])}입니다.')
    D0_stock_list.append(leader_stock_list[0]['code'])
else:
    print('현재 주도 테마는 없습니다.')

print(df)

# D0 전고점 돌파시 매수
print(D0_stock_list)
cur_price = get_current_price(D0_stock_list[0])['stck_prpr']
cur_price = int(cur_price)
prev_high_price = find_prev_high_point(D0_stock_list[0], '2024-02-02')

target_price = cur_price*1.05
loss_price = cur_price*0.95
if cur_price > prev_high_price['price']:
    do_buy(D0_stock_list[0],1,0)
    
# D0 5% 수익시 매도 , -5% 손실시 매도
if cur_price > target_price or cur_price < loss_price:
    do_sell(D0_stock_list[0],1,0)
    D0_stock_list.pop(0)

# D0 -> D1
D1_day_stock_list = D0_stock_list.copy()
D1_overnight_stock_list = D0_stock_list.copy()


# D1 overnight 5% 수익시 매도, 시초가 갭하락시 매도
cur_price = get_current_price(D1_overnight_stock_list[0])['stck_prpr']
prev_close_price = find_prev_close_price(D1_overnight_stock_list[0])
target_price = prev_close_price*1.05
loss_price = prev_close_price*0.99

if cur_price <= prev_close_price:
    do_buy(D1_overnight_stock_list[0],1,0)
    
if cur_price > target_price or cur_price < loss_price:
    do_sell(D1_overnight_stock_list[0],1,0)
    D1_overnight_stock_list.pop(0)
    

# D1 day 종가 매수 5% 수익시 매도, -1% 손절

cur_price = get_current_price(D1_day_stock_list[0])['stck_prpr']
prev_close_price = find_prev_close_price(D1_day_stock_list[0])
target_price = prev_close_price*1.05
loss_price = prev_close_price*0.99

if cur_price <= prev_close_price:
    do_buy(D1_day_stock_list[0],1,0)
    
if cur_price > target_price or cur_price < loss_price:
    do_sell(D1_day_stock_list[0],1,0)
    D1_day_stock_list.pop(0)
    
# D1 -> D2
D2_day_stock_list = D1_day_stock_list.copy()
D2_overnight_stock_list = D1_overnight_stock_list.copy()

# D2 overnight 5% 매도 -3% 매도
cur_price = get_current_price(D2_overnight_stock_list[0])['stck_prpr']
prev_close_price = find_prev_close_price(D2_overnight_stock_list[0])
target_price = prev_close_price*1.05
loss_price = prev_close_price*0.97

if cur_price <= prev_close_price:
    do_buy(D2_overnight_stock_list[0],1,0)
    
if cur_price > target_price or cur_price < loss_price:
    do_sell(D2_overnight_stock_list[0],1,0)
    D2_overnight_stock_list.pop(0)


print(df)
