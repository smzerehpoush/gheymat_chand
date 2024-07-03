import gc
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
redis_connection = redis.Redis(host='redis', port=6379, db=0)

lastPrice = 0
url = f'https://api.telegram.org/bot{bot_token}/sendMessage'


def get_milli_prices():
    try:
        milli_response = requests.get("https://milli.gold/api/v1/public/milli-price/detail", timeout=1)
        if (milli_response.status_code != 200):
            print(f'milli error:\n{milli_response.content}')
            requests.post(url, data={'chat_id': private_chat_id,
                                     'text': f'Milli Gold error:\n {milli_response.status_code} \n {milli_response.content}'},
                          timeout=1)
            return None, None
        milli_price = int(milli_response.json()['price18'] * 100)
        return milli_price, milli_price
    except  Exception:
        traceback.print_exc()
        return None, None


while True:
    try:
        now = JalaliDatetime.now()
        timestamp = int(time.time())
        print(f'start at {timestamp}')
        prices = []
        text = ''
        prices.append(('قیمت طلا 🟡', ''))
        milli_buy_price, milli_sell_price = get_milli_prices()
        if milli_buy_price and milli_sell_price:
            prices.append(('میلی', f'{milli_buy_price:,} - {milli_sell_price:,}'))
            redis_connection.set('milli_price', str(milli_buy_price))

        for name, price in prices:
            text += f"<code>{name}{' ' * (10 - len(name))}{price}</code>\n"

        persian_date = now.strftime('%Y/%m/%d')
        persian_time = now.strftime('%H:%M:%S')
        text += f'\n🕐 {persian_date} {persian_time}\n'
        text += '@gheymat_chande'

        data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': 'true'}
        if price != lastPrice:
            if profile == 'production':
                response = requests.post(url, data=data, timeout=1)
                if response.status_code == 200:
                    print('succeed')
                else:
                    print(
                        f'failed to send message to telegram for body and response: \n{text}\n ----\n{response.text}\n####')
            else:
                print(text)
        lastPrice = price
        time.sleep(30)
        gc.collect()
    except Exception as e:
        traceback.print_exc()
        gc.collect()
