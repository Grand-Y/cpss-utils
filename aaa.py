import requests
import json
import yaml
import time
from copy import deepcopy

SERVER = "http://10.176.34.90:9310/perceptionEvent/updateDatabase"

EVENT = {
    "eventIdentify":{
        "eventId":"420978334093021494",
        "name":"Person_Entry",
        "topic":"Person_Entry.laboratory01",
        "location":"laboratory01"
    },
    "timestamp":"1662341017011",
    "perceptionEventType":1,
    "eventData":{
        "location":"laboratory01",
        "objectId":"岳世杰",
        "data":{}
    }
}

ret = requests.post(url=SERVER, data=json.dumps(EVENT), headers={'content-type':'application/json'})