import yaml
import requests
import json
import copy
import time
from apiresp import APIResp
import pandas as pd
from collections import namedtuple
with open('../config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)
  
    
_TRENV = tuple()
_isPaper = True
_DEBUG = False

# 기본 헤더 정의
_base_headers = {
    "Content-Type": "application/json",
    "Accept": "text/plain",
    "charset": "UTF-8",
    'User-Agent': _cfg['my_agent']
}

# 가져오기 : 앱키, 앱시크리트, 종합계좌번호(계좌번호 중 숫자8자리), 계좌상품코드(계좌번호 중 숫자2자리), 토큰, 도메인
def _setTRENV(cfg):
    nt1 = namedtuple('KISEnv', ['my_app', 'my_sec', 'my_acct', 'my_prod', 'my_token', 'my_url'])
    d = {
        'my_app': cfg['my_app'],        # 앱키
        'my_sec': cfg['my_sec'],        # 앱시크리트
        'my_acct': cfg['my_acct'],      # 종합계좌번호(8자리)
        'my_prod': cfg['my_prod'],      # 계좌상품코드(2자리)
        'my_token': cfg['my_token'],    # 토큰
        'my_url': cfg['my_url']         # 실전 도메인 (https://openapi.koreainvestment.com:9443)
    }                                   # 모의 도메인 (https://openapivts.koreainvestment.com:29443)

    global _TRENV
    _TRENV = nt1(**d)


# 실전 투자면 prod, 모의투자면 vps
def changeTREnv(token_key, svr='vps', product='01'):
    cfg = dict()

    global _isPaper
    if svr == 'prod':  # 실전투자
        ak1 = 'my_app'  # 실전투자용 앱키
        ak2 = 'my_sec'  # 실전투자용 앱시크리트
        _isPaper = False
    elif svr == 'vps':  # 모의투자
        ak1 = 'paper_app'  # 모의투자용 앱키
        ak2 = 'paper_sec'  # 모의투자용 앱시크리트
        _isPaper = True

    cfg['my_app'] = _cfg[ak1]
    cfg['my_sec'] = _cfg[ak2]

    if svr == 'prod' and product == '01':  # 실전투자 주식투자, 위탁계좌, 투자계좌
        cfg['my_acct'] = _cfg['my_acct_stock']
    elif svr == 'vps' and product == '01':  # 모의투자 주식투자, 위탁계좌, 투자계좌
        cfg['my_acct'] = _cfg['my_paper_stock']


    cfg['my_prod'] = product
    cfg['my_token'] = token_key
    cfg['my_url'] = _cfg[svr]

    _setTRENV(cfg)
    
def _getBaseHeader():
    return copy.deepcopy(_base_headers)

def _getResultObject(json_data):
    _tc_ = namedtuple('res', json_data.keys())

    return _tc_(**json_data)

def auth(svr='prod', product='01', url=None):
    p = {
        "grant_type": "client_credentials",
    }
    # 개인 환경파일 "kis_devlp.yaml" 파일을 참조하여 앱키, 앱시크리트 정보 가져오기
    # 개인 환경파일명과 위치는 고객님만 아는 위치로 설정 바랍니다.
    if svr == 'prod':  # 실전투자
        ak1 = 'my_app'  # 앱키 (실전투자용)
        ak2 = 'my_sec'  # 앱시크리트 (실전투자용)
    elif svr == 'vps':  # 모의투자
        ak1 = 'paper_app'  # 앱키 (모의투자용)
        ak2 = 'paper_sec'  # 앱시크리트 (모의투자용)

    # 앱키, 앱시크리트 가져오기
    p["appkey"] = _cfg[ak1]
    p["appsecret"] = _cfg[ak2]


    url = f'{_cfg[svr]}/oauth2/tokenP'
    res = requests.post(url, data=json.dumps(p), headers=_getBaseHeader())  # 토큰 발급
    rescode = res.status_code
    if rescode == 200:  # 토큰 정상 발급
        my_token = _getResultObject(res.json()).access_token  # 토큰값 가져오기
    else:
        print('Get Authentification token fail!\nYou have to restart your app!!!')
        return

    # 발급토큰 정보 포함해서 헤더값 저장 관리, API 호출시 필요
    changeTREnv(f"Bearer {my_token}", svr, product)

    _base_headers["authorization"] = _TRENV.my_token
    _base_headers["appkey"] = _TRENV.my_app
    _base_headers["appsecret"] = _TRENV.my_sec

def getEnv():
    return _cfg
def getTREnv():
    return _TRENV
def isPaperTrading():
    return _isPaper

#주문 API에서 사용할 hash key값을 받아 header에 설정해 주는 함수
# Input: HTTP Header, HTTP post param
# Output: None
def set_order_hash_key(h, p):
   
    url = f"{getTREnv().my_url}/uapi/hashkey"
  
    res = requests.post(url, data=json.dumps(p), headers=h)
    rescode = res.status_code
    if rescode == 200:
        h['hashkey'] = _getResultObject(res.json()).HASH
    else:
        print("Error:", rescode)
        


def _url_fetch(api_url, ptr_id, params, appendHeaders=None, postFlag=False, hashFlag=True):
    url = f"{getTREnv().my_url}{api_url}"
    
    headers = _getBaseHeader()

    #추가 Header 설정
    tr_id = ptr_id
    if ptr_id[0] in ('T', 'J', 'C'):
        if isPaperTrading():
            tr_id = 'V' + ptr_id[1:]

    headers["tr_id"] = tr_id
    headers["custtype"] = "P"
    
    if appendHeaders is not None:
        if len(appendHeaders) > 0:
            for x in appendHeaders.keys():
                headers[x] = appendHeaders.get(x)

    if(_DEBUG):
        print("< Sending Info >")
        print(f"URL: {url}, TR: {tr_id}")
        print(f"<header>\n{headers}")
        print(f"<body>\n{params}")
        
    if (postFlag):
        if(hashFlag): set_order_hash_key(headers, params)
        res = requests.post(url, headers=headers, data=json.dumps(params))
    else:
        res = requests.get(url, headers=headers, params=params)

    if res.status_code == 200:
        ar = APIResp(res)
        if (_DEBUG): ar.printAll()
        return ar
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return None


# 모의계좌를 사용하지만 요청 url이 실전계좌일 경우
def usingprod_url_fetch(api_url, ptr_id, params, postFlag=False, hashFlag=True, tr_cont=""):
    url = f"https://openapi.koreainvestment.com:9443{api_url}"
    
    headers = _getBaseHeader()

    #추가 Header 설정
    tr_id = ptr_id

    headers["tr_id"] = tr_id
    headers["custtype"] = "P"
    headers["tr_cont"] = tr_cont
    
    if(_DEBUG):
        print("< Sending Info >")
        print(f"URL: {url}, TR: {tr_id}")
        print(f"<header>\n{headers}")
        print(f"<body>\n{params}")
        
    if (postFlag):
        if(hashFlag): set_order_hash_key(headers, params)
        res = requests.post(url, headers=headers, data=json.dumps(params))
    else:
        res = requests.get(url, headers=headers, params=params)

    if res.status_code == 200:
        ar = APIResp(res)
        if (_DEBUG): ar.printAll()
        return ar
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return None
    
#종목의 주식, ETF, 선물/옵션 등의 구분값을 반환. 현재는 무조건 주식(J)만 반환
def _getStockDiv(stock_no):
    return 'J'

# 종목별 현재가를 dict 로 반환
# Input: 종목코드
# Output: 현재가 Info dictionary. 반환된 dict 가 len(dict) < 1 경우는 에러로 보면 됨

def get_current_price(stock_no):
    url = "/uapi/domestic-stock/v1/quotations/inquire-price"
    tr_id = "FHKST01010100"

    params = {
        'FID_COND_MRKT_DIV_CODE': _getStockDiv(stock_no), 
        'FID_INPUT_ISCD': stock_no
        }

    t1 = _url_fetch(url, tr_id, params)

    if t1.isOK():
        return t1.getBody().output
    else:
        t1.printError()
        return dict()

# 주문 base function
# Input: 종목코드, 주문수량, 주문가격, Buy Flag(If True, it's Buy order), order_type="00"(지정가)
# Output: HTTP Response

def do_order(stock_code, order_qty, order_price, prd_code="01", buy_flag=True, order_type="01"):

    url = "/uapi/domestic-stock/v1/trading/order-cash"

    if buy_flag:
        tr_id = "TTTC0802U"  #buy
    else:
        tr_id = "TTTC0801U"  #sell

    params = {
        'CANO': getTREnv().my_acct, 
        'ACNT_PRDT_CD': prd_code, 
        'PDNO': stock_code, 
        'ORD_DVSN': order_type, 
        'ORD_QTY': str(order_qty), 
        'ORD_UNPR': str(order_price), 
        'CTAC_TLNO': '', 
        'SLL_TYPE': '01', 
        'ALGO_NO': ''
        }
    
    t1 = _url_fetch(url, tr_id, params, postFlag=True, hashFlag=True)
    
    if t1.isOK():
        return t1
    else:
        t1.printError()
        return None

# 사자 주문. 내부적으로는 do_order 를 호출한다.
# Input: 종목코드, 주문수량, 주문가격
# Output: True, False

def do_buy(stock_code, order_qty, order_price, prd_code="01", order_type="00"):
    t1 = do_order(stock_code, order_qty, order_price, buy_flag=True, order_type=order_type)
    if t1 == None:
        pass
    else:
        return t1.isOK()

# 팔자 주문. 내부적으로는 do_order 를 호출한다.
# Input: 종목코드, 주문수량, 주문가격
# Output: True, False

def do_sell(stock_code, order_qty, order_price, prd_code="01", order_type="00"):
    t1 = do_order(stock_code, order_qty, order_price, buy_flag=False, order_type=order_type)
    if t1 == None:
        pass
    else:
        return t1.isOK()

# 계좌 잔고를 DataFrame 으로 반환
# Input: None (Option) rtCashFlag=True 면 예수금 총액을 반환하게 된다
# Output: DataFrame (Option) rtCashFlag=True 면 예수금 총액을 반환하게 된다

def get_acct_balance(rtCashFlag=False):
    url = '/uapi/domestic-stock/v1/trading/inquire-psbl-order'
    tr_id = "TTTC8434R"

    params = {
        'CANO': getTREnv().my_acct, 
        'ACNT_PRDT_CD': '01', 
        'AFHR_FLPR_YN': 'N', 
        'FNCG_AMT_AUTO_RDPT_YN': 'N', 
        'FUND_STTL_ICLD_YN': 'N', 
        'INQR_DVSN': '01', 
        'OFL_YN': 'N', 
        'PRCS_DVSN': '01', 
        'UNPR_DVSN': '01', 
        'CTX_AREA_FK100': '', 
        'CTX_AREA_NK100': ''
        }

    t1 = _url_fetch(url, tr_id, params)

    if rtCashFlag and t1.isOK():    # 예수금 총액 반환
        r2 = t1.getBody().output2
        return int(r2[0]['dnca_tot_amt'])

    if t1.isOK():  #body 의 rt_cd 가 0 인 경우만 성공
        tdf = pd.DataFrame(t1.getBody().output1)
 
        cf1 = ['prdt_name','hldg_qty', 'ord_psbl_qty', 'pchs_avg_pric', 'evlu_pfls_rt', 'prpr', 'bfdy_cprs_icdc', 'fltt_rt']
        cf2 = ['종목명', '보유수량', '매도가능수량', '매입단가', '수익율', '현재가' ,'전일대비', '등락']
        if tdf.empty:
            print("현재 보유중인 종목이 없습니다.")
            return tdf
        else:
            tdf.set_index('pdno', inplace=True)  # tdf의 인덱스를 pdno(종목번호)로 설정
            if not isPaperTrading(): tdf.drop('', inplace=True) 
            tdf = tdf[cf1]  # 원하는 항목을 인덱싱
            tdf[cf1[1:]] = tdf[cf1[1:]].apply(pd.to_numeric)
            ren_dict = dict(zip(cf1, cf2))
            return tdf.rename(columns=ren_dict)
    else:
        t1.printError()
        return pd.DataFrame()

# 특정 주문 취소(01)/정정(02)
# Input: 주문 번호(get_orders 를 호출하여 얻은 DataFrame 의 index  column 값이 취소 가능한 주문번호임)
#       주문점(통상 06010), 주문수량, 주문가격, 상품코드(01), 주문유형(00), 정정구분(취소-02, 정정-01)
# Output: APIResp object

def _do_cancel_revise(order_no, order_branch, order_qty, order_price, prd_code, order_dv, cncl_dv):
    url = "/uapi/domestic-stock/v1/trading/order-rvsecncl"

    tr_id = "TTTC0803U"

    params = {
        "CANO": getTREnv().my_acct,
        "ACNT_PRDT_CD": prd_code,
        "KRX_FWDG_ORD_ORGNO": order_branch, 
        "ORGN_ODNO": order_no,
        "ORD_DVSN": order_dv,
        "RVSE_CNCL_DVSN_CD": cncl_dv, #취소(02)
        "ORD_QTY": str(order_qty),
        "ORD_UNPR": str(order_price),
        "QTY_ALL_ORD_YN": "Y"
    }

    t1 = _url_fetch(url, tr_id, params=params, postFlag=True)  

    if t1.isOK():
        return t1
    else:
        t1.printError()
        return None

# 특정 주문 취소
# 
def do_cancel(order_no, order_qty, order_price, order_branch='06010', prd_code='01', order_dv='00', cncl_dv='02'):
    return _do_cancel_revise(order_no, order_branch, order_qty, order_price, prd_code, order_dv, cncl_dv)

# 특정 주문 정정
# 
def do_revise(order_no, order_qty, order_price, order_branch='06010', prd_code='01', order_dv='00', cncl_dv='01'):
    return _do_cancel_revise(order_no, order_branch, order_qty, order_price, prd_code, order_dv, cncl_dv)


# 정정취소 가능한 주문 목록을 DataFrame 으로 반환
# Input: None
# Output: DataFrame

def get_orders(prd_code='01'):
    url = "/uapi/domestic-stock/v1/trading/inquire-psbl-rvsecncl"

    tr_id = "TTTC8036R"

    params = {
        "CANO": getTREnv().my_acct,
        "ACNT_PRDT_CD": prd_code,
        "CTX_AREA_FK100": '',
        "CTX_AREA_NK100": '',
        "INQR_DVSN_1": '0',
        "INQR_DVSN_2": '0'
        }

    t1 = _url_fetch(url, tr_id, params)    
    if t1.isOK():  
        tdf = pd.DataFrame(t1.getBody().output)
        tdf.set_index('odno', inplace=True)  
        tdf.drop('', inplace=True) 
        cf1 = ['pdno', 'ord_qty', 'ord_unpr', 'ord_tmd', 'ord_gno_brno','orgn_odno']
        cf2 = ['종목코드', '주문수량', '주문가격', '시간', '주문점', '원번호']
        tdf = tdf[cf1]
        ren_dict = dict(zip(cf1, cf2))

        return tdf.rename(columns=ren_dict)

    else:
        t1.printError()
        return pd.DataFrame()
    
# 모든 주문 취소
# Input: None
# Output: None

def do_cancel_all():
    tdf = get_orders()
    od_list = tdf.index.to_list()
    qty_list = tdf['주문수량'].to_list()
    price_list = tdf['주문가격'].to_list()
    branch_list = tdf['주문점'].to_list()
    cnt = 0
    for x in od_list:
        ar = do_cancel(x, qty_list[cnt], price_list[cnt], branch_list[cnt])
        cnt += 1
        print(ar.getErrorCode(), ar.getErrorMessage())
        time.sleep(.2)


# 거래대금 상위
# Input: None
# Output: None
def get_trade_rank():
    url = "/uapi/domestic-stock/v1/quotations/psearch-result"

    tr_id = "HHKST03900400"

    params = {
        "user_id" : "maple326",
        "seq" : '0' #
    }
    global _isPaper 
    _isPaper = False
    t1 = usingprod_url_fetch(url, tr_id, params=params)
    _isPaper = True 
    if t1.isOK():
        tdf = pd.DataFrame(t1.getBody().output2)
        res = tdf[['code', 'name', 'chgrate','trade_amt']]
        # res['trade_amt'] = (res['trade_amt'].astype(float) / 100000).astype(str)
        res.loc[:, 'trade_amt'] = (res['trade_amt'].astype(float) / 100000).astype(str)
        return res
    else:
        t1.printError()
        return None
    