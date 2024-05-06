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
bazar_token = ''

def get_aban_tether_usdt_prices():
    try:
      ab_response = requests.get("https://abantether.com/management/all-coins")
      if(ab_response.status_code != 200):
        print(ab_response.content)
        requests.post(url, data={'chat_id': private_chat_id, 'text': f'Aban tether error:\n {ab_response.text}'})
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
        requests.post(url, data={'chat_id': private_chat_id, 'text': f'Nobitex error:\n {nobitex_response.text}'})
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
        requests.post(url, data={'chat_id': private_chat_id, 'text': f'Tetherland error:\n {tetherland_response.text}'})
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
        requests.post(url, data={'chat_id': private_chat_id, 'text': f'Wallex error:\n {wallex_response.text}'})
        return None, None
    wallex_price = wallex_response.json()['result']['symbols']['USDTTMN']['OTC']['stats']['lastPrice']
    return wallex_price, wallex_price
  except  Exception as e: 
      traceback.print_exc()
      return None, None
  
def get_milli_prices():
    try:
      milli_response = requests.get("https://milli.gold/api/v1/public/milli-price/detail")
      if(milli_response.status_code != 200):
        requests.post(url, data={'chat_id': private_chat_id, 'text': f'Milli error:\n {response.text}'})
        return None, None
      milli_price = int(milli_response.json()['price18']*100)
      return milli_price, milli_price
    except  Exception as e: 
        traceback.print_exc()
        return None, None
    
def get_goldika_prices():
    try:
      goldika_response = requests.get("https://goldika.ir/api/public/price")
      if(goldika_response.status_code != 200):
        requests.post(url, data={'chat_id': private_chat_id, 'text': f'Goldika error:\n {response.text}'})
        return None, None
      goldika_price = goldika_response.json()['data']['price']
      goldika_buy_price = int(goldika_price['buy']/10)
      goldika_sell_price = int(goldika_price['sell']/10)
      return goldika_buy_price, goldika_sell_price
    except  Exception as e: 
        traceback.print_exc()
        return None, None

def get_bazar_token():   
  try:
    headers = {
        'Content-Type': 'application/json'
    }
    bazar_login_response = requests.post("https://web.baazar.ir/api/shop/authenticate/v2/web-login/", data={'username': '09124398514', 'password': '13@sMz&77', 'rememberMe': 'true'}, headers=headers)
    if(bazar_login_response.status_code != 200):
        requests.post(url, data={'chat_id': private_chat_id, 'text': f'Bazar login error:\n {bazar_login_response.text}'})
        return ''
    return bazar_login_response.json()['data']['token']
  except  Exception as e: 
      traceback.print_exc()
      return ''

def get_bazar_prices():   
  global bazar_token
  try:
    # token = None
    # if(datetime.now().minute == 30 or bazar_token == '' or bazar_token):
    #    token = get_bazar_token()
    # else:
    #    token = bazar_token
    token = get_bazar_token()
    if(token is None or token == ''):
      return None, None
    bazar_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    print(bazar_headers)

    bazar_response = requests.get("https://web.baazar.ir/api/shop/account/v1/dashboard", headers=bazar_headers)
    if(bazar_response.status_code != 200):
      print(bazar_response.content)
      requests.post(url, data={'chat_id': private_chat_id, 'text': f'Bazar  error:\n {bazar_response.text}'})
      return None, None
    bazar_price = bazar_response.json()['data']
    bazar_buy_price = int(int(bazar_price['goldBuyPrice'])/10)
    bazar_sell_price = int(int(bazar_price['goldSellPrice'])/10)
    return bazar_buy_price, bazar_sell_price
    
  except  Exception as e: 
      traceback.print_exc()
      return None, None


while True:
  try:
    now = JalaliDatetime.now()
    timestamp = int(time.time())
    prices = []
    text = ''
    prices.append(('🟡',''))
    milli_buy_price, milli_sell_price = get_milli_prices()
    if milli_buy_price and milli_sell_price:
       prices.append(('Milli',f'{milli_buy_price:,} - {milli_sell_price:,}'))
    
    goldika_buy_price, goldika_sell_price = get_goldika_prices()
    if goldika_buy_price and goldika_sell_price:
       prices.append(('Goldika',f'{goldika_buy_price:,} - {goldika_sell_price:,}'))
    
    prices.append(('\n💵',''))  

    ab_usdt_buy_price, ab_usdt_sell_price = get_aban_tether_usdt_prices()
    if ab_usdt_buy_price and ab_usdt_sell_price:
       prices.append(('Aban Tether',f'{ab_usdt_buy_price:,} - {ab_usdt_sell_price:,}'))
    
    nobitex_usdt_buy_price, nobitex_usdt_sell_price = get_nobitex_usdt_prices(timestamp)
    if nobitex_usdt_buy_price and nobitex_usdt_sell_price:
       prices.append(('Nobitex', f'{nobitex_usdt_buy_price:,} - {nobitex_usdt_sell_price:,}'))
      
    tetherland_usdt_buy_price, tetherland_usdt_sell_price = get_tetherland_usdt_prices()
    if tetherland_usdt_buy_price and tetherland_usdt_sell_price:
       prices.append(('Tether Land', f'{tetherland_usdt_buy_price:,} - {tetherland_usdt_sell_price:,}'))
      
    wallex_usdt_buy_price, wallex_usdt_sell_price = get_wallex_usdt_prices()
    if wallex_usdt_buy_price and wallex_usdt_sell_price:
       prices.append(('Wallex', f'{wallex_usdt_buy_price:,} - {wallex_usdt_sell_price:,}'))
      
    bazar_buy_price, bazar_sell_price = get_bazar_prices()
    if bazar_buy_price and bazar_sell_price:
       prices.append(('Bazar', f'{bazar_buy_price:,} - {bazar_sell_price:,}'))
      
    for name, price in prices:
      text += f"<code>{name:<15} {price}</code>\n"
    
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
  
    time.sleep(30)
  except  Exception as e: 
    traceback.print_exc()
