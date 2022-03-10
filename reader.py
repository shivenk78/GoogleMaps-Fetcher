import json

from scraper import DUMMY_OPEN, DUMMY_CLOSE

FILE_NAME = 'restaurants.json'


def main():
    with open(FILE_NAME, "r") as file:
        restaurants = json.load(file)

    inserts = [generate_sql_insert(r) for r in restaurants]

    # write to file
    with open('restaurant_inserts.txt', 'w') as f:
        for item in inserts:
            f.write("%s" % item)

def generate_sql_insert(restaurant):
    if (not restaurant['name'].isascii()):
        return ""

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

    vals = [
        str(restaurant["id"]),
        quote(restaurant["address"]),
        quote(restaurant["name"]),
        quote(restaurant["phone"]),
        "NULL",
        quote(restaurant["opening"]),
        quote(restaurant["closing"]),
    ]

    output += " ({}) ".format(", ".join(cols))

    output += " VALUES ({});\n".format(", ".join(vals))

    return output

def convert_time(time):
    return "{}:{}".format(time[:2], time[2:])

def quote(str):
    return "\"{}\"".format(str)

if __name__ == "__main__":
    main()