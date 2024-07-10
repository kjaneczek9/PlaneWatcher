import json
import requests
import re
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class Plane:
    def __init__(self, plane, aircraft_cache):
        self.altitude = plane.get("altitude", 0)
        self.speed = plane.get("speed", 0)
        self.callsign = plane.get("flight", None)
        self.hex_code = plane.get("hex", None)
        self.latitude = plane.get("lat", None)
        # self.flying = self.is_flying()
        self.destination = self.get_dest(aircraft_cache)
        self.landing = self.is_landing()
        self.runway = self.get_runway()
        self.aircraft = self.get_aircraft_type(aircraft_cache)
        
    # def is_flying(self):
    #     return self.altitude > 0 and self.altitude < 1900 and self.speed > 0
    
    def valid_callsign(self):
        return any(self.callsign) and not self.callsign.startswith("N")

    def get_aircraft_type(self, aircraft_cache):
        if self.hex_code in aircraft_cache['aircrafts']:
            return aircraft_cache['aircrafts'][self.hex_code]
        res = requests.get(f"https://opensky-network.org/api/metadata/aircraft/icao/{self.hex_code}")
        if res.status_code == 200:
            data = res.json()
            model = data.get("model", "Unknown")
            aircraft_cache['aircrafts'][self.hex_code] = model
            return model
        else:
            return "Unknown"

    def is_landing(self):
        return self.destination and "Los Angeles" in self.destination

    def get_dest(self, aircraft_cache):
        if not self.callsign:
            return None
        
        if self.callsign in aircraft_cache['destinations'] and aircraft_cache['destinations'][self.callsign]:
            return aircraft_cache['destinations'][self.callsign]
        
        flight_number = self.callsign.upper().strip()
        url = f"https://www.radarbox.com/data/flights/{flight_number}"
        res = requests.get(url)
        if res.status_code == 200:
            match = re.search(r"to\s+([^\.,]+(?:, [A-Z]{2})?)", res.text)
            if match:
                destination = match.group(1)
                if 'on AirNav RadarBox"/>' in destination:
                    idx = destination.find('on AirNav RadarBox"/>')
                    destination = destination[:idx]
                    aircraft_cache['destinations'][self.callsign] = destination
                return destination
        return None

    def get_runway(self):
        if round(self.latitude, 2) == 33.93 or round(self.latitude, 2) == 33.94:
            return "Far"
        elif round(self.latitude, 2) == 33.95:
            return "Close"
        return None

def fetch_plane_data(obj, aircraft_cache):
    if obj['altitude'] != 0 and obj['altitude'] < 1900 and obj['speed'] > 0:
        plane = Plane(obj, aircraft_cache)
        if plane.landing is False:
            return datetime.now(), plane.__dict__
    return None

if __name__ == "__main__":
    aircraft_cache = {
        'aircrafts': {},
        'destinations': {},
    }
    os.system("clear")

    with ThreadPoolExecutor(max_workers=1) as executor:
        with open("aircraft_data.json", "r") as file:
            planes = json.load(file)
            file.close()
        futures = [executor.submit(fetch_plane_data, obj, aircraft_cache) for obj in planes["aircraft"]]
        for future in as_completed(futures):
            result = future.result()
            if result:
                print(result[1]['runway'].upper(), result[1]['callsign'].strip(), result[1]['aircraft'], result[1]['destination'])