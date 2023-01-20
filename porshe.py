import requests
from bs4 import BeautifulSoup
import json
import re
import discord, asyncio
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

proxies = {
    'https': os.getenv('PROXY')
}


def autotrader():
    url = 'https://www.autotrader.com/rest/lsc/alpha/base?allListingType=all-cars&makeCode=POR&city=Hallandale&state=FL&zip=33009&location=%5Bobject%20Object%5D&transmissionCode=MAN&searchRadius=50&endYear=2015&marketExtension=include&newSearch=false&showAccelerateBanner=false&sortBy=datelistedDESC&numRecords=25&dma=%5Bobject%20Object%5D&channel=ATC&relevanceConfig=relevance-v2&stats=year%2Cderivedprice'
    with open('autotrader.json', 'r') as f:
        checked = json.load(f)
    try:
        r = requests.get(url, headers=headers)
    except requests.exceptions.ConnectionError:
        return []

    if r.status_code == 403:
        r = requests.get(url, headers=headers, proxies=proxies)
    if r.status_code != 200:
        return []
    try:
        cars = json.loads(r.text)['alphaShowcase']
    except json.decoder.JSONDecodeError:
        r = requests.get(url, headers=headers, proxies=proxies)
    msgs = []
    for car in cars[:5]:
        if car['id'] in checked:
            continue
        msg = ''
        msg = msg + '-----> Posting title: ' + car['title'] + '\n'
        msg = msg + '-----> Mileage: ' + car['mileage']['value'] + '\n'
        msg = msg + '-----> Price: $' + str(car['pricingDetail']['salePrice']) + '\n'
        msg = msg + '-----> Link: $' + f'https://www.autotrader.com/cars-for-sale/vehicledetails.xhtml?listingId={car["id"]}&allListingType=all-cars&zip=33009&makeCodeList=POR&state=FL&city=Hallandale&searchRadius=50&isNewSearch=false&referrer=%2Fcars-for-sale%2Fall-cars%3Fzip%3D33009%26makeCodeList%3DPOR&clickType=alpha'
        msgs.append(msg)
        checked.append(car['id'])
    
    with open('autotrader.json', 'w') as f:
        json.dump(checked, f)


    return msgs


def carguru():
    url = 'https://www.cargurus.com/Cars/preflightResults.action?zip=33009&inventorySearchWidgetType=AUTO&srpVariation=DEFAULT_SEARCH&searchId=afd8088a-7173-4172-b4ad-cdd38b0551f0&transmission=M&nonShippableBaseline=906&shopByTypes=MIX&sortDir=ASC&sourceContext=carGurusHomePageModel&distance=50&sortType=AGE_IN_DAYS&endYear=2015&entitySelectingHelper.selectedEntity=m48'
    with open('carsguru.json', 'r') as f:
        checked = json.load(f)
    try:
        r = requests.get(url, headers=headers)
    except requests.exceptions.ConnectionError:
        return []
    if r.status_code == 403:
        r = requests.get(url, headers=headers, proxies=proxies)
    if r.status_code != 200:
        return []
    cars = json.loads(r.text)['listings']
    msgs = []
    for car in cars[:5]:
        if car['id'] in checked:
            continue
        msg = ''
        try:
            msg = msg + '-----> Posting title: ' + car['listingTitle'] + '\n'
            msg = msg + '-----> Mileage: ' + str(car['mileage']) + '\n'
            msg = msg + '-----> Price: ' + car['priceString'] + '\n'
        except KeyError:
            continue
        msg = msg + '-----> Link: $' + f'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?entitySelectingHelper.selectedEntity=m48&distance=50&zip=33009&sourceContext=RecentSearches_false_0&startYear=2015&isRecentSearchView=true?io=true&format=jpg&auto=webp#listing={car["id"]}/NONE'
        msgs.append(msg)
        checked.append(car['id'])
    
    with open('carsguru.json', 'w') as f:
        json.dump(checked, f)


    return msgs


