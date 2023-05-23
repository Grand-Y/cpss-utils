def delete_event():
    query = {"eventData.data.signed_in_count": 0}
# 删除匹配的文档
    result = db.delete_many(query)
# 输出删除结果
    print(f"Deleted {result.deleted_count} documents")