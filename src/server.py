from itertools import islice
import pandas as pd
import os
import json
import datetime, time

import importlib
ranking_spec = importlib.util.find_spec('ranking')
has_ranking = ranking_spec is not None
if has_ranking:
    from ranking.predict_rank import *

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

import boto3

from shapely.geometry import Polygon
from shapely.geometry import Point

from random import randint, choice

tract_data_coords = {}
tract_bounds = {}

NUMBER_OF_RESULTS = 5

with open('src/config.json', 'r') as fp :
    config = json.load(fp)

logging_client = boto3.client('logs', region_name='us-west-2', aws_access_key_id=config['CLOUDWATCHACCESS'], aws_secret_access_key=config['CLOUDWATCHSECRET'])

today = datetime.date.today()
logging_week = today - datetime.timedelta(today.weekday());
log_stream_info = logging_client.describe_log_streams(logGroupName='LikelyHoods', logStreamNamePrefix=logging_week.strftime('%m/%d/%Y'))['logStreams']
log_sequence_token = None

if not log_stream_info:
    logging_client.create_log_stream(logGroupName='LikelyHoods', logStreamName=logging_week.strftime('%m/%d/%Y'))
else:
    if 'uploadSequenceToken' in log_stream_info[0]:
        log_sequence_token = log_stream_info[0]['uploadSequenceToken']

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

CONNECTIVITY_INDEX = 0
EDUCATION_INDEX = 1
TRANSPORTATION_INDEX = 2
WELLNESS_INDEX = 3

@app.route('/', methods=['POST'])
@cross_origin()
def hello_world():
    if has_ranking:
        selected_tracts = [get_tract(float(item['lat']), float(item['lng'])) for item in request.json['markers']]
        selected_tracts = list(filter(None.__ne__, selected_tracts))
        log_request(request.json, selected_tracts)
        print('\t'.join(map(str, [datetime.datetime.utcnow(),
                                  request.remote_addr,
                                  selected_tracts
                                 ])))
        if selected_tracts:
            filter_func = lambda tract: not tract in selected_tracts
            predicted_tracts = predict(selected_tracts)
            max_results_needed = NUMBER_OF_RESULTS + len(selected_tracts)
            candidates = list(islice(filter(filter_func, predicted_tracts[:max_results_needed]), NUMBER_OF_RESULTS))
            return jsonify(create_response(candidates))
        else:
            return jsonify([])
    else:
        return jsonify(create_mocked_response())

def log_request(request, selected_tracts):
    global log_sequence_token
    log_stream = find_or_create_logstream()
    tracts = request['markers']
    changedTract = get_tract(float(request['changedMarker']['lat']), float(request['changedMarker']['lng']))
    log_message = request['operation'] + ', ' + str(changedTract) + ', ' + str(selected_tracts) 
    
    log_event_args = {
        'logGroupName':'LikelyHoods',
        'logStreamName':log_stream,
        'logEvents':[
            {
                'timestamp':int(time.time()*1000),
                'message':log_message
            },
        ],
    }

    if log_sequence_token:
        log_event_args['sequenceToken'] = log_sequence_token
    response = logging_client.put_log_events(**log_event_args)
    print(response)
    log_sequence_token=response['nextSequenceToken']
    
def find_or_create_logstream():
    global logging_week
    today = datetime.date.today()
    beginning_of_week = today - datetime.timedelta(today.weekday());
    if beginning_of_week != logging_week:
        logging_week = beginning_of_week
        logging_client.create_log_stream(logGroupName='LikelyHoods', logStreamName=logging_week.strftime('%m/%d/%Y'))
    return logging_week.strftime('%m/%d/%Y')

def create_mocked_response():
    info_list = []
    for i in range(0,5):
        tract_info = choice(list(tract_data_coords.values()))
        info_list.append({
            'tract' : {
                'tract_id': tract_info[0],
                'name': tract_info[4],
                'center_lat': tract_info[1],
                'center_lng': tract_info[2],
                'bounding_rect': tract_info[3].replace('(', '[').replace(')',']'),
                'img_src': tract_info[5],
                'education_rank': randint(0,300),
                'transportation_rank': randint(0,300),
                'wellness_rank': randint(0,300),
                'connectivity_rank': randint(0,300),
            }
        })
    return info_list

def create_response(candidates):
    info_list = []
    rank_dict = get_ranks(candidates)
    for candidate in candidates:
        info_list.append({
            'tract' : {
                'tract_id': candidate,
                'name': tract_data_coords[candidate][4],
                'center_lat': tract_data_coords[candidate][1],
                'center_lng': tract_data_coords[candidate][2],
                'bounding_rect': tract_data_coords[candidate][3].replace('(', '[').replace(')',']'),
                'img_src': tract_data_coords[candidate][5],
                'education_rank': int(rank_dict[str(candidate)][EDUCATION_INDEX]),
                'transportation_rank': int(rank_dict[str(candidate)][TRANSPORTATION_INDEX]),
                'wellness_rank': int(rank_dict[str(candidate)][WELLNESS_INDEX]),
                'connectivity_rank': int(rank_dict[str(candidate)][CONNECTIVITY_INDEX]),
            }
        })
    return info_list

def get_tract(lat, lng):
    xy_point = Point(lat,lng)
    for tract_id, bounds in tract_bounds.items():
        if bounds.contains(xy_point):
            return tract_id
    return None

def set_tract_data():
    hvc = pd.read_csv('tract_latlong_HVC/cuyahoga_tract_lat_long_hcv.csv')

    for index, row in hvc.iterrows():
        t = row['tract_id']
        tract_data_coords[t] = [row['tract_id'], row['center_latitude'], row['center_longitude'], row['polygon_coord'], row['name'], row['img_src']]

    cuyahoga_tract_data = pd.read_csv("tract_latlong_HVC/cuyahoga_tract_lat_long_hcv.csv")

    # If performance at startup becomes a concern, this should be reverted
    # to the original method of teasing apart the string.
    for index, row in cuyahoga_tract_data.iterrows():
        tract_bounds[row['tract_id']] = Polygon(eval(row['polygon_coord']))

if __name__ == "__main__":
    set_tract_data()
    app.run(
      host=os.getenv('LISTEN', '0.0.0.0'),
      port=int(os.getenv('PORT', '5000')),
    )
