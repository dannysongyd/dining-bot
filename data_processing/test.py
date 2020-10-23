import dateutil.parser
import datetime
import math


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
        if num > 0:
            return True
        else:
            return False

    except ValueError:
        return float('nan')


def validate_input(location, cuisine, date, time, people, phone):

    locations = ['new york', 'ny',
                 'manhattan', 'manhattan, ny', 'new york, ny']
    if location is not None and location.lower() not in locations:
        return build_validation_result(False,
                                       'location',
                                       "We currently don't support {}, Please try location in new york, for example: Manhattan".format(location))

    cuisines = ["chinese", "japanese",
                "indian",  "mexican", "american", "italian"]
    if cuisine is not None and cuisine.lower() not in cuisines:
        return build_validation_result(False,
                                       'cuisine',
                                       "We do not have {}, please try cuisines in: 'Chinese', 'Japanese', 'Indian',  'Mexican', 'American' or 'Italian'".format(cuisines))
    if date is not None:
        if not isvalid_date(date):
            return build_validation_result(False, 'date', 'I did not understand that, when would you like to dinner?')
        elif datetime.datetime.strptime(date, '%Y-%m-%d').date() <= datetime.date.today():
            return build_validation_result(False, 'date', 'Appointments must be scheduled in the future. Can you try a different date?')

    if time is not None:

        if len(time) != 5:
            return build_validation_result(False, 'time', "Please try a valid time for example 18:00.")
        for i in range(len(time)):
            if i == 2:
                if time[i] != ":":
                    return build_validation_result(False, 'time', "Please try a valid time for example: 18:00.")
            else:
                if not time[i].isalnum():
                    return build_validation_result(False, 'time', "Please try a valid time for example: 18:00.")

    if people is not None:

        if not isvalid_people(people):
            return build_validation_result(False, 'people', 'I did not understand that, how many people?')

    return build_validation_result(True, None, None)
