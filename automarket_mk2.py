import pyupbit
import time
import datetime
import math
import requests
import traceback

acc_key = "dJB2MmG7ooJITAswZ80G9xbm9CyNgriI4a5C7BNx"
sec_key = "G8xeW22dMVeBIx24JHcYrZ7P2l5x1eDOTxi4WReL"
app_token = "xoxb-3529765652915-3515197923767-8fl6ezJk1PoyXN7qtsP66ycn"
channel = "#coinautotrade"

class autoTrade:
    def __init__(self,start_cash,ticker) :
        self.fee = 0.05
        self.target_price = 0
        # self.bull = False
        self.ma5 = 0  #5일 이동평균
        self.ticker = ticker
        self.buy_yn = False

        self.start_cash = start_cash

        self.timer = 0
        self.get_today_data()

    def start(self):
        now = datetime.datetime.now() # 현재 시간
        slackBot.message("자동 매매 프로그램이 시작되었습니다.\n 시작 시간 : " + str(now) +
                         "\n매매 대상 :" + self.ticker +
                         "\n시작 자산 :" + str(self.start_cash))
        openTime = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1, hours=9, seconds=10)

        while True:
            try:
                now = datetime.datetime.now()
                current_price = pyupbit.get_current_price(self.ticker)

                if openTime < now < openTime + datetime.timedelta(seconds=5):
                    openTime = datetime.datetime(now.year, now.month,now.day) + datetime.timedelta(days=1, hours=9, seconds=10)
                    print("============매도중===========")
                    slackBot.message("매도 시도")
                    self.sell_coin() #매도 시도
                self.get_today_data() #데이터 갱신

                if (self.timer % 60 == 0):
                    print(now, "\topenTime :", openTime, "\tTarget :", self.target_price, "\tCurrent :", current_price,
                          "\tMA5 :", self.ma5, "\tBuy_yn :", self.buy_yn)

                if((current_price >= self.target_price) and (current_price >= self.ma5) and not self.buy_yn) : #매수 시도
                    print("============매수중===========")
                    slackBot.message("매수 시도")
                    self.buy_coin()

            except:
                slackBot.message("프로그램 오류 발생!!")
                traceback.print_exc()

            self.timer += 1
            time.sleep(1)
    def get_today_data(self):
        daily_data = pyupbit.get_ohlcv(self.ticker, count=41)
        daily_data['noise'] = 1 - abs(daily_data['open'] - daily_data['close']) / (daily_data['high'] -daily_data['low'])
        daily_data['noise_ma20'] = daily_data['noise'].rolling(window=20).mean().shift(1)

        #변동폭 (고가-저가)
        daily_data['range'] = daily_data['high'] - daily_data['low']
        #목표매수가 (시가+변동폭 * K)
        daily_data['targetPrice'] = daily_data['open'] + daily_data['range'].shift(1) * daily_data['noise_ma20']

        #5일 이동평균선
        daily_data['ma5'] = daily_data['close'].rolling(window=5,min_periods=1).mean().shift(1)
        #상승장 여부
        daily_data['bull'] = daily_data['open'] > daily_data['ma5']

        today = daily_data.iloc[-1]

        self.target_price = today.targetPrice
        self.ma5 = today.ma5
        print(daily_data.tail())
        print("================[데이터 갱신 완료]===================")
    def buy_coin(self):
        self.buy_yn = True
        balance = upbit.get_balance() #잔고 조회

        if balance > 5000:
            upbit.buy_market_order(self.ticker, balance * 0.9995)

            buy_price = pyupbit.get_orderbook("KRW-SBD")['orderbook_units'][0]['ask_price']
            print("============매수중===========")
            slackBot.message("#매수 주문\매수 주문 가격 : " + str(buy_price) + "원")
    def sell_coin(self):
        self.buy_yn = False
        balance = upbit.get_balance("KRW-SBD") #잔고 조회

        upbit.sell_market_order(ticker,balance)

        sell_price = pyupbit.get_orderbook("KRW-SBD")['orderbook_units'][0]['ask_price']
        print("============매도중===========")
        slackBot.message("#매도 주문\매도 주문 가격 : " + str(sell_price) + "원")

class slack:
    def __init__(self,token,channel) :
        self.token = token
        self.channel = channel
    def message(self,message) :
        requests.post("https://slack.com/api/chat.postMessage",
        headers = {"Authorization": "Bearer " + self.token},
        data = {"channel": self.channel, "text": message}
        )

upbit = pyupbit.Upbit(acc_key,sec_key)
slackBot = slack(app_token,channel)

start_cash = upbit.get_balance()
ticker = "KRW-SBD"
tradingBot = autoTrade(start_cash,ticker)
tradingBot.start()