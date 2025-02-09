import gc
import json
import os
import time
import traceback
import redis
import requests
from khayyam import JalaliDatetime
from bs4 import BeautifulSoup

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
        #milli_response = requests.get("http://65.109.177.25:5000/api/v1/public/milli-price/detail", timeout=1)
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

def get_digikala_prices():
    try:
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,fa;q=0.7",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "cookie": "tracker_glob_new=gwYXsNZ; _ga=GA1.1.962936932.1694238045; _hp2_id.1726062826=%7B%22userId%22%3A%223519327814619176%22%2C%22pageviewId%22%3A%225105757535278442%22%2C%22sessionId%22%3A%223161916218542471%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; tracker_glob_new=gwYXsNZ; _hp5_event_props.2724891150=%7B%7D; TS01d07deb=010231059187ad222d325f1ed046a6a37e2041ed3804c3fb624e4ce128115f5ede292cd463763b0ce0054721ae107cec0bbcdef1d330e23cf31578e123f6a2f167be4125ff7bed693ec707158e95e88bc09dcef15c; TS01b6ea4d=01023105911acf42d29c49f314cde3f5192a27dd9db59248ad990b9ac2055c05a86e9f668d47900bb84286ca94604b2825cd9b29736b8213a075a52cf8209a7d599ecc524a56b7853771c25dfac95d9b63118ce05d5054eb04f70e7860918533c6e36012b744f3d657c3e3f88063b62e31531d3a361c0f5663da5ef98ee0c9fe3f46bcf797; PHPSESSID=gi2124rdepiejsrr963j47goqh; ab_test_experiments=%5B%22229ea1a233356b114984cf9fa2ecd3ff%22%2C%22db7b11075496e04f0a6ef0d3a02d5264%22%2C%22f0fd80107233fa604679779d7e121710%22%2C%2237136fdc21e0b782211ccac8c2d7be63%22%5D; TS011434b1=01023105911950b9b35071929bf47b23b12f4f936104c3fb624e4ce128115f5ede292cd463df6e8b88c6afa89a7a9bc982d767805d0759a9b051cd2a75e99b5061eb2257b0816ae764120a3add5ab27ae87db2fda98fd93003ae29a5e53c268a798966bd39350f8e0d8b1aecb9f312cfa6584fe8ac; Digikala:User:Token:new=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo5NzcwMjMsInN1YiI6OTc3MDIzLCJleHBpcmVfdGltZSI6MTc0MTY4MDk2NCwiZXhwIjoxNzQxNjgwOTY0LCJwYXlsb2FkIjpbXSwicGFzc3dvcmRfdmVyc2lvbiI6MSwidHlwZSI6InRva2VuIn0.ZWbK3VgneJNKBr3dYFqxlwhDjDCCOOtvnjLCugFxOGs; Digikala:General:Location=Y3FoMHZWWWVFMmY1eXRxYmppTmlSQT09%26RG9PL09DN1BkVGhtSmZVNmEzcEpGQUJHbVBDQ0E4OFgzNHlVQ1luclg4bE55THVpYVhZV0NNZTMrRmlJM0JCOXFSbmtBS3BFR2NERWN2am9NVWtyWEE9PQ~~; tracker_session=9NrdAgY; _hp5_meta.2724891150=%7B%22userId%22%3A%224524843259322362%22%2C%22sessionId%22%3A%224313476656320835%22%2C%22sessionProperties%22%3A%7B%22time%22%3A1739091383222%2C%22referrer%22%3A%22https%3A%2F%2Fwww.digikala.com%2Fusers%2Flogin%2F%3FbackUrl%3Dhttps%3A%2F%2Fwww.digikala.com%2Fgold%2Forder%2F%26skipWelcome%3Dtrue%22%2C%22id%22%3A%224313476656320835%22%2C%22search_keyword%22%3A%22%22%2C%22utm%22%3A%7B%22source%22%3A%22%22%2C%22medium%22%3A%22%22%2C%22term%22%3A%22%22%2C%22content%22%3A%22%22%2C%22campaign%22%3A%22%22%7D%2C%22initial_pageview_info%22%3A%7B%22time%22%3A1739091383222%2C%22id%22%3A%221189957210728065%22%2C%22title%22%3A%22%D8%B7%D9%84%D8%A7%DB%8C%20%D8%AF%DB%8C%D8%AC%DB%8C%D8%AA%D8%A7%D9%84%20%D8%AF%DB%8C%D8%AC%DB%8C%E2%80%8C%DA%A9%D8%A7%D9%84%D8%A7%20%7C%20%D8%AE%D8%B1%DB%8C%D8%AF%20%D9%88%20%D9%81%D8%B1%D9%88%D8%B4%22%2C%22previous_page%22%3A%22%2Fusers%2Flogin%2F%22%2C%22url%22%3A%7B%22domain%22%3A%22www.digikala.com%22%2C%22path%22%3A%22%2Fgold%2Forder%2F%22%2C%22query%22%3A%22%3FskipWelcome%3Dtrue%22%2C%22hash%22%3A%22%22%7D%2C%22source_properties%22%3A%7B%22screen_height%22%3A823%2C%22screen_width%22%3A1512%7D%7D%7D%7D; _hp5_let.2724891150=1739091383244; TS010e7d7f=0102310591da1d55414380fb3c145e60198ef6c0ceebd951aebda1739ea14fc7f7b539e4c98da35e66196a41a11b56e2579c029c0e788aafae0da5b32993c30f7833745603ceb4f9742cca956f06b0610368015b89d75c4756e4fd02f1d9b2e86d4d12b947a2ba8eb083dbed009b895a4d5596d2dffbdd0dbdbdab6204559310976d9902f7d79542ebe9496e0c48b5e05a400b9b338b6a230bf47446d8f7ee700207f29104; TS01c77ebf=01023105919cda07fb269061af0faa50fa42abf9e3d129f38b615b98953477bb5888045a3ecee79ffb2a0e1dbd381c59bd13aa86e3f5403de28332e6bc21ab084453f1bfe08026d15dc47e77e834ab3d98c5bd01e0228b102ac483aa61cec24b52a992eff8bb38f56063899183e36249d4f6d6cae8f9bbd1ec86fcf9c3d9798b36cb750d8953773b2a97548d9ce04c1b19a2333f701b8dd8a498182a7bab338714379ae029f40f31a9f3cfce06b39875de27967a287476b33cb5e043df5276064cfae46a4ecdb41b0e5c07af8e0d7517d6d8acd5cb9baea149648e7eef534e97b6f14876f4; _ga_QQKVTD5TG8=GS1.1.1739091383.12.1.1739091796.0.0.0; _sp_ses.13cb=*; _sp_id.13cb=f6deb2c0-f8e9-4c4e-90fc-11b430099f6d.1694238044.12.1739091797.1739088983.06a554f2-9140-400d-bc9e-2f77bf235d7a.bf8b20d7-bb91-47fc-918c-225a79457035.52398bbb-9134-4dff-a3d7-b7ef7867ece8.1739091797382.1",
            "Referer": "https://www.digikala.com/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        digikala_response = requests.get("https://api.digikala.com/non-inventory/v1/prices/", timeout=1)
        if digikala_response.status_code != 200:
            print(f'milli error:\n{digikala_response.content}')
            requests.post(url, data={'chat_id': private_chat_id,
                                     'text': f'Digikala error:\n {digikala_response.status_code} \n {digikala_response.content}'},
                          timeout=1)
            return None, None
        digikala_price = int(digikala_response.json()['gold18']['price'] * 100)
        return digikala_price, digikala_price
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
                                      timeout=5)
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
        tala_dot_ir_response = requests.get("https://www.tala.ir/ajax/price/talair", timeout=5)
        if tala_dot_ir_response.status_code != 200:
            print(f'tala.ir error:\n{tala_dot_ir_response.content}')
            requests.post(url, data={'chat_id': private_chat_id,
                                     'text': f'Tala.ir error:\n {tala_dot_ir_response.status_code} \n {tala_dot_ir_response.content}'},
                          timeout=1)
            return None, None
        tala_dot_ir_price = int(tala_dot_ir_response.json()['gold']['gold_18k']['v'].replace(",", ""))
        return tala_dot_ir_price, tala_dot_ir_price
    except Exception:
        traceback.print_exc()
        return None, None
    
