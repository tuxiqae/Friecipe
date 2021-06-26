import pymongo

MONGO_CONN = pymongo.MongoClient(host="localhost",
                                 port=27017,
                                 # username="root",
                                 # password="pass"
                                 )
DB = MONGO_CONN["friecipe"]
# DB["users"].create_index("_id")
