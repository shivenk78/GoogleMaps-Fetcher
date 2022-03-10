import yaml
import json
import requests

MAPS_SEARCH_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
MAPS_DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json?'
MAPS_API_KEY = ''
CHAMPAIGN_LAT_LONG = (40.11027523993279, -88.23209762908547)
MAX_RADIUS = 50000
DUMMY_ADDRESS = '12345 E Green St, Champaign, IL 61820, USA'
DUMMY_PHONE = '(217) 555-5555'
DUMMY_OPEN = '0900'
DUMMY_CLOSE = '2000'

def main():
    global MAPS_API_KEY

    # read api key(s) from yaml file
    with open("keys.yaml", "r") as yaml_file:
        keys = yaml.safe_load(yaml_file)

    MAPS_API_KEY = keys["maps_key"]
    
    # Assuming 60 per, we need at least 1000/60 = 16.667, so we will use 20
    locations = [
        CHAMPAIGN_LAT_LONG,
        (41.922943681216594, -87.65324733070048), # Chicago (Bean)
        (40.809236223750915, -73.94535595359275), # Harlem
        (40.680901622794224, -73.96010556421795), # Brooklyn
        (40.73061171209389, -73.99066128946514), # Lower Manhattan

        (39.918834363049406, -75.22741140124606), # West Philly
        (39.98752404961361, -75.1600717586356), # East Philly
        (40.349971196634456, -74.6585924277154), # Princeton
        (35.229698244391884, -80.8376188584255), # Charlotte
        (37.553497042093966, -77.46648415804177), # Richmond

        (38.92044977160566, -77.03346060450622), # Washington DC
        (47.618474720259265, -122.33765860480277), # Seattle (SLU)
        (34.042007132792676, -118.27842659078642), # Los Angeles
        (32.70926199350865, -117.13059372867312), # San Diego
        (37.327826631789634, -121.8876473706432), # San Jose,

        (37.75174598161957, -122.44343087803827), # San Francisco
        (30.271518829019996, -97.7451697626526), # Austin
        (39.76914561684112, -86.16022313734244), # Indianapolis 
        (25.77187931429908, -80.2006214324026), # Miami
        (33.75547475658903, -84.38662173954627), # Atlanta
    ]

    all_restaurants = []
    for loc in locations:
        restaurants = get_restaurants(loc)
        print("Found {} restaurants in location {}".format(len(restaurants), loc))
        all_restaurants += restaurants

    i = 0
    for restaurant in all_restaurants:
        restaurant['id'] = i
        i += 1

    print("Total {} restaurants. Writing to JSON file".format(len(restaurants)))
    with open("restaurants.json", "w") as out_file:
        json.dump(all_restaurants, out_file)

def get_restaurants(coords):
    restaurants = []
    places, next_page = get_places(coords=coords, type='restaurant')
    parse_places(restaurants, places)

    while (next_page is not None):
        places, next_page = get_next_places_page(next_page)
        parse_places(restaurants, places)
    
    return restaurants


def get_next_places_page(page_token):
    query = {
        'pagetoken': page_token,
        'key': MAPS_API_KEY
    }

    response = requests.get(MAPS_SEARCH_URL, headers={}, params=query)
    print("Attepted NEW PAGE request, response code {}".format(response.status_code))

    places = response.json()['results']
    next_page = response.json()['next_page_token'] if 'next_page_token' in response.json() else None
    print("Received {} restaurants from NEW PAGE Google Maps API".format(len(places)))
    return places, next_page

def get_places(coords, type):
    # search requires location 'lat,long' and type
    loc_string = "{},{}".format(coords[0], coords[1])
    query = {
        'location': loc_string,
        'type': type,
        'radius': MAX_RADIUS,
        'key': MAPS_API_KEY
    }

    # perform request
    response = requests.get(MAPS_SEARCH_URL, headers={}, params=query)
    print("Attepted request, response code {}".format(response.status_code))

    places = response.json()['results']
    next_page = response.json()['next_page_token'] if 'next_page_token' in response.json() else None

    print("Received {} restaurants from Google Maps API".format(len(places)))
    return places, next_page

def parse_places(restaurants, places):
    # need a ID, address, name, phone, cuisine?, opening, closing
    if (len(places) == 0):
        return

    for place in places:
        #print(place)
        name = place['name']
        place_id = place['place_id']

        details = get_details(place_id)

        dict = {
            'address': details['address'],
            'name': name,
            'phone': details['phone'],
            'opening': details['opening'],
            'closing': details['closing']
        }

        #print(dict)
        restaurants.append(dict)

def get_details(place_id):
    query = {
        'place_id': place_id,
        'fields': 'formatted_address,formatted_phone_number,opening_hours',
        'key': MAPS_API_KEY
    }

    response = requests.get(MAPS_DETAILS_URL, headers={}, params=query)
    details = response.json()['result']

    dict = {}
    dict['address'] = details['formatted_address'] if 'formatted_address' in details else DUMMY_ADDRESS
    dict['phone'] = details['formatted_phone_number'] if 'formatted_phone_number' in details else DUMMY_PHONE
    opening, closing = get_opening_closing(details['opening_hours']) if 'opening_hours' in details else (DUMMY_OPEN, DUMMY_CLOSE)
    dict['opening'] = opening
    dict['closing'] = closing

    return dict

# get a set of opening and closing times ON MONDAY
def get_opening_closing(hours):
    periods = hours['periods']
    opening = None
    try:
        opening = periods[1]['open']['time']
        closing = periods[1]['close']['time']
    except Exception as e:
        opening = DUMMY_OPEN if opening is not None else opening
        closing = DUMMY_CLOSE

    return (opening, closing)

if __name__ == '__main__':
    main()