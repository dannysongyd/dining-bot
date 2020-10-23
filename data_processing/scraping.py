import requests
import time
import json
API_KEY = 'dGcLfqVy0iBcr8CWkMMOK1N-dZscLeeq9tofxW23pYcZBrTDZPOjdBiHNHhhnwO9KePQtzqPfsDaU4QeLOFSt7baoLT_wpVRSqjrOb56-tA6FsU2MqxGD8c4r6yDX3Yx'
LOCATION = 'Manhattan'
LIMIT = 50
CUISINES = ["Chinese", "Japanese", "Indian",  "Mexican", "American", "Italian"]


def get_restaurant(location, limit, offset, cuisine):
    global count
    global restaurants_list
    global id_set
    API_URL = "https://api.yelp.com/v3/businesses/search"

    API_HEADERS = {
        'Authorization': 'Bearer %s' % API_KEY
    }
    API_PARAMS = {
        'term': cuisine,
        'location': location,
        'limit': limit,
        'offset': offset
    }

    response = requests.get(
        url=API_URL, params=API_PARAMS, headers=API_HEADERS)

    data = response.json()

    for restaurant in data["businesses"]:
        if(restaurant["id"] not in id_set):
            temp = dict()
            temp["business_id"] = restaurant["id"]
            id_set.add(temp["business_id"])
            temp["name"] = restaurant["name"]
            temp["review_count"] = restaurant["review_count"]
            temp["rating"] = restaurant["rating"]
            temp["coordinates"] = restaurant["coordinates"]
            temp["address"] = restaurant["location"]["address1"]
            temp["zip_code"] = restaurant["location"]["zip_code"]
            temp["cuisine"] = cuisine

            restaurants_list.append(temp)
            count += 1


restaurants_list = []
id_set = set()
count = 0
for cuisine in CUISINES:

    print(cuisine)
    OFFSET = 0
    while OFFSET < 1000:
        print("\n Round : ", OFFSET)
        get_restaurant(LOCATION, LIMIT, OFFSET, cuisine)
        OFFSET += 50
        time.sleep(0.5)


print(count)
with open('scraped_data2.json', 'w') as fp:
    json.dump(restaurants_list, fp, indent=2)
