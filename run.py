from stockorder import *
from stock_data import *

auth(svr='vps')
# do_buy("005930", 1, 0, order_type="01")

df = get_trade_rank()
df_code = df['code']
df_type_dict = []

for i in df_code:
    df_type_dict.append(find_theme(i))
df['theme'] = df_type_dict
print(df)

# result_df = df.set_index('code')['value'].reset_index(name='code_value')