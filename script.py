import gc
import json
import os
import time
import traceback
import redis
import requests
from khayyam import JalaliDatetime

profile = os.environ.get('GHEYMAT_CHAND_PROFILE')
bot_token = os.environ.get('BOT_TOKEN')
chat_id = os.environ.get('CHAT_ID')
private_chat_id = os.environ.get('PRIVATE_CHAT_ID')
url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
bazar_token = ''
redis_connection = redis.Redis(host='redis', port=6379, db=1)
REDIS_KEY = 'prices_history'

def get_milli_prices():
    try:
        milli_response = requests.get("https://milli.gold/api/v1/public/milli-price/detail", timeout=1)
        if milli_response.status_code != 200:
            print(f'milli error:\n{milli_response.content}')
            requests.post(url, data={'chat_id': private_chat_id,
                                     'text': f'Milli Gold error:\n {milli_response.status_code} \n {milli_response.content}'},
                          timeout=1)
            return None, None
        milli_price = int(milli_response.json()['price18'] * 100)
        return milli_price, milli_price
    except Exception:
        traceback.print_exc()
        return None, None


def get_goldika_prices():
    try:
        goldika_response = requests.get("https://goldika.ir/api/public/price", timeout=1)
        if goldika_response.status_code != 200:
            print(f'goldika error:\n{goldika_response.content}')
            requests.post(url,
                          data={'chat_id': private_chat_id, 'text': f'Goldika error:\n {goldika_response.content}'},
                          timeout=1)
            return None, None
        goldika_price = goldika_response.json()['data']['price']
        goldika_buy_price = int(goldika_price['buy'] / 10)
        goldika_sell_price = int(goldika_price['sell'] / 10)
        return goldika_buy_price, goldika_sell_price
    except Exception:
        traceback.print_exc()
        return None, None


def get_bazar_token():
    try:
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'dnt': '1',
            'origin': 'https://web.baazar.ir',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://web.baazar.ir/auth/login?redirect=%2Fdashboard',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        bazar_login_response = requests.post("https://web.baazar.ir/api/shop/authenticate/v2/web-login/",
                                             data=json.dumps({"username": "09124398514", "password": "13@sMz&77",
                                                              "rememberMe": True}), headers=headers, timeout=1)
        if bazar_login_response.status_code != 200:
            requests.post(url, data={'chat_id': private_chat_id,
                                     'text': f'Bazar login error:\n {bazar_login_response.content}'}, timeout=1)
            return None
        return bazar_login_response.json()['data']['token']
    except Exception:
        traceback.print_exc()
        return None


def get_bazar_prices():
    global bazar_token
    try:
        bazar_token = get_bazar_token()

        bazar_headers = {
            'Authorization': f'Bearer {bazar_token}',
            'Content-Type': 'application/json'
        }

        bazar_response = requests.get("https://web.baazar.ir/api/shop/account/v1/dashboard", headers=bazar_headers,
                                      timeout=1)
        if bazar_response.status_code != 200:
            print(f'bazaar error:\n{bazar_response.content}')
            if bazar_response.status_code != 401:
                requests.post(url,
                              data={'chat_id': private_chat_id, 'text': f'Bazar  error:\n {bazar_response.content}'},
                              timeout=1)
            return None, None
        bazar_price = bazar_response.json()['data']
        bazar_buy_price = int(int(bazar_price['goldBuyPrice']) / 10)
        bazar_sell_price = int(int(bazar_price['goldSellPrice']) / 10)
        return bazar_buy_price, bazar_sell_price

    except Exception:
        traceback.print_exc()
        return None, None


def get_talasea_prices():
    try:
        talasea_response = requests.get("https://talasea.ir/api/goldPrice/day", timeout=1)
        if talasea_response.status_code != 200:
            print(f'talasea error:\n{talasea_response.content}')
            requests.post(url,
                          data={'chat_id': private_chat_id, 'text': f'Talasea error:\n {talasea_response.content}'},
                          timeout=1)
            return None, None
        talasea_price = int(talasea_response.json()[-1]['price'] * 1000)
        return talasea_price, talasea_price
    except Exception:
        traceback.print_exc()
        return None, None


def get_daric_prices(timestamp):
    try:
        daric_url = f'https://apie.daric.gold/api/chart/history?symbol=GOLD18TMN&resolution=60&from={timestamp - 36000}&to={timestamp}&countback=2&currencyCode=TMN'
        daric_response = requests.get(daric_url, timeout=1)
        if (daric_response.status_code != 200):
            print(f'daric error:\n{daric_response.content}')
            requests.post(url, data={'chat_id': private_chat_id, 'text': f'Daric error:\n {daric_response.content}'},
                          timeout=1)
            return None, None
        daric_prices = daric_response.json()['c']
        buy_price = int(daric_prices[0])
        sell_price = int(daric_prices[1])
        return buy_price, sell_price
    except Exception:
        traceback.print_exc()
        return None, None


