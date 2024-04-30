import requests
import time
import traceback
import os
from khayyam import JalaliDatetime
from datetime import datetime

profile = os.environ.get('GHEYMAT_CHAND_PROFILE')
bot_token = os.environ.get('BOT_TOKEN')
chat_id = os.environ.get('CHAT_ID')
private_chat_id = os.environ.get('PRIVATE_CHAT_ID')

lastPrice = 0
url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
if profile == "production":
  requests.post(url, data={'chat_id': private_chat_id, 'text': 'bot updated'})


def get_aban_tether_usdt_prices():
    try:
      nobitex_response = requests.get("https://abantether.com/management/all-coins")
      if(nobitex_response.status_code != 200):
        print(nobitex_response.content)
        return None, None
      for coin in nobitex_response.json():
          if coin['symbol'] == 'USDT':
              buy_price = int(float(coin.get('priceBuy')))
              sell_price = int(float(coin.get('priceSell')))
              return buy_price, sell_price
      return None, None
    except  Exception as e: 
      traceback.print_exc()
      return None, None


while True:
  if(datetime.now().second % 30 != 0):
    continue
  try:
    response = requests.get("https://milli.gold/api/v1/public/milli-price/detail")
    if(response.status_code != 200):
      print(f'res {response.text}')
      requests.post(url, data={'chat_id': private_chat_id, 'text': f'bot error {response.text}'})
      continue
    price = int(response.json()['price18']*100)
    now = JalaliDatetime.now()
    persian_date = now.strftime('%Y/%m/%d')
    persian_time = now.strftime('%H:%M:%S')
    text = f'Gold18K Milli {price:,} - {price:,}\n'
    ab_usdt_buy_price, ab_usdt_sell_price = get_aban_tether_usdt_prices()
    if ab_usdt_buy_price and ab_usdt_sell_price:
       text += f'USDT Aban Tether {ab_usdt_buy_price:,}-{ab_usdt_sell_price:,}\n'
    text += f'\n🕐 {persian_date} {persian_time}\n'
    text += '@gheymat_chande'

    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': 'true'}
    if price != lastPrice:
      if(profile == 'production'):
        response = requests.post(url, data=data)
        if response.status_code == 200:
          print('succeed')
        else:
          print(f'failed: {response.text}')
      else:
         print(text)
    lastPrice = price
  
    time.sleep(1)
  except  Exception as e: 
    traceback.print_exc()
