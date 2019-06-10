import os, json

from flask import escape
from google.cloud import datastore

os.environ['TZ'] = 'Europe/London'
client = datastore.Client()

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
    search_term = request_args['search_term']#.replace('%20', ' ')
    
    parent_key = client.key('SearchTerm', search_term)
    query = client.query(kind='Listing', ancestor=parent_key)
    query.add_filter('hidden', '=', False)
    output = [
        {
            'id': x.key.id_or_name,
            'price': x['price'],
            'shipping': x['shipping'],
            'total_price': x['total_price'],
            'auction_ends': x['auction_ends'].strftime("%d/%m/%Y, %H:%M:%S"),
            'auction_ends_formatted': {
                'year': x['auction_ends'].year,
                'month': x['auction_ends'].month,
                'day': x['auction_ends'].day,
                'hour': x['auction_ends'].hour,
                'minute': x['auction_ends'].minute
            },
            'image': x['image'],
            'description': x['description'],            
        }
        for x in list(query.fetch())
    ]
    output = sorted(output, key = lambda i: i['total_price'], reverse=False) 
    return (json.dumps(output), 200, {'Access-Control-Allow-Origin': '*'})


    
    