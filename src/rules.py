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
   "questions": ["Sure, can I have your name please?",
                 "Sure, may I know your name please?"]
 },
 {
   "slot": "place",
   "questions": ["Can you let me know your boarding and landing points?",
                 "Ok, can I have your journey locations?"]
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
   "questions": ["Ok, will this be one way or round trip?",
                 "Are you looking for one way or round trip flight?"]
 },
 {
    "slot": "date",
    "questions": ["Sure, could you please share your departure and arrival day?",
                  "Can I have your travelling dates?",
                  "Sure, please share your planned travel dates?"]
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
   "questions": ["There is a {class_type} flight travelling between {place_from} and {place_to} available with United airlines, with connection limit {connection_limit} and fare 100. Shall I proceed for booking?"]
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


confirmations = {'opening': ['If I understand correctly, ',
                             'Please check if I got it correctly, ',
                             'I want to double-check with you that '],
                'place': 'you are flying from {place_from} to {place_to}. ',
                'round_date': 'you want a round trip from {date_departure} to {date_return}.',
                'one_date': 'you want a one-way trip departure from {date_departure}.',
                'connection': 'the number of maximum connection you prefer is {connection_limit}.',
                'class': 'you prefer a {class_type} flight with {connection_limit} connection .',
                'ending': 'You can always modify the search fields on the right if I misunderstand anything.'}
