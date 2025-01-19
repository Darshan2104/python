from pymongo import MongoClient

dev_url = "mongodb://root:root@172.16.22.5:27019/?authSource=admin&readPreference=primary&directConnection=true&ssl=false"
dev_db = "analytics_dashboard"
dev_col = "test_queue"


conn = MongoClient(dev_url)[dev_db][dev_col]
