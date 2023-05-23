import mysql.connector
import yaml
import requests
import json
import time

YAML_PATH = "sensor_config.yaml"

LABORATORY = ["http://10.177.21.113:8123/api", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwZmRmYzMzYjVmNGE0MzA5YWIxNjRkMDliMjYzMGZkOSIsImlhdCI6MTY3MTM1NTg4OCwiZXhwIjoxOTg2NzE1ODg4fQ.y9yYaHoUaucUKfem9UN3CMYYr3E7TLuo2D_fV2yclFk"]

MEETINGROOM01 = ["http://10.177.21.113:8123/api", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwZmRmYzMzYjVmNGE0MzA5YWIxNjRkMDliMjYzMGZkOSIsImlhdCI6MTY3MTM1NTg4OCwiZXhwIjoxOTg2NzE1ODg4fQ.y9yYaHoUaucUKfem9UN3CMYYr3E7TLuo2D_fV2yclFk"]

MEETINGROOM02 = ["http://10.177.11.124:8123/api", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhYmM1OGZiMTE5NDM0MjNmOGE3NTJiMjlhOGFhMWM5OSIsImlhdCI6MTY3NzgwODE4NywiZXhwIjoxOTkzMTY4MTg3fQ.Y-SZk5JoyBEpSNKbCzLiHhAUt4cwxTgeAyLEg8cqOIU"]

ROOMS = {"laboratory01":LABORATORY, "meetingroom01":MEETINGROOM01, "meetingroom02":MEETINGROOM02}

db = mysql.connector.connect(
    host="sh-cynosdbmysql-grp-8x7xozb2.sql.tencentcdb.com",
    port="27187",
    user="root",
    passwd="IamElaine1908",
    database="lowcode"
)
time_struct = "%Y-%m-%dT%H:%M:%S"

cursor = db.cursor()

def create_table():
    cursor.execute("CREATE TABLE sensor_data (eventId int auto_increment primary key, eventName varchar(50), timestamp varchar(50), location varchar(50), objectId varchar(50), data varchar(10))")

def delete_table():
    cursor.execute("DROP TABLE sensor_data")

def show_table():
    cursor.execute("show tables")
    for i in cursor:
        print(i)

def read_yaml_all():
    try:
        # 打开文件
        with open(YAML_PATH,"r",encoding="utf-8") as f:
            data=yaml.load(f,Loader=yaml.FullLoader)
            return data
    except:
        return None

def read_data(title, url):
    ret = None
    room = ROOMS.get(title.split("_")[0])
    headers = {"Authorization": room[1]}

    ret = requests.get(url=room[0]+url, headers=headers)
    device_data = json.loads(ret.text)


    return device_data


def insert_data(device_data, sensor):
    change_time = time.strptime(device_data["last_changed"][:19], time_struct)
    timestamp = time.mktime(change_time)
    sql = "insert into sensor_data (eventName, timestamp, location, objectId, data) VALUES (%s, %s, %s, %s, %s)"
    val = (sensor["name"], timestamp, sensor["object_id"].split("_")[0], sensor["object_id"], device_data["state"])
    cursor.execute(sql,val)
    db.commit()


if __name__ == '__main__':
    f = read_yaml_all()
    while True:
        for i in f:
            device_data = read_data(i, f[i]["url"])   
            insert_data(device_data, f[i])
        time.sleep(5)