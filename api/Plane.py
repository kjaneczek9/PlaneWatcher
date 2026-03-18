import json
import requests
import re

import constants

SAFE_TO_SHOW_PERSISTENCE = 3
STATIC_PERSISTENCE = 30

class Plane:
    def __init__(self, flight_data):
        self.hex_code = flight_data.get("hex")
        self.flight_number = flight_data.get("flight")
        self.lat = flight_data.get("lat")
        self.lon = flight_data.get("lon")
        self.altitude = flight_data.get("altitude")
        self.last_seen = flight_data.get("seen")
        self.destination = None
        self.flight_time = None
        self.landing = False
        self.taking_off = False
        self.speed = flight_data.get("speed")
        self.show_persistence = 0
        self.static_persistence = 0

        # Since these params query a 3rd party API, only fetch them when we need to show it.
        self.aircraft = None
        self.airline = None

    def get_aircraft(self):
        # First, check if we already found this hex code
        # with open("instance_state/inst_seen_planes.json", "r") as file:
        #     seen_planes = json.load(file)
        #     file.close()

        hex_code = self.hex_code.upper()

        # if hex_code in seen_planes:
        #     return seen_planes[hex_code]
        # else:
        try:
            res = requests.get(
                f"https://opensky-network.org/api/metadata/aircraft/icao/{hex_code}",
                timeout=1
            )
        except requests.exceptions.Timeout:
            return "null"

        if res.status_code == 200:
            data = res.json()
            model = data.get("model")
            # seen_planes[hex_code] = model
            # with open("instance_state/inst_seen_planes.json", "w") as f:
            #     json.dump(seen_planes, f, indent=4)
            return model
        return "null"

    def get_airline_code(self):
        callsign = self.flight_number
        if len(callsign.strip()) == 0:
            return None

        # split callsign by number
        letters = re.findall(r"[A-Za-z]+", callsign)[0].upper()

        # Check known airline codes first - to avoid overloading this API.
        with open("known_airlines.json", "r") as file:
            airlines = json.load(file)
            file.close()

        if letters in airlines:
            return airlines[letters]

        # Check local container instance.
        with open("instance_state/inst_known_airlines.json", "r") as f:
            data = json.load(f)
            file.close()

        if letters in data:
            return data[letters]

        # Otherwise query, but add to instance known to avoid again.
        else:
            res = requests.get(f"https://www.flightstats.com/v2/api-next/search/airline-airport?query={letters}&type=airline").json()
            if res["data"]:
                airline = res["data"][0]['fs']
                data[letters] = airline
            else:
                data[letters] = "404"
                airline = None

            with open("instance_state/inst_known_airlines.json", "w") as f:
                json.dump(data, f, indent=4)

            return airline

    def safe_to_show(self):
        # An plane is safe to show if it meets our filter for an amount of
        # data points.
        return self.show_persistence > SAFE_TO_SHOW_PERSISTENCE

    def matches_filter(self):
        return self.taking_off and self.altitude < 1750

    def update(self, updated_plane):
        # First, find out if we are ascending or descending.
        prev_alt = self.altitude
        new_alt = updated_plane.altitude

        # Update ourselves based on this new info!
        if prev_alt < new_alt:
            self.taking_off = True
            self.landing = False
        elif prev_alt > new_alt:
            self.landing = True
            self.taking_off = False

        # Sometimes a ground measures once and then never increases again.
        # We need a way to clear this.
        if prev_alt == new_alt:
            self.static_persistence += 1
        else:
            self.static_persistence = 0

        if self.static_persistence > STATIC_PERSISTENCE:
            self.show_persistence = 0
            self.taking_off = False
            self.landing = False

        # Update if we are matching filter
        if self.matches_filter():
            self.show_persistence += 1
        else:
            self.show_persistence = 0

        # Update all changed params.
        self.altitude = new_alt
        self.speed = updated_plane.speed
        self.lat = updated_plane.lat
        self.lon = updated_plane.lon

        # Sometimes flight # takes a minute to come up
        if not self.flight_number:
            self.flight_number = updated_plane.flight_number

    def prepare_to_show(self):
        # Does a final query for a plane once its ready to be shown.
        if self.safe_to_show and not self.aircraft:
            self.aircraft = self.get_aircraft()
            # self.airline = self.get_airline_code()
