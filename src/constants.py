import calendar

# Parameters
####################################################
PATH_GDRIVE_ROOT = '/content/gdrive/My Drive'
FILES_ROOT = '%s/models' % '..'

WORD_DICT_ROOT = '%s/word_dict' % FILES_ROOT
WV_MODEL_ROOT = '%s/wv_model' % FILES_ROOT
SEQ_MODEL_ROOT = '%s/seq_model' % FILES_ROOT

WORD_DICT_A_PATH = '%s/word_dict_a' % WORD_DICT_ROOT
WORD_DICT_Q_PATH = '%s/word_dict_q' % WORD_DICT_ROOT
WV_MODEL_PATH = '%s/word2vect_sg' % WV_MODEL_ROOT
SEQ_MODEL_PATH = '%s/seq2seq' % SEQ_MODEL_ROOT
CHAT_LOG_PATH = '%s/models/chat_log.txt' % PATH_GDRIVE_ROOT

BATCH_SIZE = 64
VOCAB_SIZE = 1833
LEARNING_RATE = 1e-2

# hyper-parameters - Word2Vec
WINDOW_SIZE = 1
SAMPLE_SIZE = 16
EMBEDDING_SIZE = 50
NUM_EPOCH = 50

# Seq2Seq:hyper-parameters
SAMPLE_SIZE2 = 4
NUM_EPOCH2 = 1000
HIDDEN_SIZE = 256

DISPLAY_INTERVAL = 100
MAX_LEN_Q = 12

STAN_JAR_PATH = './stanford-ner/stanford-ner.jar'

STAN_MODEL_PATH = './stanford-ner/english.all.3class.distsim.crf.ser.gz'

# Model
####################################################
COUNTRIES = ['Atlanta', 'Austin', 'Boston', 'Charlotte', 'Chicago', 'Dallas', 'Denver', 'Detroit', 'Houston', 'Los Angeles', 'Miami', 'Minneapolis', 'New York', 'Newark', 'Oakland', 'Orlando', 'Philadelphia', 'Phoenix', 'San Francisco', 'Seattle', 'Washington', 'Washington']
CLASSES = [dict(name="Economy", value="economy class"), dict(name="Business", value="business class")]

DEPART_LOC_LS = ['B-fromloc.city_name', 'I-fromloc.city_name', 'B-fromloc.airport_name', 'I-fromloc.airport_name', 'B-fromloc.state_name', 'I-fromloc.state_name',
'B-fromloc.airport_code']

RETURN_LOC_LS = ['B-toloc.city_name', 'I-toloc.city_name', 'B-toloc.airport_name', 'I-toloc.airport_name',
                 'B-toloc.state_name', 'I-toloc.state_name', 'B-toloc.airport_code',
                 'B-toloc.state_code','B-toloc.country_name']

ROUND_TRIP = ['B-round_trip','I-round_trip']

CLASS_TYPE = ['B-class_type','I-class_type','B-economy','I-economy']

CONNECTION_LS = 'B-connect'

STOP_LS = ['B-flight_stop', 'I-flight_stop']

NUMBER_LS = ['zero', 'one', 'two', 'three']

DAY_DICT = {}
for num, day in enumerate(calendar.day_name):
    DAY_DICT[day.lower()] = num
    DAY_DICT[day] = num

MONTH_DICT = {}
for num, month in enumerate(calendar.month_name):
    if month:
        MONTH_DICT[month]= num

NEXT_MONTH_LS = ['next month', 'the following month']
NUMBER_DICT = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}
