import pandas as pd

kospi_data = 'stock_data/kospi_code.xlsx'
kosdaq_data = 'stock_data/kosdaq_code.xlsx'
index_data = 'stock_data/idxcode.xlsx'
theme_data = 'stock_data/theme_code.xlsx'

# df 형태로 저장
kospi_df = pd.read_excel(kospi_data)
kosdaq_df = pd.read_excel(kosdaq_data)
theme_df = pd.read_excel(theme_data)
idx_df = pd.read_excel(index_data)

# etf, elw등 제외(주식만을 필터링)
kospi_df = kospi_df[kospi_df['그룹코드']=='ST']
kosdaq_df = kosdaq_df[kosdaq_df['증권그룹구분코드']=='ST']

#테마 전처리
# exclude_theme = ['2018 신규 상장주', '2019 신규 상장주', '2020 신규 상장주', '2021 신규 상장주', '2022 신규 상장주', '2023 신규 상장주']
# theme_df = theme_df[~theme_df['테마명'].isin(exclude_theme)]
theme_df['종목코드'] = theme_df['종목코드'].astype(str).str.zfill(6)


# 테마 찾아주는 함수
# input : 종목코드
# output : 종목에 포함되는 테마
def find_theme(stock_code):
    
    is_thema = stock_code in theme_df['종목코드'].values
    
    if is_thema:
        theme = theme_df.loc[theme_df['종목코드']==stock_code, '테마명'].values
    else:   
        theme = []
        
    return theme


# 업종 찾아주는 함수
def find_sector(stock_code):
    is_kospi = stock_code in kospi_df['단축코드'].values
    is_kosdaq = stock_code in kosdaq_df['단축코드'].values
    
    if is_kospi:
        sector = kospi_df.loc[kospi_df['단축코드']==stock_code, '지수업종중분류'].astype(str).values[0]
        sector = sector.zfill(4)
    elif is_kosdaq:
        sector = kosdaq_df.loc[kosdaq_df['단축코드']==stock_code, '지수 업종 중분류 코드'].astype(str).values[0]
        sector = sector.zfill(4)
    else:
        sector = '0000'
        
    return sector

def find_sector_name(sector_code):
    if sector_code!='0000':
        sector_name = idx_df.loc[idx_df['업종코드']==sector_code,'name'].values[0]
    else:
        sector_name = '알수없음'
    return sector_name


# tmp_code = find_sector('452400')
# print(tmp_code)
# print(find_sector_name(tmp_code))

