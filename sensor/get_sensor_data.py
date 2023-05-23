import requests
import json
import yaml
import time
import datetime
from copy import deepcopy

SERVER = "http://10.176.34.90:9310/perceptionEvent/updateDatabase"
YAML_PATH = "sensor_config.yaml"

LABORATORY = ["http://10.177.21.113:8123/api", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwZmRmYzMzYjVmNGE0MzA5YWIxNjRkMDliMjYzMGZkOSIsImlhdCI6MTY3MTM1NTg4OCwiZXhwIjoxOTg2NzE1ODg4fQ.y9yYaHoUaucUKfem9UN3CMYYr3E7TLuo2D_fV2yclFk"]

MEETINGROOM01 = ["http://10.177.21.113:8123/api", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwZmRmYzMzYjVmNGE0MzA5YWIxNjRkMDliMjYzMGZkOSIsImlhdCI6MTY3MTM1NTg4OCwiZXhwIjoxOTg2NzE1ODg4fQ.y9yYaHoUaucUKfem9UN3CMYYr3E7TLuo2D_fV2yclFk"]

MEETINGROOM02 = ["http://10.177.11.124:8123/api", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhYmM1OGZiMTE5NDM0MjNmOGE3NTJiMjlhOGFhMWM5OSIsImlhdCI6MTY3NzgwODE4NywiZXhwIjoxOTkzMTY4MTg3fQ.Y-SZk5JoyBEpSNKbCzLiHhAUt4cwxTgeAyLEg8cqOIU"]

ROOMS = {"laboratory01":LABORATORY, "meetingroom01":MEETINGROOM01, "meetingroom02":MEETINGROOM02}

EVENT = {
    "eventIdentify":{
        "eventId":"420978334093021494",
        "name":"",
        "topic":"",
        "location":""
    },
    "timestamp":"1662341017011",
    "perceptionEventType":1,
    "eventData":{
        "location":"",
        "objectId":"",
        "data":{}
    }
}

current_state = {}
time_struct = "%Y-%m-%dT%H:%M:%S"

state_change = ["Door_State"]

def read_yaml_all():
    try:
        # 打开文件
        with open(YAML_PATH,"r",encoding="utf-8") as f:
            data=yaml.load(f,Loader=yaml.FullLoader)
            return data
    except:
        return None


def is_json(text):
    try:
        json_object = json.loads(text)
        return True
    except ValueError as e:
        return False

def read_data(title, url):
    # print(title.split("_")[0])
    ret = None
    room = ROOMS.get(title.split("_")[0])
    headers = {"Authorization": room[1]}

    ret = requests.get(url=room[0]+url, headers=headers)
    device_data = json.loads(ret.text)

    # print(device_data)    
    # print(type(device_data["state"]))

    return device_data

def send_event(device_data, sensor):
    event1 = deepcopy(EVENT)

    change_time = time.strptime(device_data["last_changed"][:19], time_struct)
    event1["timestamp"] = time.mktime(change_time)

    if sensor["name"] in state_change:
        obj = sensor["name"].split("_")[0]
        if sensor["state"] == "on":
            sensor["name"] = obj + "_On"
        else:
            sensor["name"] = obj + "_Off"

    event1["eventIdentify"]["name"] = sensor["name"]
    event1["eventIdentify"]["topic"] = sensor["name"] + "." + sensor["object_id"]
    event1["eventIdentify"]["location"] = sensor["object_id"].split("_")[0]
    event1["eventData"]["location"] = sensor["object_id"].split("_")[0]
    event1["eventData"]["objectId"] = sensor["object_id"]
    if sensor["type"] == "float":
        event1["eventData"]["data"][sensor["state"]] = (float)(device_data["state"])
    elif sensor["type"] == "int":
        event1["eventData"]["data"][sensor["state"]] = (int)(device_data["state"])
    elif sensor["type"] == "string":
        if not sensor["state"] == "people_count":        
            event1["eventData"]["data"][sensor["state"]] = device_data["state"]
        else:
            people = "有" if device_data["state"] == "on" else "无"
            event1["eventData"]["data"][sensor["state"]] = people

        

    print(json.dumps(event1))

    ret = requests.post(url=SERVER, data=json.dumps(event1), headers={'content-type':'application/json'}, verify=False)


if __name__ == '__main__':
    f = read_yaml_all()
    while True:
        for i in f:
            device_data = read_data(i, f[i]["url"])
            if i not in current_state or current_state[i] != device_data["state"]:
                if i in current_state and f[i]["name"] == "Light_State":
                    if abs(float(current_state[i]) - float(device_data["state"])) < 10:
                        current_state[i] = device_data["state"]
                        continue
                current_state[i] = device_data["state"]
                send_event(device_data, f[i])
        print(current_state)
        time.sleep(5)



