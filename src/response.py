from src.utilities import PrepUtility
from src.rules import rules, slot_list, extractSlot, confirmations
from src.slotDetection import find_connection, find_dates, find_class_type, find_name, find_trip, get_place
from datetime import datetime
import random
import os
import pathlib
from src.utilities import read_json, write_json

root = pathlib.Path(os.path.abspath(__file__)).parent.parent
test_tag_path = str(root) + '/model_tmp/test_results/tagging.test.hyp.txt'

slot_checked = []

def get_response(message):
    user_in = PrepUtility.create_test_seq_in(message)
    tag_ls, word_ls = extract_information(test_tag_path)
    customer_name = find_name(message)
    place_from, place_to, isNewPlace = get_place(tag_ls, word_ls)
    date_departure, date_return, isNewDate = find_dates(message)
    is_round_trip, isNewTrip = find_trip(tag_ls, word_ls)
    connection_limit, isNewConnection = find_connection(tag_ls, word_ls)
    class_type, isNewClass = find_class_type(tag_ls, word_ls)
    informationDict = dict(date_departure=date_departure, date_return=date_return,
                    place_from=place_from, place_to=place_to, is_round_trip=is_round_trip,
                    customer_name=customer_name, connection_limit=connection_limit, class_type=class_type,
                           isNewPlace = isNewPlace, isNewDate = isNewDate, isNewTrip = isNewTrip,
                           isNewConnection = isNewConnection, isNewClass = isNewClass)
    checkSlot(place_from, place_to, date_departure, date_return, is_round_trip, connection_limit, customer_name, class_type)

    #print("[INFO] user in = ", user_in)
    print('[INFO] slot_checked before: ', slot_checked)
    slot = extractSlot(user_in)
    if (slot != None) and (slot[0] not in slot_checked):
        slotIndex = slot_list.index(slot[0])
        slot_checked.extend(slot)
        message_response = random.choice(rules[slotIndex]['questions'])
        response_list = prepareResponse(slot[0], message_response, informationDict)
    else:
        slot_left = [s for s in slot_list if s not in slot_checked]
        if slot_left:
            slot_to_check = slot_left[0]
            slot_checked.append(slot_to_check)
        else:
            slot_to_check = 'defaulterror'
        slotIndex = slot_list.index(slot_to_check)
        message_response = random.choice(rules[slotIndex]['questions'])
        response_list = prepareResponse(slot_to_check, message_response, informationDict)

    print('[INFO] slot_checked after: ', slot_checked)
    response = dict(messages=response_list, date_departure=date_departure, date_return=date_return,
                    place_from=place_from, place_to=place_to, is_round_trip=is_round_trip,
                    customer_name=customer_name, class_type=class_type)
    return response

def extract_information(test_tag_path):
    f = open(test_tag_path, "r")
    lines = f.readlines()
    tag_ls = []
    word_ls = []
    for line in lines:
        if line.strip().split()[0] == 'EOS':
            break
        elif line.strip().split()[0] != 'BOS':
            word_ls.append(line.strip().split()[0])
            tag_ls.append(line.strip().split()[1])
    print('[INFO] extract_information tag_ls: ', tag_ls, 'word_ls: ', word_ls)
    return tag_ls, word_ls

def checkSlot(place_from, place_to, date_departure, date_return, is_round_trip, connection_limit, customer_name, class_type):
    if 'place_from' not in slot_checked and place_from:
        slot_checked.append('place_from')
        if 'place'not in slot_checked:
            slot_checked.append('place')
    if 'place_to' not in slot_checked and place_to:
        slot_checked.append('place_to')
        if 'place'not in slot_checked:
            slot_checked.append('place')

    if 'date_departure' not in slot_checked and date_departure:
        slot_checked.append('date_departure')
        if 'date' not in slot_checked:
            slot_checked.append('date')
    if 'date_return' not in slot_checked and (date_return or is_round_trip==False):
        slot_checked.append('date_return')
        if 'date' not in slot_checked:
            slot_checked.append('date')

    if 'trip_type' not in slot_checked and (is_round_trip is not None):
        slot_checked.append('trip_type')

    if 'connection_limit' not in slot_checked and connection_limit:
        slot_checked.append('connection_limit')

    if 'name' not in slot_checked and customer_name:
        slot_checked.append('name')

    if 'class' not in slot_checked and class_type:
        slot_checked.append('class')

def prepareResponse(slot, response, informationDict):
    response_list = []
    customer_name = informationDict.get('customer_name', '')
    place_from = informationDict.get('place_from', None)
    place_to = informationDict.get('place_to', None)
    date_departure = informationDict.get('date_departure', None)
    date_return = informationDict.get('date_return', None)
    is_round_trip = informationDict.get('is_round_trip', None)
    connection_limit = informationDict.get('connection_limit', None)
    class_type = informationDict.get('class_type', None)
    isNewPlace = informationDict.get('isNewPlace')
    isNewDate = informationDict.get('isNewDate')
    #isNewTrip = informationDict.get('isNewTrip')
    #isNewConnection = informationDict.get('isNewConnection')
    isNewClass = informationDict.get('isNewClass')
    print('slot:', slot, 'customer_name: ', customer_name)
    if slot == 'greeting':
        response = response.format(name = ' ' + customer_name)
    if slot == 'searchResult':
        response = response.format(class_type = class_type, place_from=place_from,
                                       place_to=place_to, connection_limit=connection_limit)

    summary_response = []
    checkList = [isNewPlace, isNewDate, isNewClass]
    if any(checkList):
        summary_response.append(random.choice(confirmations['opening']))
    if place_from and place_to and isNewPlace:
        summary_response.append(confirmations['place'].format(place_from=place_from, place_to=place_to))
        summary_response.append(confirmations['ending'])
    if is_round_trip == True and date_departure and date_return and isNewDate:
        summary_response.append(confirmations['round_date'].format(date_departure=date_departure, date_return=date_return))
    if is_round_trip == False and date_departure and isNewDate:
        summary_response.append(confirmations['one_date'].format(date_departure=date_departure))
    # if connection_limit and isNewConnection:
    #     summary_response.append(confirmations['connection'].format(connection_limit=connection_limit))
    if connection_limit and class_type and isNewClass:
        summary_response.append(confirmations['class'].format(connection_limit=connection_limit, class_type=class_type))
    if len(summary_response)>=1:
        summary = ' '.join(summary_response)
        response_list.append(dict(message=summary, time=format_current_time()))

    response_list.append(dict(message=response, time=format_current_time()))
    return response_list



def format_current_time():
    return datetime.now().strftime("%H:%M:%S")