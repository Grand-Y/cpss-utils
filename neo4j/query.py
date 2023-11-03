from json.tool import main
from py2neo import Graph, Node, Relationship, NodeMatcher
import snowflake.client
import json
import yaml


# SERVER = "http://10.176.34.90:9310/perceptionEvent/updateDatabase"
graph = Graph('http://10.177.29.226/:7474', auth=('neo4j', '12345678'), name="neo4j")
queue = []
ENV_PATH = "./conf/build.json"
EVENT_PATH= "./conf/eventType.txt"


def get_room(graph):
    res = []
    data = graph.run("match (n:Space) return n").data()
    for i in data:
        if i["n"]["name"] == "Context": continue
        else: res.append(i["n"]["name"])
    print(res)
    return res

def get_device_by_room(graph, room_name):
    res = []
    data = graph.run("match (n:Device)-[r:BELONG_TO]->(nn) where nn.name='" + room_name + "' return n").data()
    for i in data:
        res.append(i["n"]["name"])
    print(res)
    return res

def get_effect_by_room(graph, room_name):
    res = []
    data = graph.run("match (n:Effect) where n.room='" + room_name + "' return n").data()
    for i in data:
        res.append(i["n"]["name"])
    print(res)
    return res

def get_state_by_room(graph, room_name):
    res = []
    data = graph.run("match (m)-[r:HAS]->(n:EnvState) where m.name='" + room_name + "' return n").data()
    for i in data:
        res.append(i["n"]["name"])
    print(res)
    return res

def get_device(graph, room_name, device_name):
    res = {}
    data = graph.run("match (n:Device)-[r:BELONG_TO]->(nn) where n.name='" + device_name + "' and nn.name='" + room_name + "' return n").data()[0]["n"]
    res["name"] = data["name"]
    res["state"] = data["state"]
    res["type"] = data["type"]
    print(res)
    return res

def get_state(graph, room_name, state_name):
    res = {}
    data = graph.run("match (m)-[r:HAS]->(n:EnvState) where m.name='" + room_name + "' and n.name='" + state_name + "' return n").data()[0]["n"]
    res["name"] = data["name"]
    res["value"] = data["value"]
    print(res)
    return res

def get_action_by_device(graph, room_name, device_name):
    res = []
    actions = graph.run("match (n:Action)<-[:CAN]-(m:Device)-[:BELONG_TO]->(nn) where m.name='" + device_name + "' and nn.name='" + room_name + "' return n").data()
    for i in actions:
        res.append(i["n"]["name"])
    print(res)
    return res

def get_action_by_state(graph, room_name, state_name):
    res = []
    actions = graph.run("match (nn)-[:HAS]->(m:EnvState)-[:CAN]->(n:Action) where m.name='" + state_name + "' and nn.name='" + room_name + "' return n").data()
    for i in actions:
        res.append(i["n"]["name"])
    print(res)
    return res

def get_effect_and_pre(graph, room_name, device_name, action_name):
    res = {}
    data = graph.run("match (p)<-[:DEPENDING_ON]-(e:Effect)<-[:HAS]-(a:Action)<-[:CAN]-(d:Device) where e.room='" + room_name + "' and  a.name='" + action_name + "' and d.name='" + device_name + "' return e, p").data()
    print(data[0])
    print(data[1])
    for i in data:
        effect_name = i["e"]["name"]
        if effect_name in res:
            res[effect_name].append(i["p"]["room"] + "." + i["p"]["name"])
            continue
        res[effect_name] = []
        res[effect_name].append(i["p"]["room"] + "." + i["p"]["name"])
    print(res)
    return res

def get_room_related(graph, room_name):
    res = []
    data = graph.run("match (n)-[:ADJACENT_TO]->(m) where m.name='" + room_name + "' return n").data()
    for i in data:
        res.append(i["n"]["name"])
    print(res)
    return res

if __name__ == '__main__':
    get_room(graph)
    get_device_by_room(graph, "Lab")
    get_effect_by_room(graph, "Lab")
    get_state_by_room(graph, "Lab")
    get_device(graph, "Lab", "Door001")
    get_state(graph, "Lab", "Noise")
    get_action_by_device(graph, "Lab", "Door001")
    get_action_by_state(graph, "Lab", "Noise")
    get_effect_and_pre(graph, "Lab", "Window001", "action_on")
    get_room_related(graph, "Lab")
