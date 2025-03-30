import json
import re
from functools import lru_cache

import requests
from flask import Flask, jsonify, request
from flask_caching import Cache
from flask_cors import CORS
import logging


import constants 

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)  # Adjust the level as needed
logger = logging.getLogger(__name__)

# Configure cache
app.config["CACHE_TYPE"] = (
    "SimpleCache"  # Use 'RedisCache' for Redis or other supported types
)
app.config["CACHE_DEFAULT_TIMEOUT"] = 60  # Cache timeout in seconds
CORS(app)
cache = Cache(app)


@app.route("/")
def home():
    return "hot girls use flask"


@app.route("/api/get_aircraft/<hex_code>", methods=["GET"])
@lru_cache(maxsize=128)
def get_aircraft(hex_code):
    res = requests.get(
        f"https://opensky-network.org/api/metadata/aircraft/icao/{hex_code}"
    )
    if res.status_code == 200:
        data = res.json()
        model = data.get("model")
        return model
    return None


@app.route("/api/get_destination/<callsign>", methods=["GET"])
@lru_cache(maxsize=128)
def get_destination(callsign):
    if len(callsign) > 0:
        flight_number = callsign.upper().strip()
        url = f"https://www.radarbox.com/data/flights/{flight_number}"
        res = requests.get(url)
        if res.status_code == 200:
            match = re.search(constants.AIRNAV_RADARBOX_DESTINATION_REGEX, res.text)
            if match:
                destination = match.group(1)
                if constants.AIRNAV_RADARBOX_INTERNATIONAL_COND in destination:
                    idx = destination.find(constants.AIRNAV_RADARBOX_INTERNATIONAL_COND)
                    destination = destination[:idx]
                if ' on AirNav Radar"/>' in destination:
                    destination = destination.split(' on AirNav Radar"/>')[0]
                return destination
    return None


def get_runway(latitude):
    if round(latitude, 2) in constants.FAR_LATITUDE:
        return "Far"
    elif round(latitude, 2) == constants.CLOSE_LATITUDE:   
        return "Close"
    return None


def is_landing(destination):
    return destination and "Los Angeles" in destination


@app.route("/api/all_planes", methods=["GET"])
def read_dump1090_output():
    with open("data/aircraft_data.json", "r") as file:
        planes = json.load(file)
        file.close()
    return planes


@app.route("/api/get_flying_planes", methods=["GET"])
def get_flying_planes():
    planes = read_dump1090_output()
    flying_planes = []
    for obj in planes["aircraft"]:
        if obj["altitude"] != 0 and obj["altitude"] < 2100 and obj["speed"] > 0:
            flying_planes.append(obj)
    return flying_planes


@app.route("/api/gather_planes", methods=["GET"])
def gather_planes():
    planes = get_flying_planes()
    plane_objs = []
    for obj in planes:
        obj["destination"] = get_destination(obj["flight"])
        obj["runway"] = get_runway(obj["lat"])
        obj["aircraft"] = get_aircraft(obj["hex"])
        obj["landing"] = is_landing(obj["destination"])
        plane_objs.append(obj)
    return plane_objs

@app.route("/api/plane_tracker", methods = ["GET"])
def plane_tracker():
    planes = gather_planes()
    sort_dict = {"CLOSE":[], "FAR":[]}
    for plane in planes:
        if not plane['landing'] and plane['landing'] != None:
            if plane['runway'] == "Far":
                sort_dict["FAR"].append(plane)
            elif plane['runway'] == "Close":
                sort_dict["CLOSE"].append(plane)
    return sort_dict


@app.route("/api/get_far_runway", methods=["GET"])
def far_runway_planes():
    planes = sorted_planes()
    far_runway = []
    for plane in planes:
        if plane["runway"] == "Far":
            far_runway.append(plane)
    return far_runway


@app.route("/api/get_close_runway", methods=["GET"])
def close_runway_planes():
    planes = sorted_planes()
    far_runway = []
    for plane in planes:
        if plane["runway"] == "Close":
            far_runway.append(plane)
    return far_runway


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
