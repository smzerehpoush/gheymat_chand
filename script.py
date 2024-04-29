import requests
import time
import traceback
import os
from khayyam import JalaliDatetime
from datetime import datetime

bot_token = os.environ.get('BOT_TOKEN')
chat_id = os.environ.get('CHAT_ID')
private_chat_id = os.environ.get('PRIVATE_CHAT_ID')

lastPrice = 0
url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
requests.post(url, data={'chat_id': private_chat_id, 'text': 'bot updated'})

while True:
  if(datetime.now().second % 30 != 0):
    continue
  try:
    response = requests.get("https://milli.gold/api/v1/public/milli-price/detail")
    price = int(response.json()['price18']*1000)
    text = '<b>نرخ طلای ۱۸ عیار</b> ' + '(خرید و فروش)\n\n'
    now = JalaliDatetime.now()
    persian_date = now.strftime('%Y/%m/%d')
    persian_time = now.strftime('%H:%M:%S')
    text += f'<b>تاریخ: </b>' + f'{persian_date}\n'
    text += f'<b>ساعت</b>: {persian_time}\n\n'
    text += f'🟡 <b>{price:,}</b> ریال\n\n'
    text += '<b>«میلی؛ به قدرت طلا»</b>\n\n'
    text += '@milligold_liveprice'

  
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': 'true'}
    if price != lastPrice:
      response = requests.post(url, data=data)
      if response.status_code == 200:
        print('Message sent successfully.')
      else:
        print(f'Error sending message: {response.text}')
    lastPrice = price
  
    time.sleep(1)
  except  Exception as e: 
    traceback.print_exc()
