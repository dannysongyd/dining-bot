import requests
import time
from decimal import Decimal
import json
import boto3


def load_restaurant(data):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('yelp-restaurants')
    count = 0
    with table.batch_writer() as batch:
        for restaruant in data:

            # print(restaruant['id'])
            # print(type(restaruant['id']))

            # business_id = restaruant['id'],
            # print(type(business_id))

            # name = restaruant['name'],
            # address = restaruant['address'][0]
            # coordinates = restaruant['coordinates']
            # reviews = restaruant['review_count']
            # zip_code = restaruant['zip_code']
            batch.put_item(
                Item=restaruant
            )
            count += 1
            print(count)

            # batch.put_item(
            #     Item={
            #         "business_id": {"S": restaruant['id']},
            #         "name": {"S": restaruant['name']},
            #         "address": {"S": restaruant['address'][0]},
            #         "coordinates": {"S": restaruant['coordinates']},
            #         "review_count": {"S": restaruant['review_count']},
            #         "zip_code": {"S": restaruant['zip_code']},
            #     }
            # )


with open("yelp-data/scraped_data.json") as json_file:
    restaurant_list = json.load(json_file, parse_float=Decimal)
load_restaurant(restaurant_list)
