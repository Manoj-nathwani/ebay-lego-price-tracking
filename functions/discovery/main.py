import os, logging, json
from datetime import datetime

import requests
from flask import escape
from bs4 import BeautifulSoup
from google.cloud import datastore

os.environ['TZ'] = 'Europe/London'
client = datastore.Client()

def get_page(url):
    logging.info('Fetching url: {}'.format(url))
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36'}
    http_request = requests.get(url, headers=headers)
    assert http_request.status_code == 200, 'http_request error'
    return BeautifulSoup(http_request.text, 'html.parser')

def hello_http(request):
    request_args = request.args
    assert 'search_term' in request_args
    search_term = request_args['search_term']
    
    url = 'https://www.ebay.co.uk/sch/i.html?_from=R40&_sacat=0&LH_Auction=1&LH_ItemCondition=3&_ftrt=901&_ftrv=1&_sadis=200&_stpos=leeds&_dmd=1&_ipg=200&_nkw={search_term}&LH_LocatedIn=3'.format(
        search_term=search_term
    )
    page_html = get_page(url=url)
    rows = page_html\
        .find('div', {"id": "ResultSetItems"})\
        .ul.find_all('li', recursive=False)

    rows_inserted = 0
    for row in rows:
        if 'sresult' not in row.attrs['class']: break
        sku = row['listingid']
        price = row.find('li', class_='lvprice prc').text.replace('\n£', '').replace('\n', '')
        shipping = 0
        if row.find('span', class_='fee'):
                shipping = row.find('span', class_='fee')\
                .text.split(' ')[1].replace('£','')
        auction_ends = row.find('span', class_='tme').span['timems']
        image = row.img['src']
        description = row.h3.a.text
        
        key = client.key('Listing', sku)
        entity = datastore.Entity(key=key, exclude_from_indexes=('price', 'shipping', 'shipping_cost', 'image', 'description'))
        entity['search_term'] = search_term
        entity['price'] = float(price)
        entity['shipping'] = float(shipping)
        entity['auction_ends'] = datetime.fromtimestamp(int(auction_ends)/1000)
        entity['image'] = image
        entity['description'] = description
        client.put(entity)
        rows_inserted += 1
        
    return json.dumps({'rows_inserted': rows_inserted})