def get_talayen_prices():
    try:
        talayen_response = requests.get("https://tlyn.ir/", timeout=1)
        if talayen_response.status_code != 200:
            print(f'talayen error:\n{talayen_response.content}')
            requests.post(url, data={'chat_id': private_chat_id,
                                     'text': f'Talayen error:\n {talayen_response.status_code} \n {talayen_response.content}'},
                          timeout=1)
            return None, None
        soup = BeautifulSoup(talayen_response.content, 'html.parser')
        buy_element = soup.select_one('#buy-price-n .elementor-shortcode')
        sell_element = soup.select_one('#sale-price-n .elementor-shortcode')
        return extract_tlyn_number(buy_element),  extract_tlyn_number(sell_element)
    except Exception:
        traceback.print_exc()
        return None, None
    
def extract_tlyn_number(value):
    if value:
        return int(value.get_text(strip=True).replace(',', ''))
    else:
        return None

def get_abshode_prices():
    try:
        abshode_response = requests.get("http://65.109.177.25/api/v1/crawler/abshdanaghdy/prices", timeout=5)
        if abshode_response.status_code != 200:
            print(f'abshode error:\n{abshode_response.content}')
            requests.post(url, data={'chat_id': private_chat_id,
                                     'text': f'Abshode error:\n {abshode_response.status_code} \n {abshode_response.content}'},
                          timeout=1)
            return None, None
        unofficial_price = int(int(abshode_response.json()['unofficial'])/4.331802) if abshode_response.json()['unofficial'] else None
        cash_price = int(int(abshode_response.json()['cash'])/4.331802) if abshode_response.json()['cash'] else None
        return unofficial_price, cash_price
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
    except Exception as e:
        print(f"Error storing prices in Redis: {e}")
        traceback.print_exc()

