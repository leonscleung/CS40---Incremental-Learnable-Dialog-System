import re

rules = [
 {
   "slot": "greeting",
   "questions": ["Hello{name}, how may I be of your address?",
                 "Hi{name}, how can I help you?",
                 "Hello{name}, how may I provide assistance to you?"]
 },
 {
   "slot": "name",
   "questions": ["Can I have your name please?",
                 "May I know your name please?"]
 },
 {
   "slot": "place",
   "questions": ["Can you let me know your boarding and landing points?",
                 "Can I have your journey locations?"]
 },
 {
   "slot": "place_from",
   "questions": ["Which city are you leaving from?",
                 "May I know your departure city?"]
 },
 {
   "slot": "place_to",
   "questions": ["Can I know your destination?",
                 "May I know your return city?"]
 },
 {
   "slot": "trip_type",
   "questions": ["Will this be one way or round trip?",
                 "Are you looking for one way or round trip flight?"]
 },
 {
    "slot": "date",
    "questions": ["Could you please share your departure and arrival day?",
                  "Can I have your travelling dates?",
                  "Please share your planned travel dates?"]
},
 {
    "slot": "date_departure",
    "questions": ["Please share your departure date?"]
 },
 {
    "slot": "date_return",
    "questions": ["Please share your return date?"]
 },
 {
   "slot": "connection_limit",
   "questions": ["How many connections would you like at most?",
                 "Do you have any connection limit preferrence?"]
 },
 {
   "slot": "class",
   "questions": ["Are you comfortable with economy class flight or business class flight?",
                 "Would you like to prefer business class or economy class?"]
 },
 {
   "slot": "others",
   "questions": ["Do you have any other preference?",
                 "Do you have any other specification that you are looking for?"]
 },
 {
   "slot": "searchResult",
   "questions": {"onewaywithconnection":"Hi {name}, there is a {class_type} flight travelling between {place_from} and {place_to} departure on {date_departure} available with United airlines, with connection limit {connection_limit} and fare 100. Shall I proceed for booking?",
                 "onewaywithout":"Hi {name}, there is a {class_type} flight directly travelling between {place_from} and {place_to} departure on {date_departure} available with United airlines and fare 100. Shall I proceed for booking?",
                 "roundwaywithout":"Hi {name}, I found a direct flight from {place_from} to {place_to}. Your flights will be on {date_departure} and {date_return}, as {class_type} from United Airlines. Your ticket price will be 100. Is that ok for you?",
                 "roundwaywithconnection": "Hi {name}, I found a flight with {connection_limit} stop(s) from {place_from} to {place_to}. Your flights will be on {date_departure} and {date_return}, as {class_type} from United Airlines. Your ticket price will be 100. Is that ok for you?"}
 },
 {
   "slot": "confirmationY",
   "questions": ["Your reservation has been done. You can collect your ticket at the time of checkin.",
                 "Your ticket has been confirmed.",
                 "Ok, your ticket has been processed."]
 },
 {
    "slot": "confirmationN",
    "questions": ["Thanks for reaching us. For further assistance, ou can also call to our customer-executive on 022-1111111."]
 },
 {
   "slot": "ending",
   "questions": ["Thanks for reaching us.", "Thank you for choosing us.", "Have a nice day.", "You are welcome."]
 },
 {
    "slot": "defaulterror",
    "questions": ["For further assistance, ou can also call to our customer-executive on 022-1111111."]
 }
]

slot_list = ['greeting', 'name', 'place', 'place_from', 'place_to', 'trip_type', 'date',
             'date_departure', 'date_return', 'connection_limit', 'class',
             'others', 'searchResult', 'confirmationY', 'confirmationN', 'ending', 'defaulterror']


#Here we define the regular expression templates
EXPRESSIONS = [("hello.*book.*", ["name","greeting"]),
               ("hi.*book.*", ["name","greeting"]),
               ("i.*book.*", ["name","greeting"]),
               ("i.*fly.*", ["name","greeting"]),
               ("good morning.*book.*", ["name","greeting"]),
               ("good afternoon.*book.*", ["name","greeting"]),
               ("good evening.*book.*", ["name","greeting"]),
               ("good morning.*", ["greeting"]),
               ("good afternoon.*", ["greeting"]),
               ("good evening.*", ["greeting"]),
               ("hello.*", ["greeting"]),
               ("hi.*", ["greeting"]),
               ("hey.*", ["greeting"]),
               ("please.*proceed.*",   ["confirmationY"]),
               ("ok.*proceed.*",   ["confirmationY"]),
               ("sure.*proceed.*",   ["confirmationY"]),
               ("yes.*proceed.*",   ["confirmationY"]),
               ("i.*check.*another.*", ["confirmationN"]),
               ("ok.*i.*check.*another.*", ["confirmationN"]),
               ("thanks.*",   ["ending"]),
               ("thank.*you.*",   ["ending"])]

def extractSlot(inputString):
    #Next we are going to look through all the patterns that we have until we find one that matches a template
    #For every regex pattern that we have
    for regex, logicalForm in EXPRESSIONS:
        compiledRegex = re.compile(regex)

        result = compiledRegex.match(inputString)

        if(result != None):
            print("We found a match!", regex, logicalForm)
            return logicalForm         #Return the logical form so we are able to use it later

    print("We didn't find a match") #If we didn't find a match, say so
    return None


confirmations = {'opening1': ['Got it.',
                             'Thanks for your information.',
                             'Sure.',
                             'Ok.'],
                 'opening2': ['I will try to find','I will search for', 'I will get', 'So you want me to find'],
                 'round': 'a return ticket',
                 'oneway':'a one-way ticket',
                 'ticket':'a flight ticket',
                 'place': 'from {place_from} to {place_to}',
                 'round_date': 'with departure date on {date_departure} and return date on {date_return}',
                 'one_date': 'taking off on {date_departure}',
                 'connection': 'with maximum {connection_limit} stop(s)',
                 'direct': 'without stop',
                 'class': 'in {class_type}',
                 'ending': 'for you.'}
