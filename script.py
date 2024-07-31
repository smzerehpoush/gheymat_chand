import gc
import os
import time
import traceback
import requests
from khayyam import JalaliDatetime

profile = os.environ.get('GHEYMAT_CHAND_PROFILE')
bot_token = os.environ.get('BOT_TOKEN')
chat_id = os.environ.get('CHAT_ID')
private_chat_id = os.environ.get('PRIVATE_CHAT_ID')

lastPrice = 0
url = f'https://api.telegram.org/bot{bot_token}/sendMessage'


def get_milli_price():
    try:
        milli_response = requests.get("https://milli.gold/api/v1/public/milli-price/detail", timeout=1)
        if (milli_response.status_code != 200):
            print(f'milli error:\n{milli_response.content}')
            requests.post(url, data={'chat_id': private_chat_id,
                                     'text': f'Milli Gold error:\n {milli_response.status_code} \n {milli_response.content}'},
                          timeout=1)
            return None
        milli_price = int(milli_response.json()['price18'] * 100)
        return milli_price
    except  Exception:
        traceback.print_exc()
        return None
    
def get_tala_dot_ir_price():
    try:
        tala_dot_ir_response = requests.get("https://www.tala.ir/ajax/price/talair", timeout=1)
        if (tala_dot_ir_response.status_code != 200):
            print(f'milli error:\n{tala_dot_ir_response.content}')
            requests.post(url, data={'chat_id': private_chat_id,
                                     'text': f'Milli Gold error:\n {tala_dot_ir_response.status_code} \n {tala_dot_ir_response.content}'},
                          timeout=1)
            return None
        tala_dot_ir_price = int(tala_dot_ir_response.json()['gold']['gold_18k']['v'].replace(",",""))
        return tala_dot_ir_price
    except  Exception:
        traceback.print_exc()
        return None


while True:
    try:
        now = JalaliDatetime.now()
        timestamp = int(time.time())
        print(f'start at {JalaliDatetime.now()}')
        prices = []
        text = ''
        prices.append(('قیمت طلا 🟡', ''))
        milli_price = get_milli_price()
        prices.append(('میلی', f'{milli_price:,}'))
        tala_dot_ir_price = get_tala_dot_ir_price()
        prices.append(('سایت طلا', f'{tala_dot_ir_price:,}'))
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
        time.sleep(20)
        gc.collect()
    except Exception as e:
        traceback.print_exc()
        gc.collect()
