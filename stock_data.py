import pandas as pd

kospi_data = 'stock_data/kospi_code.xlsx'
kosdaq_data = 'stock_data/kosdaq_code.xlsx'
index_data = 'stock_data/idxcode.xlsx'
theme_data = 'stock_data/theme_code.xlsx'

# df 형태로 저장
kospi_df = pd.read_excel(kospi_data)
kosdaq_df = pd.read_excel(kosdaq_data)
theme_df = pd.read_excel(theme_data)

# etf, elw등 제외(주식만을 필터링)
kospi_df = kospi_df[kospi_df['그룹코드']=='ST']
kosdaq_df = kosdaq_df[kosdaq_df['증권그룹구분코드']=='ST']

#종목코드 통일화
theme_df['종목코드'] = theme_df['종목코드'].astype(str).str.zfill(6)


def find_theme(stock_code):
    
    is_thema = stock_code in theme_df['종목코드'].values
    
    if is_thema:
        sector = theme_df.loc[theme_df['종목코드']==stock_code, '테마명'].values
    else:   
        sector = []
        
    return sector
        