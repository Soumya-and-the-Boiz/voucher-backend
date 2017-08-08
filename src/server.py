from itertools import islice
import pandas as pd
import os
import json

import datetime

import importlib
ranking_spec = importlib.util.find_spec('ranking')
has_ranking = ranking_spec is not None
if has_ranking:
    from ranking.predict_rank import *

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin


import logging
from logging.handlers import RotatingFileHandler

from shapely.geometry import Polygon
from shapely.geometry import Point

from random import randint, choice

tract_data_coords = {}
tract_bounds = {}

NUMBER_OF_RESULTS = 5

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

with open('src/config.json', 'r') as fp :
    config = json.load(fp)

CONNECTIVITY_INDEX = 0
EDUCATION_INDEX = 1
TRANSPORTATION_INDEX = 2
WELLNESS_INDEX = 3

@app.route('/', methods=['POST'])
@cross_origin()
def hello_world():
    if has_ranking:
        log_request(request.json)
        selected_tracts = [get_tract(float(item['lat']), float(item['lng'])) for item in request.json['markers']]
        selected_tracts = list(filter(None.__ne__, selected_tracts))
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

def log_request(request):
    tracts = request['markers']
    changedMarker = request['changedMarker']
    if request['operation'] == "add":
        print('Add request logged')
    elif request['operation'] == "remove":
        print('Remove request logged')
    else:
        print('Unknown request logged, expected add or remove')

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
    handler = RotatingFileHandler('backend.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    set_tract_data()
    app.run(
      host=os.getenv('LISTEN', '0.0.0.0'),
      port=int(os.getenv('PORT', '5000')),
    )
