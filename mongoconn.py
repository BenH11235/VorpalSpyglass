import vorpalconfig
import pymongo

mongoConn = pymongo.MongoClient(
    vorpalconfig.MONGODB_ADDRESS,
    vorpalconfig.MONGODB_PORT
)

vorpalDatabase = mongoConn[vorpalconfig.MONGODB_DBNAME]

deletionsDictionary = vorpalDatabase[vorpalconfig.MONGODB_DICT_DEL_DISTANCES]
