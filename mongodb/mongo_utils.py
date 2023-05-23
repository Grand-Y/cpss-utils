from pymongo import MongoClient

# client_zm = MongoClient("mongodb://zsm:123456@10.176.34.90:27017/structural_characterization")
client_se = MongoClient("mongodb://zsm:123456@10.176.34.90:27017/structural_characterization")


db = client_se['structural_characterization']
collection = db['event_management1']

def delete_all():
    collection.delete_many({"eventType":True})

# print(collection.find_one({"eventIdentify.name": "Person_Leave"}))

def delete_event():
    query = {"eventIdentify.Person_Entry": {"$exists": True}}
# 删除匹配的文档
    result = collection.delete_many(query)
# 输出删除结果
    print(f"Deleted {result.deleted_count} documents")

if __name__ == '__main__':
    delete_event()
    # print(collection.find({"eventType":False}))
    print("一眼丁真")

