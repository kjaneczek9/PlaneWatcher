import json
import re
from functools import lru_cache

import requests
from flask import Flask, jsonify, request
from flask_caching import Cache

app = Flask(__name__)

# Configure cache
app.config["CACHE_TYPE"] = (
    "SimpleCache"  # Use 'RedisCache' for Redis or other supported types
)
app.config["CACHE_DEFAULT_TIMEOUT"] = 60  # Cache timeout in seconds

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
    flight_number = callsign.upper().strip()
    url = f"https://www.radarbox.com/data/flights/{flight_number}"
    res = requests.get(url)
    if res.status_code == 200:
        match = re.search(r"to\s+([^\.,]+(?:, [A-Z]{2})?)", res.text)
        if match:
            destination = match.group(1)
            if 'on AirNav RadarBox"/>' in destination:
                idx = destination.find('on AirNav RadarBox"/>')
                destination = destination[:idx]
            return destination
    return None


def get_runway(latitude):
    if round(latitude, 2) == 33.93 or round(latitude, 2) == 33.94:
        return "Far"
    elif round(latitude, 2) == 33.95:
        return "Close"
    return None


def is_landing(destination):
    return destination and "Los Angeles" in destination


@app.route("/api/all_planes", methods=["GET"])
def read_dump1090_output():
    with open("aircraft_data.json", "r") as file:
        planes = json.load(file)
        file.close()
    return planes


@app.route("/api/get_flying_planes", methods=["GET"])
def get_flying_planes():
    planes = read_dump1090_output()
    flying_planes = []
    for obj in planes["aircraft"]:
        if obj["altitude"] != 0 and obj["altitude"] < 1900 and obj["speed"] > 0:
            flying_planes.append(obj)
    return flying_planes


@app.route("/api/sort_planes", methods=["GET"])
def sort_planes():
    planes = get_flying_planes()
    plane_objs = []
    for obj in planes:
        obj["destination"] = get_destination(obj["flight"])
        obj["runway"] = get_runway(obj["lat"])
        obj["aircraft"] = get_aircraft(obj["hex"])
        obj["landing"] = is_landing(obj["destination"])
        plane_objs.append(obj)
    return plane_objs


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
    app.run(debug=True)