def craiglist():
    url = 'https://miami.craigslist.org/search/hallandale-fl/cta?lat=25.98100&lon=-80.14900&search_distance=15&min_price=&max_price=&auto_make_model=porshe&max_auto_year=2015&auto_transmission=1'
    with open('craigs.json', 'r') as f:
        checked = json.load(f)
    try:
        r = requests.get(url, headers=headers)
    except requests.exceptions.ConnectionError:
        return []
    if r.status_code == 403:
        r = requests.get(url, headers=headers, proxies=proxies)
    if r.status_code != 200:
        return []
    bs = BeautifulSoup(r.text, 'lxml')
    cars = bs.find_all(class_='result-row')
    msgs = []
    if len(cars) == 0:
        return msgs
    to = 5 if int(bs.find(class_='totalcount').text) >= 5 else int(bs.find(class_='totalcount').text)
    for car in cars[:to]:
        link = car.find('a')['href']
        if link.split('/')[-1].split('.')[0] in checked:
            continue
        msg = ''
        msg = msg + '-----> Posting title: ' + car.find(class_='result-heading').text + '\n'
        try:
            r = requests.get(link, headers=headers)
        except requests.exceptions.ConnectionError:
            continue
        if r.status_code != 200:
            continue
        msg = msg + '-----> Mileage: ' + re.search(r'odometer: <b>\d*', r.text)[0].split('<b>')[1] + '\n'
        msg = msg + '-----> Price: ' + car.find(class_='result-price').text + '\n'
        msg = msg + '-----> Link: $' + link
        msgs.append(msg)
        checked.append(link.split('/')[-1].split('.')[0])
    
    with open('craigs.json', 'w') as f:
        json.dump(checked, f)


    return msgs


def carscom():
    url = 'https://www.cars.com/shopping/results/?dealer_id=&keyword=&list_price_max=&list_price_min=&makes[]=porsche&maximum_distance=20&mileage_max=&page_size=20&sort=listed_at_desc&stock_type=all&transmission_slugs[]=manual&year_max=2016&year_min=&zip=33009'

    with open('carscom.json', 'r') as f:
        checked = json.load(f)
    try:
        r = requests.get(url, headers=headers)
    except requests.exceptions.ConnectionError:
        return []
    if r.status_code == 403:
        r = requests.get(url, headers=headers, proxies=proxies)
    if r.status_code != 200:
        return []
    bs = BeautifulSoup(r.text, 'lxml')
    cars = bs.find_all('div',class_='vehicle-card')
    msgs = []
    if len(cars) == 0:
        return msgs
    for car in cars[:5]:
        link = car.find('a')['href']
        if link.split('/')[2] in checked:
            continue
        msg = ''
        msg = msg + '-----> Posting title: ' + car.find('h2', class_='title').text + '\n'
        msg = msg + '-----> Mileage: ' + car.find('div', class_='mileage').text + '\n'
        msg = msg + '-----> Price: ' + car.find('span', class_='primary-price').text + '\n'
        msg = msg + '-----> Link: $' + f'https://www.cars.com{link}'
        msgs.append(msg)
        checked.append(link.split('/')[2])
    
    with open('carscom.json', 'w') as f:
        json.dump(checked, f)


    return msgs


bot = commands.Bot(intents=discord.Intents.default(),command_prefix='!')

async def send_msg(channel, text):
    channel = bot.get_channel(channel)
    await channel.send(text)

@bot.event
async def on_ready():
    channel = 1065664376142573640
    while True:
        msgs = autotrader()
        msgs+= carguru()
        msgs+= craiglist()
        msgs+= carscom()
        for msg in msgs:
            asyncio.run_coroutine_threadsafe(send_msg(channel, msg), bot.loop)
            await asyncio.sleep(10)
        await asyncio.sleep(20*60)

bot.run(os.getenv('PORSHE'))
