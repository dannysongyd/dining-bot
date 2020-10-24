import boto3
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from botocore.exceptions import ClientError


def get_info_from_sqs():
    # Create SQS client
    sqs = boto3.client('sqs')

    queue_url = 'https://sqs.us-east-1.amazonaws.com/715339036598/ChatbotQueue'

    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )

    if('Messages' in response):
        message = response['Messages'][0]

        # Delete After recieved
        receipt_handle = message['ReceiptHandle']
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

        cuisine = message['MessageAttributes']['Cuisine']['StringValue']
        date = message['MessageAttributes']['Date']['StringValue']
        dtime = message['MessageAttributes']['Time']['StringValue']

        location = message['MessageAttributes']['Location']['StringValue']
        people = message['MessageAttributes']['People']['StringValue']
        phone = message['MessageAttributes']['Phone']['StringValue']
        print(cuisine)
        info_dict = {
            'cuisine': cuisine,
            'date': date,
            'dtime': dtime,
            'location': location,
            'people': people,
            'phone': phone
        }

        return info_dict
    else:
        return None
    return None


def get_business_id_from_es(info_dict):
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

    # Randomly return 3 ids
    body = {
        "size": 3,
        "query": {
            "function_score": {
                "query": {"match": {"cuisine": info_dict['cuisine']}},
                "boost": "5",
                "random_score": {},
                "boost_mode": "multiply"
            }
        }
    }

    result = es.search(body)['hits']['hits']

    business_id_list = []
    for i in range(len(result)):
        business_id_list.append(result[i]['_id'])
    # business_id = es.search(body)['hits']['hits'][0]['_id']

    return business_id_list


def get_business_name_and_address(ids):
    # Geting dynamdb data
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('yelp-restaurants')
    # items = table.get_item

    # For every business_id got from es
    business_list = []
    for i in range(len(ids)):
        address = table.get_item(Key={'business_id': ids[i]})[
            'Item']['address']
        name = table.get_item(Key={'business_id': ids[i]})['Item']['name']
        business = (name, address)
        business_list.append(business)
    return business_list


def build_message(info_dict, business_list):
    cuisine = info_dict['cuisine']
    people = info_dict['people']
    date = info_dict['date']
    dtime = info_dict['dtime']

    greatting_str = 'Hello! Here are my ' + cuisine + \
        ' restaurants suggestions for ' + people + \
        ' people, on ' + date + ' at ' + dtime

    restaurants_list_str = ''
    for i in range(len(business_list)):
        restaurants_list_str += '{}. '.format(
            i+1) + business_list[i][0] + ', located at ' + business_list[i][1] + '\n'

    finish_str = 'Enjoy your meal!'

    message = greatting_str + '\n' + restaurants_list_str + finish_str
    return message


def send_ses(message, info_dict):
    SENDER = "ys4242@nyu.edu"
    RECIPIENT = info_dict['phone']
    AWS_REGION = "us-east-1"
    SUBJECT = "Your Restaurants Recommendation"
    CHARSET = "UTF-8"
    client = boto3.client('ses', region_name=AWS_REGION)

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': message,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER
        )

    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def lambda_handler(event, context):
    # TODO implement

    info_dict = get_info_from_sqs()
    if info_dict is not None:

        ids = get_business_id_from_es(info_dict)
        business_list = get_business_name_and_address(ids)
        message = build_message(info_dict, business_list)
        # send_ses(message, info_dict)
        send_sms(message, info_dict)
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps('No new message now')
        }


def send_sms(message, info_dict):
    phone = info_dict['phone']
    sns = boto3.client('sns', region_name='us-east-1')
    sns.publish(PhoneNumber=phone, Message=message)
