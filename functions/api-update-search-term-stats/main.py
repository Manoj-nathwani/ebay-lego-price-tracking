import json
from flask import escape
import numpy as np
from google.cloud import datastore

client = datastore.Client()
batch = client.batch()

def update_search_term(search_term):
    # get listings
    parent_key = client.key('SearchTerm', search_term)    
    query = client.query(kind='Listing', ancestor=parent_key)
    query.add_filter('hidden', '=', False)
    entities = list(query.fetch())
    # calculate things
    prices = [x['total_price'] for x in entities]
    percentiles = {
        '0': np.percentile(prices, 0),
        '25': np.percentile(prices, 25),
        '50': np.percentile(prices, 50),
        '75': np.percentile(prices, 75),
        '100': np.percentile(prices, 100)
    }    
    # update parent_key percentiles    
    entity = datastore.Entity(key=parent_key, exclude_from_indexes=('listings', 'percentiles', '25_75_gap', 'average'))
    entity.update({
        'listings': len(prices),
        'percentiles': percentiles,
        '25_75_gap': percentiles['75'] - percentiles['25'],
        'average': np.average(prices),
    })
    batch.put(entity)

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
    
    batch.begin()
    if 'search_term' in request_args:
        update_search_term(request_args['search_term'])
    else:
        query = client.query(kind='SearchTerm')
        results = list(query.fetch())
        for listing in results:
            update_search_term(listing.key.id_or_name)
    batch.commit()
    return (json.dumps('Success'), 200, {'Access-Control-Allow-Origin': '*'})


    
    