import json

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
    
    query = client.query(kind='SearchTerm')
    results = list(query.fetch())
    output = json.dumps([
        {
            'id': x.key.id_or_name,
            'percentiles': x['percentiles'] if 'percentiles' in x else {},
            'listings': x['listings'],
            '25_75_gap': x['25_75_gap'],
            'average': x['average'],
        }
        for x in results
    ])
    return (output, 200, {'Access-Control-Allow-Origin': '*'})