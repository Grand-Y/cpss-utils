from json.tool import main
from py2neo import Graph, Node, Relationship, NodeMatcher
import snowflake.client
import json
import yaml


# SERVER = "http://10.176.34.90:9310/perceptionEvent/updateDatabase"
graph = Graph('http://localhost:7474', auth=('neo4j', '123456'))
ENV_PATH = "./conf/build_env.json"
EVENT_PATH= "./conf/eventType.txt"

def read_json_all(path):
    try:
        # 打开文件
        with open(path, "r", encoding="utf-8") as f:
            data=json.load(f)
            return data
    except:
        return None



def delete_all(graph):
    graph.run("match (n) detach delete n")

def build_origin(graph):
    origin_name = ["PhysicalEnvironment", "DynamicObject", "Human", "EventType", "Space", "Device", "Action", "PerceptionEvent"]
    for i in origin_name:
        node = Node("Concept", name=i, uuid=snowflake.client.get_guid())
        graph.create(node)
    
    origin_ralation = [["DynamicObject", "composeOf", "PhysicalEnvironment"],
                       ["Space", "composeOf", "PhysicalEnvironment"], 
                       ["EventType", "composeOf", "PhysicalEnvironment"],
                       ["Device", "composeOf", "PhysicalEnvironment"],
                       ["Action", "composeOf", "PhysicalEnvironment"],
                       ["PerceptionEvent", "composeOf", "PhysicalEnvironment"],
                       ["PerceptionEvent", "hasType", "EventType"],
                       ["Device", "hasAction", "Action"],
                       ["Device", "deployedIn", "Space"],
                       ["EventType", "relatedTo", "Device"],
                       ["EventType", "relatedTo", "DynamicObject"],
                       ["EventType", "occurIn", "Space"],
                       ["DynamicObject", "locatedAt", "Space"],
                       ["Human", "subclassOf", "DynamicObject"]]
    for i in origin_ralation:
        node_1 = graph.run("MATCH (n:Concept) WHERE n.name='" + i[0] + "' RETURN n").data()[0]['n']
        node_2 = graph.run("MATCH (n:Concept) WHERE n.name='" + i[2] + "' RETURN n").data()[0]['n']
        relationship = Relationship(node_1, i[1], node_2, relationID=snowflake.client.get_guid())
        graph.create(relationship)

def node_exist(name):
    return len(graph.run("MATCH (n:Concept) WHERE n.name='" + name + "' RETURN n").data()) > 0

def get_node_by_name(name):
    return graph.run("MATCH (n) WHERE n.name='" + name + "' RETURN n").data()[0]['n']

def get_concept_node(name):
    if not node_exist(name):
        node = Node("Concept", name=name, uuid=snowflake.client.get_guid())
        graph.create(node)
        return node
    return get_node_by_name(name)

def room_node_create(concept, data, name):
    property = data["property"]
    state = data["state"]
    return Node(concept, property=json.dumps(property), state=json.dumps(state), name=name, type=concept, uuid=snowflake.client.get_guid())

def device_node_create(concept, data, name):
    d_node = None
    if data.get("action") == None:
        d_node = Node(concept, property=json.dumps(data["property"]), state=json.dumps(data["state"]), name=name, type=concept, uuid=snowflake.client.get_guid())
    else: 
        actions = data["action"]
        d_node = Node(concept, action=json.dumps(data["action"]), property=json.dumps(data["property"]), state=json.dumps(data["state"]), name=name, type=concept, uuid=snowflake.client.get_guid())
        for i in actions:
            action_name = i
            if not node_exist(action_name):
                action_node = get_concept_node(action_name)
                Action = get_node_by_name("Action")
                graph.create(Relationship(action_node, "subclassOf", Action, relationID=snowflake.client.get_guid()))
            action_node = get_node_by_name(action_name)
            graph.create(Relationship(d_node, "hasAction", action_node, relationID=snowflake.client.get_guid()))
        
    concept_node = get_concept_node(concept)
    graph.create(Relationship(concept_node, "subclassOf", get_node_by_name("Device"), relationID=snowflake.client.get_guid()))
    graph.create(Relationship(d_node, "isA", concept_node, relationID=snowflake.client.get_guid()))
    return d_node


def buid_env(graph):
    graph.run("match (n) detach delete n")
    build_origin(graph)

    queue = []

    f = read_json_all(ENV_PATH)
    for i in f:
        concept_node = get_concept_node(i)
        graph.create(Relationship(concept_node, "subclassOf", get_node_by_name("Space"), relationID=snowflake.client.get_guid()))

        for j in f[i]:
            name = j
            room_node = room_node_create(i, f[i][j], name)
            

            graph.create(Relationship(room_node, "isA", concept_node, relationID=snowflake.client.get_guid()))

            if f[i][j]["adjacentTo"] != None:
                for k in f[i][j]["adjacentTo"].split():
                    a_name = k
                    queue.append([name, "adjacentTo", a_name])

            if f[i][j]["reachableTo"] != None:
                for k in f[i][j]["reachableTo"].split():
                    r_name = k
                    queue.append([name, "reachableTo", r_name])

            
            if f[i][j]["Device"] != None:
                for k in f[i][j]["Device"]:
                    d_name = k.split("_")[0]
                    d_node = device_node_create(k.split("_")[1], f[i][j]["Device"][k], d_name)
                    graph.create(Relationship(d_node, "deployedIn", room_node, relationID=snowflake.client.get_guid()))

    print(queue)
    for i in queue:
        print(i[0])
        node_1 = get_node_by_name(i[0])
        node_2 = get_node_by_name(i[2])
        relationship = Relationship(node_1, i[1], node_2, relationID=snowflake.client.get_guid())
        graph.create(relationship)


def build_event(graph, path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            eventType = get_node_by_name("EventType")
            for i in f:
                event_name = i.strip("\n")
                event_node = Node("Concept", name=event_name, uuid=snowflake.client.get_guid())
                graph.create(event_node)
                graph.create(Relationship(event_node, "subclassOf", eventType, relationID=snowflake.client.get_guid()))
    except:
        return None



if __name__ == '__main__':
    buid_env(graph)
    build_event(graph, EVENT_PATH)
                
