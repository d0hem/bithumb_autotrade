import time
import requests
import math
import pybithumb
from pybithumb import Bithumb
api_key = ""
secret_key = ""

bithumb = Bithumb(api_key, secret_key)


def get_highest_lowest_price():
    url = "https://api.bithumb.com/public/candlestick/SUI_KRW/30m"
    response = requests.get(url)
    data = response.json()
    # 최신 캔들 데이터는 마지막 인덱스에 위치하도록 가정합니다.
    latest_candle = data['data'][-1]
    high_price = float(latest_candle[3])
    low_price = float(latest_candle[4])
    return high_price, low_price


def buy_available_cnt(current_price):

    try:
        balance = bithumb.get_balance('SUI')
        buy_coins = (balance[2]-balance[3])/current_price
        return buy_coins
    except:
        return 0


def sell_available_cnt():

    try:
        balance = bithumb.get_balance('SUI')
        sell_coins = balance[0]-balance[1]
        return sell_coins
    except:
        return 0


def main():
    k = 0.444
    min_krw_amount = 1000

    while True:
        current_time_epoch = time.time()
        current_time_local = time.localtime(current_time_epoch)
        current_date_time = time.strftime(
            '%Y-%m-%d %H:%M:%S', current_time_local)

        balance = bithumb.get_balance('SUI')  # 보유 원화
#         print("현재 보유 원화 : ",balance[2] ," 원")
#         print("-----------------------------------")

        current_price = pybithumb.get_current_price('SUI')  # 현재 SUI 가격
        # current_price = round(current_price)
#         print("SUI 현재가: ", current_price, " 원")

        high_price, low_price = get_highest_lowest_price()
        target_price = low_price + (high_price - low_price) * k
        # target_price = int(target_price)
#         print("SUI 타겟가: ", target_price, " 원")

        buy_balance = buy_available_cnt(current_price)

        buy_balance = round(buy_balance * 0.7, 4)  # 가능수량의 70%만
#         print("매수 가능 수량: ", buy_balance, " 개")

        sell_balance = sell_available_cnt()
#         print("매도 가능 수량: ", sell_balance, " 개")

        now = time.localtime()

        # Buy condition
        # X8분 00초~ X9분2초까지는 매수 x
        if (current_price >= target_price) and (now.tm_min % 30 != 28) and buy_balance > 0.1 and not (now.tm_min % 30 == 29 and now.tm_sec in (0, 1, 2, 3)):
            try:

                buy_result = bithumb.buy_market_order("SUI", buy_balance)
                if len(buy_result) != 2:
                    print("현재 보유 원화 : ", balance[2], " 원")
                    print("현재 DTTM:", current_date_time)
                    print("-----------------------------------")
                    print("SUI 현재가: ", current_price, " 원")
                    print("SUI 타겟가: ", target_price, " 원")
                    print("★★★★★SUI코인 ", buy_balance, "개 매수 주문완료★★★★★")

                    # while True:
                    #     outstanding_buy = bithumb.get_outstanding_order(
                    #         buy_result)  # 미완료 몇개인지 확인
                    #     if outstanding_buy < 0.01:  # 팔렸으면
                    #         print("★★★★★매수 체결완료★★★★★")
                    #         print("현재 DTTM:", current_date_time)
                    #         print("-----------------------------------")
                    #         break
                    #     time.sleep(1)

            except:
                pass

        # Sell condition
        # X8분 15초~x8분 30초 사이에 매도 # X9분 3초에 갱신
        elif now.tm_min % 30 == 28 and 15 < now.tm_sec < 30 and sell_balance > 0.01:
            try:
                sell_result = bithumb.sell_market_order("SUI", sell_balance)
                if len(sell_result) != 2:
                    print("★★★★★SUI코인 ", sell_balance, "개 매도 주문완료★★★★★")
                    time.sleep(5)
                    # while True:
                    #     outstanding_sell = bithumb.get_outstanding_order(
                    #         sell_result)  # 미완료 몇개인지 확인
                    #     if outstanding_sell < 0.01:  # 팔렸으면
                    #         print("★★★★★매도 체결완료★★★★★")
                    #         print("현재 DTTM:", current_date_time)
                    #         print("-----------------------------------")
                    #         break
                    #     time.sleep(1)

            except:
                pass

        # 매수 매도 조건 아니면 안했으면
        else:
            pass
#             print("주문 실행 X")

        # Wait for 1 minute before checking the conditions again.
        time.sleep(0.5)


if __name__ == "__main__":
    main()
