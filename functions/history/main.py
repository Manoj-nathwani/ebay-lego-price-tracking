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

def entity_exists(key):
    query = client.query(kind=key.kind)
    query.key_filter(key)
    return list(query.fetch())

def hello_http(request):
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    request_args = request.args
    assert 'search_term' in request_args
    search_term = request_args['search_term']
    
    url = 'https://www.ebay.co.uk/sch/i.html?_from=R40&_nkw={search_term}&_in_kw=1&_ex_kw&_sacat=0&LH_Sold=1&_udlo&_udhi&_samilow&_samihi&_sadis=15&_stpos&_sargn=-1%26saslc%3D1&_fsradio2=%26LH_LocatedIn%3D1&_salic=3&LH_SubLocation=1&_sop=10&_dmd=1&_ipg=200&LH_Complete=1&_clu=2&_fcid=3&_localstpos&gbr=1&LH_ItemCondition=1000&_udlo=50'.format(
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
        price = float(row.find('li', class_='lvprice prc').span.text.replace('£', '').replace('\n', '').replace('\t', '').replace(',', ''))
        shipping = 0
        if row.find('span', class_='fee'):
            shipping = float(row.find('span', class_='fee')\
                .text.split(' ')[1].replace('£',''))
        auction_ends = datetime.strptime(
            row.find('span', class_='tme').span.text,
            '%d-%b %H:%M'
        )
        if datetime.now().month < 6:
            if auction_ends.month < 6:
                # we can guess it's this year
                auction_ends = auction_ends.replace(year=datetime.now().year)
            else:
                # we can guess it's last year
                auction_ends = auction_ends.replace(year=datetime.now().year-1)
        else:
            auction_ends = auction_ends.replace(year=datetime.now().year)
        image_tag = row.find('div', class_='lvpicinner').img
        image = [x for x in str(image_tag).split('"') if 'jpg' in x][0]
        #image = image[0] if image else str(image_tag)
        description = row.h3.a.text
        
        parent_key = client.key('SearchTerm', search_term)
        if not entity_exists(parent_key):
            client.put(datastore.Entity(parent_key))
            
        key = client.key('Listing', sku, parent=parent_key)
        if not entity_exists(key):
            entity = datastore.Entity(key=key, exclude_from_indexes=('price', 'shipping', 'shipping_cost', 'image', 'description'))
            entity['price'] = price
            entity['checked'] = False
            entity['hidden'] = False
            entity['shipping'] = shipping
            entity['auction_ends'] = auction_ends
            entity['image'] = image
            entity['description'] = description
            entity['total_price'] = price + shipping
            client.put(entity)
            rows_inserted += 1
        
    output = json.dumps({'rows_inserted': rows_inserted})
    return (output, 200, {'Access-Control-Allow-Origin': '*'})