def get_tala_dot_ir_prices():
    try:
        tala_dot_ir_response = requests.get("https://www.tala.ir/ajax/price/talair", timeout=1)
        if tala_dot_ir_response.status_code != 200:
            print(f'tala.ir error:\n{tala_dot_ir_response.content}')
            requests.post(url, data={'chat_id': private_chat_id,
                                     'text': f'Milli Gold error:\n {tala_dot_ir_response.status_code} \n {tala_dot_ir_response.content}'},
                          timeout=1)
            return None, None
        tala_dot_ir_price = int(tala_dot_ir_response.json()['gold']['gold_18k']['v'].replace(",", ""))
        return tala_dot_ir_price, tala_dot_ir_price
    except Exception:
        traceback.print_exc()
        return None, None

def store_prices_in_redis(prices):
    try:
        print(prices)
        # Serialize prices to JSON
        prices_json = json.dumps(prices)
        # Add prices to the Redis list
        redis_connection.rpush(REDIS_KEY, prices_json)
        # Trim the list to the last 30 entries
        redis_connection.ltrim(REDIS_KEY, -60, -1)
    except Exception as e:
        print(f"Error storing prices in Redis: {e}")
        traceback.print_exc()

while True:
    try:
        now = JalaliDatetime.now()
        timestamp = int(time.time())
        print(f'start at {timestamp}')
        prices = []
        dataset_prices = {}
        text = ''
        prices.append(('قیمت طلا 🟡', ''))
        milli_buy_price, milli_sell_price = get_milli_prices()
        if milli_buy_price:
            prices.append(('میلی', f'{milli_buy_price:,} - {milli_sell_price:,}'))
            dataset_prices['milli.gold']= int((milli_buy_price+ milli_sell_price)/2)

        tala_dot_ir_buy_price, tala_dot_ir_sell_price = get_tala_dot_ir_prices()
        if tala_dot_ir_buy_price and tala_dot_ir_sell_price:
            prices.append(('سایت طلا', f'{tala_dot_ir_buy_price:,} - {tala_dot_ir_sell_price:,}'))
            dataset_prices['tala.ir']= int((tala_dot_ir_buy_price+ tala_dot_ir_sell_price)/2)
        

        talasea_buy_price, talasea_sell_price = get_talasea_prices()
        if talasea_buy_price and talasea_sell_price:
            prices.append(('طلاسی', f'{talasea_buy_price:,} - {talasea_sell_price:,}'))
            dataset_prices['talasi']= int((talasea_buy_price+ talasea_sell_price)/2)

        goldika_buy_price, goldika_sell_price = get_goldika_prices()
        if goldika_buy_price and goldika_sell_price:
            prices.append(('گلدیکا', f'{goldika_buy_price:,} - {goldika_sell_price:,}'))
            dataset_prices['goldika']= int((goldika_buy_price+ goldika_sell_price)/2)

        # bazar_buy_price, bazar_sell_price = get_bazar_prices()
        # if bazar_buy_price and bazar_sell_price:
            # prices.append(('بازر', f'{bazar_buy_price:,} - {bazar_sell_price:,}'))
            # dataset_prices['بازر']= int((bazar_buy_price+ bazar_sell_price)/2)

        # daric_buy_price, daric_sell_price = get_daric_prices(timestamp)
        # if daric_buy_price and daric_sell_price:
        #     prices.append(('داریک', f'{daric_buy_price:,} - {daric_sell_price:,}'))
        #     dataset_prices['داریک']= int((daric_buy_price+ daric_sell_price)/2)

        store_prices_in_redis({'time': timestamp, 'prices': dataset_prices})
        prices.append(('اختلاف میلی و طلا', f'{milli_buy_price - tala_dot_ir_buy_price:,}'))

        for name, price in prices:
            text += f"<code>{name}{' ' * (10 - len(name))}{price}</code>\n"

        persian_date = now.strftime('%Y/%m/%d')
        persian_time = now.strftime('%H:%M:%S')
        text += f'\n🕐 {persian_date} {persian_time}\n'
        text += '@gheymat_chande'

        data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': 'true'}
        if (profile == 'production'):
            response = requests.post(url, data=data, timeout=1)
            if response.status_code == 200:
                print('succeed')
            else:
                print(
                    f'failed to send message to telegram for body and response: \n{text}\n ----\n{response.text}\n####')

        time.sleep(30)
        gc.collect()
    except Exception:
        traceback.print_exc()
        gc.collect()
