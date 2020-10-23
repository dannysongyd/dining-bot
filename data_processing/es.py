from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import json

# Geting dynamdb data
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('yelp-restaurants')
items = table.scan()['Items']

print(len(items))
# # Cerating es connection
host = 'search-yelp-es-o6ndu6nw7m3cm2fxf7ngwu2uq4.us-east-1.es.amazonaws.com'
region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key,
                   credentials.secret_key,
                   region, service,
                   session_token=credentials.token)

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# for item in items:
#     doc = {
#         'business_id': item['business_id'],
#         'cuisine': item['cuisine']
#     }
#     es.index(index='restaurants', doc_type='Restaurant',
#              id=doc['business_id'], body=doc)

# print(json.dumps(es.info(), indent=4, sort_keys=True))

print(es.info)
