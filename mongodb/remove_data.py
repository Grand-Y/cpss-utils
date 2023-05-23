import pymongo


# SERVER = 'mongodb://10.176.34.90:27017/structural_characterization'
SERVER = 'mongodb://10.176.34.90:27017/structural_characterization'
client = pymongo.MongoClient(SERVER, username='zsm', password='123456')
db = client['structural_characterization']['event_management1']

def delete_event():
    query = {"eventData.data.signed_in_count": 0}
# 删除匹配的文档
    result = db.delete_many(query)
# 输出删除结果
    print(f"Deleted {result.deleted_count} documents")


def delete_all():
    db_list = client.list_database_names()
    # print(db_list)

    myquery = { "eventType": {"$ne":"1"} }

    x = db.delete_many(myquery)
    print(x.deleted_count)

if __name__ == '__main__':
    delete_event()
    # delete_all()