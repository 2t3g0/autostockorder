import requests # HTTP 요청을 보냄
import json     # 특정 객체를 JSON 데이터로 만들어 쓸 수 있음





def hashkey(datas):
    """암호화"""
    PATH = "uapi/hashkey"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
    'content-Type' : 'application/json',
    'appKey' : APP_KEY,
    'appSecret' : APP_SECRET,
    }
    res = requests.post(URL, headers=headers, data=json.dumps(datas))
    hashkey = res.json()["HASH"]
    return hashkey

def get_access_token():
    """토큰 발급"""
    headers = {"content-type":"application/json"}
    body = {"grant_type":"client_credentials",
    "appkey":APP_KEY, 
    "appsecret":APP_SECRET}
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    ACCESS_TOKEN = res.json()["access_token"]
    return ACCESS_TOKEN

def get_cur_price(access_token):
    """ 주식 현재가"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
           "authorization": f"Bearer {access_token}",
           "appKey":APP_KEY,
           "appSecret":APP_SECRET,
           "tr_id":"FHKST01010100"} # tr_id : 주식현재가 시세 등 항목에 대한 파라미터
    
    params = {
    "fid_cond_mrkt_div_code":"J",   # 시장 구분 : J
    "fid_input_iscd":"005930"       # 종목 코드 : 005930(삼성전자)
    }
    
    res = requests.get(URL, headers=headers, params=params)
    
    return res.json()['output']['stck_prpr']   # stck_prpr : 현재가
                                               # res는 msg1 / msg_cd / output 3가지로 이루어짐
                                               # 대부분 정보는 output에 저장되어 있음

def get_cur_price_per_day(access_token):
    """주식 현재가 일자별"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
           "authorization": f"Bearer {access_token}",
           "appKey":APP_KEY,
           "appSecret":APP_SECRET,
           "tr_id":"FHKST01010400"} # 주식 현재가 일자별 
    
    params = {
    "fid_cond_mrkt_div_code":"J",   # 주식, ETF, ETN : J
    "fid_input_iscd":"005930",      # 종목코드
    "fid_org_adj_prc":"0",          # 수정주가 원주가 가격 : 0 (수정주가가 반영된 가격, 쉽게 말해 액면 분할 병합등 과거주가를 현재 주가에 맞게 보정한 것)
    "fid_period_div_code":"D"       # 기간 분류 코드 : D(일자별)
    }
    res = requests.get(URL, headers=headers, params=params)
    return res.json()['output'][1]['stck_clpr']    # 값들이 여러개 리스트 형식으로 나옴 그중에 첫번째(0) 종가가격 출력
    
def buy_marketplace(access_token):
    """주식 주문(시장가)"""
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
    "CANO": "50101367",
    "ACNT_PRDT_CD": "01",
    "PDNO": "005930",       # 종목 코드
    "ORD_DVSN": "01",       # 주문방법(현재 시장가)
    "ORD_QTY": "10",        # 주문 개수
    "ORD_UNPR": "0",        # 주문 단가(시장가시에는 주문단가를 무시함)
    }
    
    headers = {"Content-Type":"application/json", 
           "authorization":f"Bearer {access_token}",
           "appKey":APP_KEY,
           "appSecret":APP_SECRET,
           "tr_id":"VTTC0802U",
           "custtype":"P",
           "hashkey" : hashkey(data)}
    
    res = requests.post(URL, headers=headers, data=json.dumps(data))    # 주문시에는 post
    print(res.json()['msg1'])
    
def buy_orderplace(access_token):
    """주식 주문(지정가)"""
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
    "CANO": "50101367",
    "ACNT_PRDT_CD": "01",
    "PDNO": "005930",       # 종목 코드
    "ORD_DVSN": "00",       # 주문방법(현재 지정가)
    "ORD_QTY": "10",        # 주문 개수
    "ORD_UNPR": "60000",        # 주문 단가(시장가시에는 주문단가를 무시함)
    }
    
    headers = {"Content-Type":"application/json", 
           "authorization":f"Bearer {access_token}",
           "appKey":APP_KEY,
           "appSecret":APP_SECRET,
           "tr_id":"VTTC0802U",
           "custtype":"P",
           "hashkey" : hashkey(data)}
    
    res = requests.post(URL, headers=headers, data=json.dumps(data))    # 주문시에는 post
    print(res.json()['msg1'])
    print(res.json())

def cancel_order(access_token, KRX_FWDG_ORD_ORGNO, ODNO):
    """주문 취소"""
    PATH = "uapi/domestic-stock/v1/trading/order-rvsecncl"
    URL = f"{URL_BASE}/{PATH}"
    data ={
    "CANO": "50101367",                         # 계좌번호 앞6자리
    "ACNT_PRDT_CD": "01",                       # 계좌번호 뒤2자리
    "KRX_FWDG_ORD_ORGNO":KRX_FWDG_ORD_ORGNO,    # 주문번호(한국거래소전송주문조직번호)
    "ORGN_ODNO":ODNO,                           # 주문번호(그냥)
    "RVSE_CNCL_DVSN_CD":"02",                   # 정정/취소 구분 : 01/정정, 02/취소
    "ORD_DVSN":"00",                            # 주문 구분(취소시에는 상관없어 보임) : 00 지정
    "ORD_QTY":"10",                             # 취소 수량
    "ORD_UNPR":"0",                             # 주문 단가(취소시 필요없음:0)
    "QTY_ALL_ORD_YN": "Y",                      # 잔량전부주문여부(Y: 전량, N: 일부)
    }
    headers = {"Content-Type":"application/json", 
          "authorization":f"Bearer {access_token}",
          "appKey":APP_KEY,
          "appSecret":APP_SECRET,
          "tr_id":"VTTC0803U",
          "custtype":"P", 
          "hashkey" : hashkey(data)}
    
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    
def sell_order(access_token):
    """주식 매도"""
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
    "CANO": "50101367",         # 계좌번호
    "ACNT_PRDT_CD": "01",
    "PDNO": "005930",           # 종목코드
    "ORD_DVSN": "01",           # 주문구분 : 00(지정), 01(시장)
    "ORD_QTY": "12",            # 주문수량
    "ORD_UNPR": "0",            # 주문단가 (시장가 주문의 경우에는 주문단가 무시함)
    }
    headers = {"Content-Type":"application/json", 
          "authorization":f"Bearer {access_token}",
          "appKey":APP_KEY,
          "appSecret":APP_SECRET,
          "tr_id":"VTTC0801U",
          "custtype":"P",
          "hashkey" : hashkey(data)
          }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    print(res.json()["msg1"])
    
access_tokent = get_access_token()
sell_order(access_tokent)
