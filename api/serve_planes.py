import json
import re
from functools import lru_cache

from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import logging
import time
import threading

from Plane import Plane
from Sky import Sky

import constants 

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

logging.basicConfig(level=logging.INFO)  # Adjust the level as needed
logger = logging.getLogger(__name__)

CORS(app)

@app.route("/")
def home():
    return read_dump1090_output()

@app.route("/api/all_planes", methods=["GET"])
def read_dump1090_output():
    """
    Raw dump1090 output.
    """
    with open("data/aircraft_data.json", "r") as file:
        planes = json.load(file)
        file.close()
    
    parsed_planes = []
    for obj in planes["aircraft"]:
        # Quick skips where we can get them.
        if obj["speed"] <= 5 or obj["lat"] == 0 or obj["lon"] == 0 or obj["lon"] >= -118.398:
            continue
        parsed_planes.append(obj)
    
    return parsed_planes

def get_filtered_planes():
    """
    Sorts through and filters 1090 output into what should be shown.
    """
    planes = read_dump1090_output()
    
    for obj in planes:
        sky.process_plane(Plane(obj))
    
    return sky.planes_to_show


@app.route("/api/plane_tracker", methods = ["GET"])
def plane_tracker():
    """
    Serves HTML/Client.
    """
    planes_to_show = get_filtered_planes()
    sort_dict = {"PLANES":[]}
    
    for plane in planes_to_show:
        sort_dict["PLANES"].append(plane.__dict__)
    
    return sort_dict

def background_thread():
    while True:
        data = plane_tracker()
        socketio.emit('update', data)
        socketio.sleep(0.1)

@socketio.on('connect')
def handle_connect():
    print("Client connected")


if __name__ == "__main__":
    sky = Sky()
    thread = threading.Thread(target=background_thread)
    thread.daemon = True
    thread.start()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)