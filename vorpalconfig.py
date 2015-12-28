import logging

#MongoDB Configuration

MONGODB_ADDRESS = "localhost"
MONGODB_PORT = 27017
MONGODB_DBNAME = "master"
MONGODB_TRAINING_COLLECTION = "dgd_training"
MONGODB_TEST_WHITE_COLLECTION = "dgd_test_white"
MONGODB_TEST_BLACK_COLLECTION = "dgd_test_black"
MONGODB_DICT_DEL_DISTANCES = "dgd_data"

#Logging Configuration

#set to logging.INFO to enable verbose mode
#set to logging.CRITICAL to disable verbose mode
loggingLevel = logging.CRITICAL

#Set to True to enable log throttling 
#(pausing the first 3 times a log event occurs)
throttling = False


#Dictionary location

dictionaryLocation = "dictionary.txt"
