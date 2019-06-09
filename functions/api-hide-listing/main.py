from flask import escape
from google.cloud import datastore

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
    assert 'listing_id' in request_args
    assert 'search_term' in request_args
    listing_id = request_args['listing_id']
    search_term = request_args['search_term']
    
    parent_key = client.key('SearchTerm', search_term)
    key = client.key('Listing', listing_id, parent=parent_key)
    
    query = client.query(kind=key.kind)
    query.key_filter(key)
    entity = list(query.fetch())[0]
    entity['hidden'] = True
    entity['checked'] = True
    client.put(entity)
    
    return ('Success', 200, {'Access-Control-Allow-Origin': '*'})


    
    