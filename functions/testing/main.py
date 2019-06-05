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
    return http_request.text

def hello_http(request):
    return get_page(url='https://www.ebay.co.uk/sch/i.html?_from=R40&_nkw=LEGO+75192&_in_kw=1&_ex_kw=&_sacat=0&_udlo=&_udhi=&LH_Auction=1&LH_ItemCondition=3&_ftrt=901&_ftrv=1&_sabdlo=&_sabdhi=&_samilow=&_samihi=&_sadis=15&_stpos=&_sargn=-1%26saslc%3D1&_fsradio2=%26LH_LocatedIn%3D1&_salic=3&LH_SubLocation=1&_sop=10&_dmd=1&_ipg=200')