import json
import requests
import re

def get_depts():
    
    res = requests.get("https://www.flightstats.com/v2/flight-tracker/departures/LAX/?year=2024&month=6&date=18&hour=18")
    shorter = res.text[res.text.index('__NEXT_DATA__'):]
    short = shorter[shorter.index('"flights":['):]
    shortest = short[:short.index(',"showCodeshares"')]
    
    json_string = '{' + shortest + '}'

    # Convert the JSON string to a Python dictionary
    data = json.loads(json_string)
    
    return data['flights']

def get_aircraft_type(hex_code):
    res = requests.get(f"https://opensky-network.org/api/metadata/aircraft/icao/{hex_code}")
    
    if res.status_code == 200:
        data = res.json()
        return data.get('model', 'Unknown')
    else:
        return 'Unknown'
    
def get_dest(flight_number):
    flight_number = flight_number.strip()
    url = f"https://www.radarbox.com/data/flights/{flight_number}"
    res = requests.get(url)
    match = re.search(r"Follow\s+Flight\s+(\w+)\s+from\s+([^\d,]+(?:,\s*[A-Z]{2})?)\s+to\s+([^\d,]+(?:,\s*[A-Z]{2})?)\s+on\s+AirNav\s+RadarBox", res.text)
    if match:
        match_idx = match.start()
        narrow_search = res.text[match_idx:]
        match = re.search(r"to\s+([^\.,]+(?:, [A-Z]{2})?)", narrow_search)
        destination = match.group(1)
        
        if 'on AirNav RadarBox"/>' in destination:
            words = destination.split(' ')
            destination = words[0]
        
        return destination
    else:
        print(f"{flight_number}: No destination found")
        return None


def get_flight_map(flights):
    flight_map = {}
    for flight in flights:
        carrier = flight.get('carrier')
        if carrier:
            flight_num = carrier['fs'] + carrier['flightNumber']
            airport = flight.get('airport')
            if airport:
                dest = airport['city']
                flight_map[flight_num] = dest
    
    return list(flight_map.keys())
        

if __name__ == "__main__":    
    printed = []
    while True:
        planes_file = "aircraft.json"
        with open(planes_file, 'r') as file:
            planes = json.load(file)
        
        for plane in planes['aircraft']:
            if 'altitude' in plane and plane['altitude'] != 'ground' and plane['altitude'] < 3000:
                if 'flight' in plane and not plane['flight'].startswith('N'):
                    found_plane = plane['flight']
                    if found_plane not in printed:
                        dest = get_dest(found_plane.upper())
                        aircraft = get_aircraft_type(plane.get('hex',None))
                        if dest and 'Los Angeles' in dest:
                            dest = "landing"
                            continue
                        if '777' in aircraft and dest != 'landing':
                            print("================== 777 ALERT =====================")
                        print(f"{found_plane}\t\t\t{aircraft}\t\t\t\t{dest}")
                        printed.append(found_plane)
                        
