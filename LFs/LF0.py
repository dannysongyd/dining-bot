import json
import time
import os
import boto3


def get_request(event):
    messages = event["messages"]
    message = messages[0]
    text = message["unstructured"]["text"]
    return text


def build_response(text):
    user_id = 'ys4242'
    body = {
        "messages": [
            {
                "type": "unstructured",
                "unstructured": {
                    "user_id": user_id,
                    "text": text,
                    "time": time.time()
                }
            }]
    }

    response = {
        "status code": 200,
        "body": body
    }
    return response


def get_lex_response(text):
    user_id = 'ys4242'
    message = ''
    client = boto3.client('lex-runtime')
    lex_response = client.post_text(
        botName='chatbot',
        botAlias='LexBot',
        userId=user_id,
        inputText=text
    )
    message = lex_response['message']

    return message


def lambda_handler(event, context):
    text = get_request(event)
    chatbot_text = get_lex_response(text)
    return build_response(chatbot_text)
