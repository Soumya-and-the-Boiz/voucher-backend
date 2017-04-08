import requests
from flask import Flask, request
app = Flask(__name__)

QUERY_TEMPLATE = 'http://data.fcc.gov/api/block/2010/find?format=json&latitude={}&longitude=}{}'

def get_tract(latitude, longitude):
    #TODO: DAVE!

@app.route('/', methods='POST')
def hello_world():
    locations = request.json['locations']
    tracts = []
    for location in locations:
        tracts.append(get_tract(location['lat'], location['lng']))
    output = ''
    for tract in tracts:
        output += tract + '\n'
    return output
