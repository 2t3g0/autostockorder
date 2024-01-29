## information

### 파일
- apiresp.py : api의 response를 처리해주는 클래스
- kis_api.py : 한국투자 증권 api예제 파일
- stockorder.py : 주문을 위한 주요 함수들이 저장됨
- config.yaml : 계좌, api key 등이 저장된 파일.(개인정보 때문에 따로 보관)
- run.py : 프로그램이 실행 파일

### 주요함수
- auth : 최초 실행시 토큰 발급 및 여러 정보들을 설정해주는 함수
- _url_fetch : url, headers 설정 및 post/get을 입력 받아서 apiresp 클래스 형태로 리턴
- do_buy : 매수
- do_sell : 매도
- get_acct_balance : 계좌 확인
- do_cancel : 주문 취소
- do_revise : 주문 정정
- do_cancel_all : 모든 주문 퀴소
- get_trade_rank : 거래대금 순위 출력

---

### 업데이트 내용
## 2024.01.09
- [거래대금 순으로 출력하는 get_trade_rank 추가]
    - [c]