from src.utilities import read_json, write_json
from datetime import datetime
import datefinder
from src.constants import DEPART_LOC_LS, RETURN_LOC_LS, ROUND_TRIP, CLASS_TYPE, STOP_LS, NUMBER_LS, CONNECTION_LS
from src.utilities import extract_person_name

def find_name(message):
    ticket_info = read_json("ticket.json")
    customer_name = ticket_info.get("customer_name", None)
    # print('customer_name: ', customer_name)
    if customer_name:
        return customer_name
    else:
        customer_name = extract_person_name(message)
        ticket_info.update(dict(customer_name=customer_name))
        write_json(ticket_info, "ticket.json")
        return customer_name


def process_date(date_find, date_style):
    return date_find.strftime(date_style) if date_find else None

def find_dates(message):
    available_dates = datefinder.find_dates(message)
    isNewDates = False
    ticket_info = read_json("ticket.json")
    date_departure, date_return = ticket_info.get("date_departure", None), ticket_info.get("date_return", None)
    date_departure = datetime.strptime(date_departure,"%Y-%m-%d") if date_departure else None
    date_return = datetime.strptime(date_return,"%Y-%m-%d") if date_return else None
    for available_date in available_dates:
        isNewDates = True
        if date_departure is None:
            date_departure = available_date
        elif available_date < date_departure:
            date_return, date_departure = date_departure, available_date
        elif available_date > date_departure:
            date_return = available_date

    ticket_info.update(dict(date_departure=process_date(date_departure,"%Y-%m-%d"),
                            date_return=process_date(date_return,"%Y-%m-%d")))
    write_json(ticket_info, "ticket.json")

    return process_date(date_departure,"%Y-%m-%d"), process_date(date_return,"%Y-%m-%d"), isNewDates

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


def get_place(tag_ls, word_ls):
    ticket_info = read_json("ticket.json")
    from_city, to_city = ticket_info.get("place_from", None), ticket_info.get("place_to", None)
    isNewPlace = False

    depart_index_ls = []
    return_index_ls = []
    for tag in tag_ls:
        if tag in DEPART_LOC_LS:
            depart_index_ls.append(tag_ls.index(tag))
        if tag in RETURN_LOC_LS:
            return_index_ls.append(tag_ls.index(tag))
    if len(depart_index_ls) == 2:
        from_city = word_ls[depart_index_ls[0]].capitalize() + ' ' + word_ls[depart_index_ls[1]].capitalize()
        isNewPlace = True
    elif len(depart_index_ls) == 1:
        from_city = word_ls[depart_index_ls[0]].capitalize()
        isNewPlace = True
    if len(return_index_ls) == 2:
        to_city = word_ls[return_index_ls[0]].capitalize() + ' ' + word_ls[return_index_ls[1]].capitalize()
        isNewPlace = True
    elif len(return_index_ls) == 1:
        to_city = word_ls[return_index_ls[0]].capitalize()
        isNewPlace = True
    print('[INFO] place_from, place_to', from_city, to_city)
    ticket_info.update(dict(place_from=from_city,
                            place_to=to_city))
    write_json(ticket_info, "ticket.json")
    return from_city, to_city, isNewPlace

def find_trip(tag_ls, word_ls):
    ticket_info = read_json("ticket.json")
    is_round_trip = ticket_info.get("is_round_trip", None)
    isNewTrip = False
    round_trip_ls = []
    for tag in tag_ls:
        if tag in ROUND_TRIP:
            round_trip_ls.append(word_ls[tag_ls.index(tag)])
            isNewTrip = True
    trip = ' '.join(round_trip_ls)
    print('[INFO] find trip: ', trip)
    if trip == 'one way':
        is_round_trip = False
    elif trip and trip != 'one way':
        is_round_trip = True
    ticket_info.update(dict(is_round_trip=is_round_trip))
    write_json(ticket_info, "ticket.json")
    return is_round_trip, isNewTrip

def find_class_type(tag_ls, word_ls):
    ticket_info = read_json("ticket.json")
    class_type = ticket_info.get("class_type", None)
    class_type_ls = []
    isNewClass = False
    for tag in tag_ls:
        if tag in CLASS_TYPE:
            class_type_ls.append(word_ls[tag_ls.index(tag)])
            class_type = ' '.join(class_type_ls)
            isNewClass = True
    print('[INFO] class slot: ', class_type)
    ticket_info.update(dict(class_type=class_type))
    write_json(ticket_info, "ticket.json")
    return class_type, isNewClass

def find_connection(tag_ls, word_ls):
    ticket_info = read_json("ticket.json")
    connect = ticket_info.get("connection_limit", None)
    isNewConnection = False
    connect_num = []
    for tag in tag_ls:
        # print('tag', tag, 'word_ls[tag_ls.index(tag)] ', word_ls[tag_ls.index(tag)] )
        # print()
        if tag == CONNECTION_LS and word_ls[tag_ls.index(tag)] == 'direct':
            connect_num.append('zero')
            isNewConnection = True
        if tag in STOP_LS:
            connect_num.append(word_ls[tag_ls.index(tag)])
            isNewConnection = True
    for ele in connect_num:
        if ele in NUMBER_LS:
            connect = ele
    print('[INFO] connection: ', connect)
    ticket_info.update(dict(connection_limit=connect))
    write_json(ticket_info, "ticket.json")
    return connect, isNewConnection