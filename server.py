
import requests
import pandas as pd

from flask import Flask, request, jsonify
from flask.ext.cors import CORS, cross_origin

from shapely.geometry import Polygon
from shapely.geometry import Point

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

QUERY_TEMPLATE = 'http://data.fcc.gov/api/block/2010/find?format=json&latitude={}&longitude=}{}'

MOCKED_RESPONSE = [
    {'tract' : {
        'name': 'Tract 1',
        'bounding_rect': [(41.467714, -81.759736), (41.467195, -81.758724), (41.465218, -81.758711), (41.465238, -81.758649), (41.466693, -81.754202), (41.467728, -81.751035), (41.468388, -81.749038), (41.468464, -81.748835), (41.469226, -81.746722), (41.47009, -81.745592), (41.470056, -81.751034), (41.47046, -81.748568), (41.472142, -81.748559), (41.473252, -81.748558), (41.477114, -81.748543), (41.477103, -81.750968), (41.477066, -81.754133), (41.47043, -81.754186), (41.470107, -81.75286), (41.469819, -81.752498), (41.46878, -81.755502), (41.467997, -81.758053), (41.467714, -81.759736)],
        'img_src': 'https://s-media-cache-ak0.pinimg.com/736x/73/de/32/73de32f9e5a0db66ec7805bb7cb3f807.jpg',
        'education_rank': 42,
        'transportation_rank': 195,
        'wellness_rank': 220,
        'connectivity_rank': 421,
    }},
    {'tract' : {
        'name': 'Tract 2',
        'bounding_rect': [(41.498592, -81.556092), (41.497699, -81.556092), (41.497701, -81.551552), (41.497708, -81.549237), (41.497716, -81.545784), (41.495926, -81.545773), (41.495697, -81.544243), (41.49594, -81.541318), (41.495723, -81.538718), (41.495925, -81.536242), (41.497854, -81.536242), (41.499604, -81.53626), (41.499605, -81.540169), (41.501355, -81.540168), (41.501371, -81.546043), (41.503195, -81.546087), (41.503162, -81.555251), (41.503333, -81.555938), (41.501328, -81.556005), (41.498592, -81.556092)],
        'img_src': 'https://static.pexels.com/photos/106399/pexels-photo-106399.jpeg',
        'education_rank': 42,
        'transportation_rank': 195,
        'wellness_rank': 220,
        'connectivity_rank': 421,
    }},
    {'tract' : {
        'name': 'Tract 3',
        'bounding_rect': [(41.346946, -81.857614), (41.331086, -81.857681), (41.331352, -81.850858), (41.331742, -81.84913), (41.333786, -81.844576), (41.332507, -81.844632), (41.331653, -81.846302), (41.329942, -81.84661), (41.328216, -81.845999), (41.3286, -81.838912), (41.330081, -81.83838), (41.330185, -81.836868), (41.333052, -81.836431), (41.336273, -81.832519), (41.341461, -81.827994), (41.349565, -81.821299), (41.350719, -81.820826), (41.350615, -81.843766), (41.35075, -81.845657), (41.35045, -81.848557), (41.343826, -81.848611), (41.346946, -81.857614)],
        'img_src': 'https://cdn.houseplans.com/product/o2d2ui14afb1sov3cnslpummre/w560x373.jpg?v=15',
        'education_rank': 42,
        'transportation_rank': 195,
        'wellness_rank': 220,
        'connectivity_rank': 421,
    }},
    {'tract' : {
        'name': 'Tract 4',
        'bounding_rect': [(41.525383, -81.550013), (41.520512, -81.550014), (41.520657, -81.54572), (41.520691, -81.536455), (41.520922, -81.536497), (41.523288, -81.538431), (41.525368, -81.539402), (41.53116, -81.542106), (41.531803, -81.542758), (41.533568, -81.546297), (41.534302, -81.548568), (41.534791, -81.549742), (41.530167, -81.549628), (41.526927, -81.549565), (41.525383, -81.550013)],
        'img_src': 'https://www.epa.gov/sites/production/files/styles/large/public/2016-10/house_on.jpg',
        'education_rank': 42,
        'transportation_rank': 195,
        'wellness_rank': 220,
        'connectivity_rank': 421,
    }},
    {'tract' : {
        'name': 'Tract 5',
        'bounding_rect': [(41.434288, -81.618897), (41.430061, -81.615661), (41.425936, -81.612446), (41.425962, -81.611448), (41.428321, -81.611467), (41.427896, -81.605963), (41.425352, -81.604547), (41.423986, -81.604551), (41.423965, -81.602219), (41.424641, -81.598293), (41.426717, -81.598344), (41.430484, -81.600924), (41.431071, -81.600717), (41.433916, -81.606685), (41.436403, -81.610571), (41.439405, -81.615248), (41.436335, -81.615365), (41.434271, -81.615408), (41.434288, -81.618897)],
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
    print(request.json)
    return jsonify(MOCKED_RESPONSE)
    tracts = []
    for location in locations:
        tracts.append(get_tract(location['lat'], location['lng']))
    output = ''
    for tract in tracts:
        output += tract + '\n'
    return output



def get_tract(lat, long):
    xy_point = Point(lat,long)
    
    cuyahoga_tract_data = pd.read_csv("tract_latlong_HVC/cuyahoga_tract_lat_long_hcv.csv")
    #_ = cuyahoga_tract_data[['tract_id','center_latitude','center_longitude','polygon_coord']]

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