def check_milli_price(price):
    if price and (price <= 5400000):
        #requests.post(url, data={'chat_id': 296382884, 'text': f'milli price {price}'})
        requests.post(url, data={'chat_id': -4636462998, 'text': f'milli price {price}'})

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
        check_milli_price(milli_buy_price)
        if milli_buy_price:
            prices.append(('میلی', f'{milli_buy_price:,} - {milli_sell_price:,}'))
            dataset_prices['milli.gold']= int((milli_buy_price+ milli_sell_price)/2)
        
        abshode_unofficial_price, abshode_cash_price = get_abshode_prices()

        if abshode_cash_price:
            prices.append(('نقدی', f'{abshode_cash_price:,} - {abshode_cash_price:,}'))
            dataset_prices['abshode_cash']= abshode_cash_price
        
        if abshode_unofficial_price:
            prices.append(('غیررسمی', f'{abshode_unofficial_price:,} - {abshode_unofficial_price:,}'))
            dataset_prices['abshode_unofficial']= abshode_unofficial_price

        tala_dot_ir_buy_price, tala_dot_ir_sell_price = get_tala_dot_ir_prices()
        if tala_dot_ir_buy_price and tala_dot_ir_sell_price:
            prices.append(('طلا', f'{tala_dot_ir_buy_price:,} - {tala_dot_ir_sell_price:,}'))
            dataset_prices['tala.ir']= int((tala_dot_ir_buy_price+ tala_dot_ir_sell_price)/2)
        

        talasea_buy_price, talasea_sell_price = get_talasea_prices()
        if talasea_buy_price and talasea_sell_price:
            prices.append(('طلاسی', f'{talasea_buy_price:,} - {talasea_sell_price:,}'))
            dataset_prices['talasi']= int((talasea_buy_price+ talasea_sell_price)/2)

        talayen_buy_price, talayen_sell_price = get_talayen_prices()
        if talayen_buy_price and talayen_sell_price:
            prices.append(('طلاین', f'{talayen_buy_price:,} - {talayen_sell_price:,}'))
            dataset_prices['talayen']= int((talayen_buy_price+ talayen_sell_price)/2)

        goldika_buy_price, goldika_sell_price = get_goldika_prices()
        if goldika_buy_price and goldika_sell_price:
            prices.append(('گلدیکا', f'{goldika_buy_price:,} - {goldika_sell_price:,}'))
            dataset_prices['goldika']= int((goldika_buy_price+ goldika_sell_price)/2)

        bazar_buy_price, bazar_sell_price = get_bazar_prices()
        if bazar_buy_price and bazar_sell_price:
            prices.append(('بازر', f'{bazar_buy_price:,} - {bazar_sell_price:,}'))
            dataset_prices['bazar']= int((bazar_buy_price+ bazar_sell_price)/2)

        digikala_buy_price, digikala_sell_price = get_digikala_prices()
        if digikala_buy_price and digikala_sell_price:
            prices.append(('دیجیکالا', f'{digikala_buy_price:,} - {digikala_sell_price:,}'))
            dataset_prices['digikala']= int((digikala_buy_price+ digikala_sell_price)/2)

        # daric_buy_price, daric_sell_price = get_daric_prices(timestamp)
        # if daric_buy_price and daric_sell_price:
        #     prices.append(('داریک', f'{daric_buy_price:,} - {daric_sell_price:,}'))
        #     dataset_prices['داریک']= int((daric_buy_price+ daric_sell_price)/2)
        
        store_prices_in_redis({'time': timestamp, 'prices': dataset_prices})
        if milli_buy_price and tala_dot_ir_buy_price:
            prices.append(('اختلاف میلی و طلا', f'{milli_buy_price - tala_dot_ir_buy_price:,}'))
        if milli_buy_price and abshode_cash_price:
            prices.append(('اختلاف میلی و نقدی', f'{milli_buy_price - abshode_cash_price:,}'))

        for name, price in prices:
            text += f"<code>{name}{' ' * (10 - len(name))}{price}</code>\n"

        persian_date = now.strftime('%Y/%m/%d')
        persian_time = now.strftime('%H:%M:%S')
        text += f'\n🕐 {persian_date} {persian_time}\n'
        text += '@gheymat_chande'

        data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': 'true'}
        if (profile == 'production'):
            response = requests.post(url, data=data, timeout=10)
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
