import requests
from bs4 import BeautifulSoup
import json
import re
import discord, asyncio
from discord.ext import commands
from dotenv import load_dotenv
import os
import sys

load_dotenv()


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

proxies = {
    'https': os.getenv('PROXY')
}


porshe = 1065664376142573640
ferrari = 1065664710256623657
lamba = 1065664862119800873
bmw = 1065664766116364419

def craiglist():
    s = requests.Session()
    urls = ['https://sapi.craigslist.org/web/v7/postings/search/full?auto_make_model=porshe&auto_transmission=1&batch=20-0-360-0-0&cc=US&lang=en&max_auto_year=2015&searchPath=cta', 'https://sapi.craigslist.org/web/v7/postings/search/full?auto_make_model=bmw&auto_transmission=1&batch=20-0-360-0-0&cc=US&lang=en&max_auto_miles=150000&max_auto_year=1997&searchPath=cta', 'https://sapi.craigslist.org/web/v7/postings/search/full?auto_make_model=lamborghini&batch=20-0-360-0-0&cc=US&lang=en&searchPath=cta', 'https://sapi.craigslist.org/web/v7/postings/search/full?auto_make_model=ferrari&batch=20-0-360-0-0&cc=US&lang=en&searchPath=cta']
    
    msgs = {
        'porshe': '',
        'bmw': '',
        'lamba': '',
        'ferrari': '',
    }

    with open('craigs.json', 'r') as f:
        checked = json.load(f)


    for url in urls:
        try:
            r = s.get(url)
        except:
            continue
        data = json.loads(r.text)['data']
        if len(data['items']) == 0:
            continue
        min_id = int(data['decode']['minPostingId'])
        for car in data['items']:
            link = f'https://{data["decode"]["locations"][int(car[4].split(":")[0])][1]}.craigslist.org/brw/cto/{min_id+car[0]}.html'
            try:
                r = s.get(link, headers=headers)
            except:
                continue
            if min_id + car[0] in checked:
                continue
            msg = ''
            msg = msg + '-----> Posting title: ' + car[-1] + '\n'
            mile = re.search(r'odometer: <b>\d*', r.text)
            if mile == None:
                continue
            msg = msg + '-----> Mileage: ' + mile[0].split('<b>')[1] + '\n'
            msg = msg + '-----> Price: ' + str(car[3]) + '\n'
            msg = msg + '-----> Link: $' + link
            if 'https://sapi.craigslist.org/web/v7/postings/search/full?auto_make_model=porshe&auto_transmission=1&batch=20-0-360-0-0&cc=US&lang=en&max_auto_year=2015&searchPath=cta' == url:
                msgs['porshe'] += '\n' + '\n' + msg
            elif 'https://sapi.craigslist.org/web/v7/postings/search/full?auto_make_model=bmw&auto_transmission=1&batch=20-0-360-0-0&cc=US&lang=en&max_auto_miles=150000&max_auto_year=1997&searchPath=cta' == url:
                msgs['bmw'] += '\n' + '\n' + msg
            elif 'https://sapi.craigslist.org/web/v7/postings/search/full?auto_make_model=lamborghini&batch=20-0-360-0-0&cc=US&lang=en&searchPath=cta' == url:
                msgs['lamba'] += '\n' + '\n' + msg
            elif 'https://sapi.craigslist.org/web/v7/postings/search/full?auto_make_model=ferrari&batch=20-0-360-0-0&cc=US&lang=en&searchPath=cta' == url:
                msgs['ferrari'] += '\n' + '\n' + msg
            checked.append(min_id + car[0])

    with open('craigs.json', 'w') as f:
        json.dump(checked, f)


    return msgs


