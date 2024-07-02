from flask import Flask, jsonify, request
import json
from read_planes import Plane

AIRCRAFT_CACHE = {
        'aircrafts': {},
        'destinations': {},
    }
app = Flask(__name__)

@app.route('/')
def home():
    return "hot girls use flask"

@app.route('/api/all_planes', methods=['GET'])
def read_dump1090_output():
    with open("aircraft_data.json", "r") as file:
        planes = json.load(file)
        file.close()
    return planes

@app.route('/api/get_flying_planes', methods=['GET'])
def get_flying_planes():
    planes = read_dump1090_output()
    flying_planes = []
    for obj in planes['aircraft']:
        if obj['altitude'] != 0 and obj['altitude'] < 1900 and obj['speed'] > 0:
            flying_planes.append(obj)
    return flying_planes
            

@app.route('/api/sort_planes', methods=['GET'])
def sorted_planes():
    planes = get_flying_planes()
    plane_objs = []
    for obj in planes:
        plane_objs.append(Plane(obj, AIRCRAFT_CACHE).__dict__)
    return plane_objs

@app.route('/api/get_far_runway', methods=['GET'])
def far_runway_planes():
    planes = sorted_planes()
    far_runway = []
    for plane in planes:
        if plane['runway'] == 'Far':
            far_runway.append(plane)
    return far_runway        

@app.route('/api/get_close_runway', methods=['GET'])
def close_runway_planes():
    planes = sorted_planes()
    far_runway = []
    for plane in planes:
        if plane['runway'] == 'Close':
            far_runway.append(plane)
    return far_runway   



if __name__ == '__main__':
    app.run(debug=True)
