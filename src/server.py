from itertools import islice
import pandas as pd
import os

import importlib
ranking_spec = importlib.util.find_spec('ranking')
has_ranking = ranking_spec is not None
if has_ranking:
    from ranking.predict_rank import *

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from shapely.geometry import Polygon
from shapely.geometry import Point

from random import randint, choice

tract_data_coords = {}
tract_bounds = {}

NUMBER_OF_RESULTS = 5

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

CITIES = ['Miltona', 'Attu Station', 'Blytheville', 'Drumright', 'Broadwater', 'Nevis', 'Alsace Manor', 'Wedowee', 'Inglis', 'Homedale', 'Lakeshore Gardens', 'Rushmere', 'West Winfield', 'Adelino', 'Farmers Loop', 'Windy Hills', 'Hebgen Lake Estates', 'Villanueva', 'Falkner', 'White Marsh', 'Ishpeming', 'Breinigsville', 'Sharonville', 'Hytop', 'Learned', 'Redington Beach', 'Adamsburg', 'Gumbranch', 'Bolindale', 'Ludlow', 'South Russell', 'Shingle Springs', 'Tariffville', 'Windsor', 'Maxville', 'Keyport', 'Fairplay', 'Westfield Center', 'Estes Park', 'Kimball', 'North East', 'Ketchum', 'New Melle', 'North Tunica', 'Madawaska', 'Hallam', 'Poplar Bluff', 'Madeira Beach', 'Shadow Lake', 'Plandome Heights']

PICTURES = [
'http://media.cleveland.com/cleveland-heights/photo/lee-road-library-2jpg-a9f3050b56d92eb2.jpg',
'http://www.coventryvillage.org/wordpress/wp-content/uploads/2010/12/streetsm.jpg',
'http://d3qp2gvi46z69k.cloudfront.net/wp-content/uploads/2013/03/NeighborhoodRECON.jpg',
'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Shaker_Heights_Public_Library.jpg/315px-Shaker_Heights_Public_Library.jpg',
'http://blog.dentalplans.com/wp-content/uploads/2016/05/343829-neighborhood-1024x683.jpg',
'http://www.howardhanna.com/ClientImage/Office-Full/0028.jpg',
'http://www.seechicagorealestate.com/uploads/agent-1/Chicago-Neighborhoods.jpg',
'http://0.tqn.com/d/cleveland/1/S/3/d/-/-/collinwood2-spivack.jpg',
'http://image.cleveland.com/home/cleve-media/width960/img/plain-dealer/photo/2016/07/15/-63b196e7e586620f.jpg',
'http://www.pittsburghcityliving.com/img/heroes/203J4387-%20Lawrenceville%20streetscape.jpg',
'http://snipesproperties.com/wp-content/uploads/2014/03/church-hill.jpg',
'http://www.dreamtown.com/photos/tiles/neighborhoods/IrvingPark.jpg',
'https://s3.amazonaws.com/citybuzz/2015/11/ukrainian-village-chicago-neighborhood/ukrainian-village-1.jpg',
'https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/SD_Houses_2.jpg/300px-SD_Houses_2.jpg',
'https://upload.wikimedia.org/wikipedia/en/c/c3/UD_Ghetto_Irving.jpg',
'http://livability.com/sites/default/files/7730312BM7935_1.jpg',
]

CONNECTIVITY_INDEX = 0
EDUCATION_INDEX = 1
TRANSPORTATION_INDEX = 2
WELLNESS_INDEX = 3

@app.route('/', methods=['POST'])
@cross_origin()
def hello_world():
    if has_ranking:
        selected_tracts = [get_tract(float(item['lat']), float(item['lng'])) for item in request.json]
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
      port=int(os.getenv('PORT', '5000'))
    )