def carguru():
    s = requests.Session()
    urls = ['https://www.cargurus.com/Cars/preflightResults.action?zip=33009&inventorySearchWidgetType=AUTO&srpVariation=DEFAULT_SEARCH&searchId=afd8088a-7173-4172-b4ad-cdd38b0551f0&transmission=M&nonShippableBaseline=906&shopByTypes=MIX&sortDir=ASC&sourceContext=carGurusHomePageModel&distance=50&sortType=AGE_IN_DAYS&endYear=2015&entitySelectingHelper.selectedEntity=m48',
    'https://www.cargurus.com/Cars/preflightResults.action?zip=33009&inventorySearchWidgetType=AUTO&srpVariation=DEFAULT_SEARCH&searchId=7fac9cb9-bba5-4947-ac2b-b783693b3231&transmission=M&nonShippableBaseline=56&maxMileage=150000&shopByTypes=MIX&sortDir=ASC&sourceContext=carGurusHomePageModel&distance=50&sortType=AGE_IN_DAYS&endYear=1997&entitySelectingHelper.selectedEntity=m3',
    'https://www.cargurus.com/Cars/preflightResults.action?zip=33009&inventorySearchWidgetType=AUTO&srpVariation=DEFAULT_SEARCH&sellerHierarchyTypes=PRIVATE&searchId=01065332-774b-41d5-bc38-c1c9865b2943&nonShippableBaseline=188&shopByTypes=NEAR_BY&sortDir=ASC&sourceContext=carGurusHomePageModel&distance=50&sortType=AGE_IN_DAYS&entitySelectingHelper.selectedEntity=m34',
    'https://www.cargurus.com/Cars/preflightResults.action?zip=33009&inventorySearchWidgetType=AUTO&srpVariation=DEFAULT_SEARCH&searchId=dac04f92-0e05-42ba-9ac6-38da7c1f945a&nonShippableBaseline=202&shopByTypes=NEAR_BY&sortDir=ASC&sourceContext=carGurusHomePageModel&distance=50&sortType=AGE_IN_DAYS&entitySelectingHelper.selectedEntity=m25']

    msgs = {
        'porshe': '',
        'bmw': '',
        'lamba': '',
        'ferrari': '',
    }

    with open('carsguru.json', 'r') as f:
        checked = json.load(f)


    for url in urls:
        try:
            r = s.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            continue
        if r.status_code == 403:
            r = s.get(url, headers=headers, proxies=proxies)
        if r.status_code != 200:
            continue
        cars = json.loads(r.text)['listings']
        
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
            if 'https://www.cargurus.com/Cars/preflightResults.action?zip=33009&inventorySearchWidgetType=AUTO&srpVariation=DEFAULT_SEARCH&searchId=afd8088a-7173-4172-b4ad-cdd38b0551f0&transmission=M&nonShippableBaseline=906&shopByTypes=MIX&sortDir=ASC&sourceContext=carGurusHomePageModel&distance=50&sortType=AGE_IN_DAYS&endYear=2015&entitySelectingHelper.selectedEntity=m48' == url:
                msgs['porshe'] += '\n' + '\n' + msg
            elif 'https://www.cargurus.com/Cars/preflightResults.action?zip=33009&inventorySearchWidgetType=AUTO&srpVariation=DEFAULT_SEARCH&searchId=7fac9cb9-bba5-4947-ac2b-b783693b3231&transmission=M&nonShippableBaseline=56&maxMileage=150000&shopByTypes=MIX&sortDir=ASC&sourceContext=carGurusHomePageModel&distance=50&sortType=AGE_IN_DAYS&endYear=1997&entitySelectingHelper.selectedEntity=m3' == url:
                msgs['bmw'] += '\n' + '\n' + msg
            elif 'https://www.cargurus.com/Cars/preflightResults.action?zip=33009&inventorySearchWidgetType=AUTO&srpVariation=DEFAULT_SEARCH&sellerHierarchyTypes=PRIVATE&searchId=01065332-774b-41d5-bc38-c1c9865b2943&nonShippableBaseline=188&shopByTypes=NEAR_BY&sortDir=ASC&sourceContext=carGurusHomePageModel&distance=50&sortType=AGE_IN_DAYS&entitySelectingHelper.selectedEntity=m34' == url:
                msgs['lamba'] += '\n' + '\n' + msg
            elif 'https://www.cargurus.com/Cars/preflightResults.action?zip=33009&inventorySearchWidgetType=AUTO&srpVariation=DEFAULT_SEARCH&searchId=dac04f92-0e05-42ba-9ac6-38da7c1f945a&nonShippableBaseline=202&shopByTypes=NEAR_BY&sortDir=ASC&sourceContext=carGurusHomePageModel&distance=50&sortType=AGE_IN_DAYS&entitySelectingHelper.selectedEntity=m25' == url:
                msgs['ferrari'] += '\n' + '\n' + msg

            checked.append(car['id'])
        
    with open('carsguru.json', 'w') as f:
        json.dump(checked, f)


    return msgs


