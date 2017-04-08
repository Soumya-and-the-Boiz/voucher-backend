import requests
from flask import Flask, request
app = Flask(__name__)

QUERY_TEMPLATE = 'http://data.fcc.gov/api/block/2010/find?format=json&latitude={}&longitude=}{}'

@app.route('/', methods='POST')
def hello_world():
    locations = request.json['locations']
    tracts = []
    for location in locations:
        lat, lng = location['lat'], location['lng']
        query_string = QUERY_TEMPLATE.format(lat, lng)
        response = requests.get(query_string).json()
        full_code = response['Block']['FIPS']
        tracts.append(full_code[5:11])
    output = ''
    for tract in tracts:
        output += tract + '\n'
    return output
