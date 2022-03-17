import json
import random

from scraper import DUMMY_OPEN, DUMMY_CLOSE

FILE_NAME = 'restaurants.json'
CUISINES = [
    "American",
    "Chinese",
    "French",
    "Indian",
    "Italian",
    "Japanese",
    "Korean",
    "Mediterranean",
    "Mexican",
    "Thai",
    "Other"
]


def main():
    with open(FILE_NAME, "r") as file:
        restaurants = json.load(file)

    inserts = []
    i = 0
    for r in restaurants:
        insert = generate_sql_insert(r, i)

        if (insert is not None):
            inserts.append(insert)
            i += 1

    # write to file
    with open('restaurant_inserts.txt', 'w') as f:
        for item in inserts:
            f.write("%s" % item)

def generate_sql_insert(restaurant, override_id):
    if (not restaurant['name'].isascii()):
        return None

    output = "INSERT INTO Restaurant "
    cols = [
        "restaurantID",
        "address",
        "name",
        "phoneNumber",
        "cuisine",
        "openingTime",
        "closingTime"
    ]

    # convert times
    restaurant["opening"] = convert_time(restaurant["opening"]) if restaurant["opening"] is not None else convert_time(DUMMY_OPEN)
    restaurant["closing"] = convert_time(restaurant["closing"]) if restaurant["closing"] is not None else convert_time(DUMMY_CLOSE)

    # get cuisine
    cuisine = generate_cuisine(restaurant["name"])

    vals = [
        str(override_id),
        quote(restaurant["address"]),
        quote(restaurant["name"]),
        quote(restaurant["phone"]),
        quote(cuisine),
        quote(restaurant["opening"]),
        quote(restaurant["closing"]),
    ]

    output += " ({}) ".format(", ".join(cols))

    output += " VALUES ({});\n".format(", ".join(vals))

    return output

def generate_cuisine(name):
    cuisines = [x.lower() for x in CUISINES] 
    name =  name.lower()
    # check if restaurant name contains a valid cuisine
    for cuisine in cuisines:
        if (cuisine in name):
            print("Cuisine match! ", cuisine, " - ", name)
            return cuisine.capitalize()
    
    # else, randomly pick one
    return random.choice(CUISINES)

def convert_time(time):
    return "{}:{}".format(time[:2], time[2:])

def quote(str):
    return "\"{}\"".format(str)

if __name__ == "__main__":
    main()