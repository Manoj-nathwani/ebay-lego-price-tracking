import json

from flask import escape
from google.cloud import datastore

client = datastore.Client()

def entity_exists(key):
    query = client.query(kind=key.kind)
    query.key_filter(key)
    return list(query.fetch())

def hello_http(request):
    request_args = request.args
    
    query = client.query(kind='SearchTerm')
    results = list(query.fetch())
    return json.dumps([
        x.key.id_or_name
        for x in results
    ])