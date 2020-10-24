import json
import logging
import time
import os
import boto3
import dateutil.parser
import datetime


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/715339036598/ChatbotQueue'


def sqs_send_message(slots):
    location = slots['location']
    cuisine = slots['cuisine']
    date = slots['date']
    dtime = slots['time']
    people = slots['people']
    phone = slots['phone']

    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=1,
        MessageAttributes={
            'Location': {
                'DataType': 'String',
                'StringValue': location
            },
            'Cuisine': {
                'DataType': 'String',
                'StringValue': cuisine
            },
            'Date': {
                'DataType': 'String',
                'StringValue': date
            },
            'Time': {
                'DataType': 'String',
                'StringValue': dtime
            },
            'People': {
                'DataType': 'String',
                'StringValue': people
            },
            'Phone': {
                'DataType': 'String',
                'StringValue': phone
            }
        },
        MessageBody=(
            'Restauraunt Request Information'
        )
    )


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }


def elicit_intent(session_attributes, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitIntent',
            'message': message
        }
    }
    return response


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def book_restaruant(intent_request):
    location = get_slots(intent_request)["location"]
    cuisine = get_slots(intent_request)["cuisine"]
    date = get_slots(intent_request)["date"]
    dtime = get_slots(intent_request)["time"]
    people = get_slots(intent_request)["people"]
    phone = get_slots(intent_request)["phone"]

    source = intent_request['invocationSource']
    logger.debug(location)

    if source == 'DialogCodeHook':
        slots = get_slots(intent_request)

        validation_result = validate_input(
            location, cuisine, date, dtime, people, phone)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'], intent_request['currentIntent']['name'], slots, validation_result['violatedSlot'], validation_result['message'])

        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {
        }

        return delegate(output_session_attributes, get_slots(intent_request))

    logger.debug('THISISATEST dsajfkldsafjsdlkfjsdlkf ')
    slots = get_slots(intent_request)
    sqs_send_message(slots)

    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Thank you! I will sent detailed information to your phone:{}'.format(phone)})


def greeting(intent_request):
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {
    }
    return elicit_intent(
        session_attributes,
        {
            'contentType': 'PlainText',
            'content': 'Hi there, how can I help?'
        }
    )


def thankyou(intent_request):
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {
    }
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Thank you bye bye!'
        }
    )


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'GreetingIntent':
        return greeting(intent_request)
    if intent_name == 'DiningSuggestionsIntent':
        return book_restaruant(intent_request)
    if intent_name == 'ThankYouIntent':
        return thankyou(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def isvalid_people(people):
    try:
        num = int(people)
        if num > 0 and num < 20:
            return True
        else:
            return False

    except ValueError:
        return float('nan')


def validate_input(location, cuisine, date, dtime, people, phone):

    locations = ['new york', 'ny', 'manhattan',
                 'manhattan, ny', 'new york, ny']
    if location is not None and location.lower() not in locations:
        return build_validation_result(False,
                                       'location',
                                       "We currently don't support {}, Please try location in new york, for example: Manhattan".format(location))

    cuisines = ["chinese", "japanese",
                "indian",  "mexican", "american", "italian"]
    if cuisine is not None and cuisine.lower() not in cuisines:
        return build_validation_result(False,
                                       'cuisine',
                                       "We do not have {}, please try cuisines in: 'Chinese', 'Japanese', 'Indian',  'Mexican', 'American' or 'Italian'".format(cuisine))
    if date is not None:
        if not isvalid_date(date):
            return build_validation_result(False, 'date', 'I did not understand that, when would you like?')
        elif datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today():
            return build_validation_result(False, 'date', 'Appointments must be scheduled in the future. Can you try a different date?')

    if dtime is not None:
        print(dtime)
        if len(dtime) != 5:
            return build_validation_result(False, 'time', "Please try a valid time for example 18:00.")
        curr_full_time_str = str(datetime.datetime.strptime(
            date, '%Y-%m-%d').date()) + ' ' + dtime
        if datetime.datetime.strptime(curr_full_time_str, '%Y-%m-%d %H:%M') < datetime.datetime.now():
            return build_validation_result(False, 'time', "Please try a valid time that is not before")

    if people is not None:
        if not isvalid_people(people):
            return build_validation_result(False, 'people', 'Your party size should be less than 20. Please try agian')

    return build_validation_result(True, None, None)


def lambda_handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()

    return dispatch(event)