def carscom():
    s = requests.Session()
    urls = ['https://www.cars.com/shopping/results/?dealer_id=&keyword=&list_price_max=&list_price_min=&makes[]=porsche&maximum_distance=20&mileage_max=&page_size=20&sort=listed_at_desc&stock_type=all&transmission_slugs[]=manual&year_max=2016&year_min=&zip=33009',
    'https://www.cars.com/shopping/results/?dealer_id=&keyword=&list_price_max=&list_price_min=&makes[]=bmw&maximum_distance=30&mileage_max=150000&page_size=20&sort=listed_at_desc&stock_type=all&transmission_slugs[]=manual&year_max=1997&year_min=&zip=33009',
    'https://www.cars.com/shopping/results/?dealer_id=&keyword=&list_price_max=&list_price_min=&makes[]=lamborghini&maximum_distance=30&mileage_max=&page_size=20&seller_type[]=private_seller&sort=listed_at_desc&stock_type=all&year_max=&year_min=&zip=33009',
    'https://www.cars.com/shopping/results/?makes[]=ferrari&sort=listed_at_desc&zip=33009']

    msgs = {
        'porshe': '',
        'bmw': '',
        'lamba': '',
        'ferrari': '',
    }

    with open('carscom.json', 'r') as f:
        checked = json.load(f)

    for url in urls:
        try:
            r = s.get(url, headers=headers)
        except:
            continue
        if r.status_code == 403:
            r = s.get(url, headers=headers, proxies=proxies)
        if r.status_code != 200:
            continue
        bs = BeautifulSoup(r.text, 'lxml')
        cars = bs.find_all('div',class_='vehicle-card')

        if len(cars) == 0:
            continue
        for car in cars[:5]:
            link = car.find('a')['href']
            if link.split('/')[2] in checked:
                continue
            msg = ''
            msg = msg + '-----> Posting title: ' + car.find('h2', class_='title').text + '\n'
            msg = msg + '-----> Mileage: ' + car.find('div', class_='mileage').text + '\n'
            msg = msg + '-----> Price: ' + car.find('span', class_='primary-price').text + '\n'
            msg = msg + '-----> Link: $' + f'https://www.cars.com{link}'
            if 'https://www.cars.com/shopping/results/?dealer_id=&keyword=&list_price_max=&list_price_min=&makes[]=porsche&maximum_distance=20&mileage_max=&page_size=20&sort=listed_at_desc&stock_type=all&transmission_slugs[]=manual&year_max=2016&year_min=&zip=33009' == url:
                msgs['porshe'] += '\n' + '\n' + msg
            elif 'https://www.cars.com/shopping/results/?dealer_id=&keyword=&list_price_max=&list_price_min=&makes[]=bmw&maximum_distance=30&mileage_max=150000&page_size=20&sort=listed_at_desc&stock_type=all&transmission_slugs[]=manual&year_max=1997&year_min=&zip=33009' == url:
                msgs['bmw'] += '\n' + '\n' + msg
            elif 'https://www.cars.com/shopping/results/?dealer_id=&keyword=&list_price_max=&list_price_min=&makes[]=lamborghini&maximum_distance=30&mileage_max=&page_size=20&seller_type[]=private_seller&sort=listed_at_desc&stock_type=all&year_max=&year_min=&zip=33009' == url:
                msgs['lamba'] += '\n' + '\n' + msg
            elif 'https://www.cars.com/shopping/results/?makes[]=ferrari&sort=listed_at_desc&zip=33009' == url:
                msgs['ferrari'] += '\n' + '\n' + msg
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

    asyncio.run_coroutine_threadsafe(send_msg(porshe, guru['porshe']), bot.loop)

    await asyncio.sleep(5)

    asyncio.run_coroutine_threadsafe(send_msg(bmw, guru['bmw']), bot.loop)

    await asyncio.sleep(5)

    asyncio.run_coroutine_threadsafe(send_msg(lamba, guru['lamba']), bot.loop)

    await asyncio.sleep(5)

    asyncio.run_coroutine_threadsafe(send_msg(ferrari, guru['ferrari']), bot.loop)

    await asyncio.sleep(5)

    asyncio.run_coroutine_threadsafe(send_msg(porshe, com['porshe']), bot.loop)

    await asyncio.sleep(5)

    asyncio.run_coroutine_threadsafe(send_msg(bmw, com['bmw']), bot.loop)

    await asyncio.sleep(5)

    asyncio.run_coroutine_threadsafe(send_msg(lamba, com['lamba']), bot.loop)

    await asyncio.sleep(5)

    asyncio.run_coroutine_threadsafe(send_msg(ferrari, com['ferrari']), bot.loop)

    await asyncio.sleep(5)
    asyncio.run_coroutine_threadsafe(send_msg(porshe, craig['porshe']), bot.loop)

    await asyncio.sleep(5)

    asyncio.run_coroutine_threadsafe(send_msg(bmw, craig['bmw']), bot.loop)

    await asyncio.sleep(5)

    asyncio.run_coroutine_threadsafe(send_msg(lamba, craig['lamba']), bot.loop)

    await asyncio.sleep(5)

    asyncio.run_coroutine_threadsafe(send_msg(ferrari, craig['ferrari']), bot.loop)


    await asyncio.sleep(60*60)



guru = carguru()

com = carscom()

craig = craiglist()
 

bot.run(os.getenv('AUTO'))
