
import requests
import pandas as pd

from flask import Flask, request, jsonify
from flask.ext.cors import CORS, cross_origin

from shapely.geometry import Polygon
from shapely.geometry import Point

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

MOCKED_RESPONSE = [
    {'tract' : {
        'name': 'Tract 1',
        'center_lat': '41.471166',
        'center_lng': '-81.75266400000001',
        'bounding_rect': [(41.467714, -81.759736), (41.467195, -81.758724), (41.465218, -81.758711), (41.465238, -81.758649), (41.466693, -81.754202), (41.467728, -81.751035), (41.468388, -81.749038), (41.468464, -81.748835), (41.469226, -81.746722), (41.47009, -81.745592), (41.470056, -81.751034), (41.47046, -81.748568), (41.472142, -81.748559), (41.473252, -81.748558), (41.477114, -81.748543), (41.477103, -81.750968), (41.477066, -81.754133), (41.47043, -81.754186), (41.470107, -81.75286), (41.469819, -81.752498), (41.46878, -81.755502), (41.467997, -81.758053), (41.467714, -81.759736)],
        'img_src': 'https://s-media-cache-ak0.pinimg.com/736x/73/de/32/73de32f9e5a0db66ec7805bb7cb3f807.jpg',
        'education_rank': 42,
        'transportation_rank': 195,
        'wellness_rank': 220,
        'connectivity_rank': 421,
    }},
    {'tract' : {
        'name': 'Tract 2',
        'center_lat': '41.3942805',
        'center_lng': '-81.75430349999999',
        'bounding_rect': [(41.388627, -81.763984), (41.385643, -81.760703), (41.384553, -81.760121), (41.384555, -81.75321), (41.384538, -81.746945), (41.384539, -81.744623), (41.392282, -81.744752), (41.394875, -81.745398), (41.398667, -81.745232), (41.404023, -81.745311), (41.397556, -81.75322), (41.393845, -81.757743), (41.392793, -81.758933), (41.388627, -81.763984)],
        'img_src': 'https://static.pexels.com/photos/106399/pexels-photo-106399.jpeg',
        'education_rank': 42,
        'transportation_rank': 195,
        'wellness_rank': 220,
        'connectivity_rank': 421,
    }},
    {'tract' : {
        'name': 'Tract 3',
        'center_lat': '41.4674265',
        'center_lng': '-81.72753',
        'bounding_rect': [(41.463547, -81.738387), (41.462525, -81.738583), (41.46235, -81.738117), (41.461029, -81.734553), (41.459574, -81.731669), (41.462313, -81.730159), (41.462335, -81.728826), (41.462359, -81.727675), (41.462364, -81.725932), (41.462366, -81.724923), (41.462387, -81.72234), (41.462396, -81.721186), (41.462406, -81.720316), (41.462406, -81.720049), (41.464118, -81.720021), (41.467263, -81.720009), (41.467519, -81.720009), (41.46965, -81.720001), (41.469655, -81.718288), (41.469664, -81.716494), (41.475279, -81.716477), (41.475036, -81.722268), (41.472412, -81.730145), (41.471883, -81.731751), (41.470999, -81.735739), (41.469581, -81.736237), (41.464627, -81.738021), (41.463547, -81.738387)],
        'img_src': 'https://cdn.houseplans.com/product/o2d2ui14afb1sov3cnslpummre/w560x373.jpg?v=15',
        'education_rank': 42,
        'transportation_rank': 195,
        'wellness_rank': 220,
        'connectivity_rank': 421,
    }},
    {'tract' : {
        'name': 'Tract 4',
        'center_lat': '41.5581235',
        'center_lng': '-81.525047',
        'bounding_rect': [(41.568986, -81.535167), (41.567278, -81.537014), (41.56306, -81.531238), (41.561502, -81.530226), (41.560203, -81.533286), (41.558051, -81.534763), (41.554959, -81.53187), (41.55217, -81.531082), (41.551049, -81.528977), (41.54954, -81.529278), (41.546706, -81.527254), (41.557973, -81.527607), (41.5601, -81.527957), (41.560051, -81.51308), (41.562595, -81.513123), (41.564155, -81.515015), (41.565418, -81.514524), (41.565934, -81.514107), (41.568122, -81.514157), (41.567647, -81.515276), (41.56731, -81.522404), (41.567541, -81.526384), (41.568801, -81.533071), (41.569541, -81.533754), (41.568986, -81.535167)],
        'img_src': 'https://www.epa.gov/sites/production/files/styles/large/public/2016-10/house_on.jpg',
        'education_rank': 42,
        'transportation_rank': 195,
        'wellness_rank': 220,
        'connectivity_rank': 421,
    }},
    {'tract' : {
        'name': 'Tract 5',
        'center_lat': '41.430186500000005',
        'center_lng': '-81.9423575',
        'bounding_rect': [(41.412017, -81.962253), (41.411047, -81.962464), (41.411047, -81.959963), (41.413747, -81.959663), (41.413746, -81.946265), (41.418545, -81.945772), (41.418644, -81.942675), (41.426242, -81.942786), (41.426333, -81.940909), (41.426533, -81.939027), (41.428869, -81.935968), (41.428969, -81.932928), (41.430649, -81.932734), (41.43409, -81.932598), (41.433946, -81.92276), (41.439678, -81.922546), (41.449326, -81.922251), (41.446892, -81.928762), (41.445626, -81.930717), (41.443356, -81.933713), (41.440287, -81.936656), (41.437993, -81.938757), (41.432612, -81.94369), (41.427126, -81.950021), (41.424516, -81.955868), (41.42268, -81.961831), (41.412017, -81.962253)],
        'img_src': 'http://appropriations.house.gov/uploadedphotos/highresolution/bac5a9ce-7a70-49bb-9eef-adc8ae3c4873.jpg',
        'education_rank': 42,
        'transportation_rank': 195,
        'wellness_rank': 220,
        'connectivity_rank': 421,
    }}
]


@app.route('/', methods=['POST'])
@cross_origin()
def hello_world():
    tracts = []
    for item in request.json:
        tracts.append(get_tract(float(item['lat']), float(item['lng'])))
    print(tracts)
    return jsonify(MOCKED_RESPONSE)



def get_tract(lat, lng):
    xy_point = Point(lat,lng)

    cuyahoga_tract_data = pd.read_csv("tract_latlong_HVC/cuyahoga_tract_lat_long_hcv.csv")

    for index, row in cuyahoga_tract_data.iterrows():
        _ = row['polygon_coord'][1:-1]
        l_str = _.replace('(','').replace(' ','')
        _latlong = l_str.split('),')
        ll  = []
        for pair in _latlong:
            pair = pair.replace(')', '')
            separator = pair.find(',')
            ll.append((float(pair[:separator]), float(pair[separator+1:])))

        polygon = Polygon(ll)
        if polygon.contains(xy_point):
            return row['tract_id']

    return None

if __name__ == "__main__":
    app.run()
