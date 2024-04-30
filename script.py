import requests
import time
import traceback
import os
import time
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
      ab_response = requests.get("https://abantether.com/management/all-coins")
      if(ab_response.status_code != 200):
        print(ab_response.content)
        return None, None
      for coin in ab_response.json():
          if coin['symbol'] == 'USDT':
              buy_price = int(float(coin.get('priceBuy')))
              sell_price = int(float(coin.get('priceSell')))
              return buy_price, sell_price
      return None, None
    except  Exception as e: 
      traceback.print_exc()
      return None, None
    
def get_nobitex_usdt_prices(timestamp):
  try:
    nobitex_url = f'https://chart.nobitex.ir/market/udf/history?symbol=USDTIRT&resolution=1&from={timestamp - 600}&to={timestamp}&countback=2&currencyCode=%EF%B7%BC'
    nobitex_response = requests.get(nobitex_url)
    if(nobitex_response.status_code != 200):
        print(nobitex_response.content)
        return None, None
    nobitex_prices = nobitex_response.json()['c']
    buy_price = int(nobitex_prices[0])
    sell_price = int(nobitex_prices[1])
    return buy_price, sell_price
  except  Exception as e: 
      traceback.print_exc()
      return None, None
  
def get_tetherland_usdt_prices():
  try:
    tetherland_response = requests.post("https://api.teterlands.com/api/v4/info", {'type':'web'})
    if(tetherland_response.status_code != 200):
        print(tetherland_response.content)
        return None, None
    tetherland_price = tetherland_response.json()['price']
    return tetherland_price, tetherland_price
  except  Exception as e: 
      traceback.print_exc()
      return None, None

def get_wallex_usdt_prices():
  try:
    wallex_response = requests.get("https://api.wallex.ir/v1/all-markets")
    if(wallex_response.status_code != 200):
        print(wallex_response.content)
        return None, None
    wallex_price = wallex_response.json()['result']['symbols']['USDTTMN']['OTC']['stats']['lastPrice']
    return wallex_price, wallex_price
  except  Exception as e: 
      traceback.print_exc()
      return None, None

while True:
  if(datetime.now().second % 30 != 0):
    continue
  try:
    now = JalaliDatetime.now()
    timestamp = int(time.time())
    text = ''
    response = requests.get("https://milli.gold/api/v1/public/milli-price/detail")
    if(response.status_code != 200):
      print(f'res {response.text}')
      requests.post(url, data={'chat_id': private_chat_id, 'text': f'bot error {response.text}'})
      continue
    price = int(response.json()['price18']*100)
    text += f'Gold18K Milli {price:,} - {price:,}\n'
    
    ab_usdt_buy_price, ab_usdt_sell_price = get_aban_tether_usdt_prices()
    if ab_usdt_buy_price and ab_usdt_sell_price:
       text += f'USDT Aban Tether {ab_usdt_buy_price:,}-{ab_usdt_sell_price:,}\n'
    
    nobitex_usdt_buy_price, nobitex_usdt_sell_price = get_nobitex_usdt_prices(timestamp)
    if nobitex_usdt_buy_price and nobitex_usdt_sell_price:
       text += f'USDT Nobitex {nobitex_usdt_buy_price:,}-{nobitex_usdt_sell_price:,}\n'
    
    tetherland_usdt_buy_price, tetherland_usdt_sell_price = get_tetherland_usdt_prices()
    if tetherland_usdt_buy_price and tetherland_usdt_sell_price:
       text += f'USDT Tether Land {tetherland_usdt_buy_price:,}-{tetherland_usdt_sell_price:,}\n'
    
    wallex_usdt_buy_price, wallex_usdt_sell_price = get_wallex_usdt_prices()
    if wallex_usdt_buy_price and wallex_usdt_sell_price:
       text += f'USDT Wallex {wallex_usdt_buy_price:,}-{wallex_usdt_sell_price:,}\n'
    
    
    persian_date = now.strftime('%Y/%m/%d')
    persian_time = now.strftime('%H:%M:%S')
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
  
    time.sleep(0.5)
  except  Exception as e: 
    traceback.print_exc()
