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

def build_context(graph, state):
    context_node = Node("Space", name="Context")
    graph.create(context_node)
    for i in state:
        state_node = Node("ContextState", name=i, room="Context", value=state[i]["value"])
        graph.create(state_node)
        # state_node = get_node_by_name(i)
        graph.create(Relationship(context_node, "HAS", state_node))

        for j in state[i]["Action"]:
            action_node = Node("Action", name=j)
            graph.create(action_node)
            graph.create(Relationship(state_node, "CAN", action_node))

def node_exist(name):
    return len(graph.run("MATCH (n:Concept) WHERE n.name='" + name + "' RETURN n").data()) > 0

def get_node_by_name(name):
    return graph.run("MATCH (n) WHERE n.name='" + name + "' RETURN n").data()[0]['n']

def create_room_node(data, room_name):
    room_node = Node("Space", name=room_name)
    graph.create(room_node)
    # room_node = get_node_by_name(room_name)

    state = data["State"]
    for i in state:
        state_node = Node("EnvState", name=i, room=room_name, value=state[i]["value"])
        graph.create(state_node)
        # state_node = get_node_by_name(i)
        graph.create(Relationship(room_node, "HAS", state_node))

        for j in state[i]["Action"]:
            action_node = Node("Action", name=j)
            graph.create(action_node)
            graph.create(Relationship(state_node, "CAN", action_node))
    return room_node

def create_device_node(concept, data, name, room_name):
    actions = data["Action"]
    device_node = Node("Device", name=name, type=concept, state=data["state"])
    graph.create(device_node)
    for i in actions:
        action_name = i
        action_node = Node("Action", name=action_name)
        graph.create(action_node)
        graph.create(Relationship(device_node, "CAN", action_node))
        
        
        # print(actions[i]["Effect"]['name'])
        if len(actions[i]["Effect"]) == 0:
            continue
        if isinstance(actions[i]["Effect"], dict):
            print(actions[i]["Effect"]['name'])

            effect_name = actions[i]["Effect"]['name']
            pre_condition = actions[i]["Effect"]['PreCondition']
            effect_node = Node("Effect", name=effect_name, room=room_name, device=name, value=actions[i]["Effect"]['value'], pre_condition=pre_condition)
            graph.create(effect_node)
            graph.create(Relationship(action_node, "HAS", effect_node))

            if pre_condition == "":
                continue
            conditions = []
            if ">" in pre_condition:
                conditions = pre_condition.split(" > ")
            elif "<" in pre_condition:
                conditions = pre_condition.split(" < ")
            elif "=" in pre_condition:
                conditions = pre_condition.split(" = ")
            else:
                continue
                
            queue.append(effect_node, "DEPENDING_ON", conditions[0])
            queue.append(effect_node, "DEPENDING_ON", conditions[1])
        else :
            for j in actions[i]["Effect"]:
                print(j)

                effect_name = j['name']
                pre_condition =j['PreCondition']
                effect_node = Node("Effect", name=effect_name, room=room_name, device=name, value=j['value'], pre_condition=pre_condition)
                graph.create(effect_node)
                graph.create(Relationship(action_node, "HAS", effect_node))

                if pre_condition == "":
                    continue
                conditions = []
                if ">" in pre_condition:
                    conditions = pre_condition.split(" > ")
                elif "<" in pre_condition:
                    conditions = pre_condition.split(" < ")
                elif "=" in pre_condition:
                    conditions = pre_condition.split(" = ")
                else:
                    continue
                    
                queue.append([effect_node, "DEPENDING_ON", conditions[0]])
                queue.append([effect_node, "DEPENDING_ON", conditions[1]])
        

    return device_node

def buid_env(graph):
    graph.run("match (n) detach delete n")
    # build_origin(graph)

    f = read_json_all(ENV_PATH)
    for i in f:
        if i == "Context":
            build_context(graph, f[i]["State"])
            continue

        name = i
        room_node = create_room_node(f[i], name)

        if f[i]["adjacentTo"] != None:
            for k in f[i]["adjacentTo"]:
                a_name = k
                queue.append([name, "ADJACENT_TO", a_name])

        
        if f[i]["Device"] != None:
            for k in f[i]["Device"]:
                device_name = k.split("_")[0]
                device_node = create_device_node(k.split("_")[1], f[i]["Device"][k], device_name, name)
                graph.create(Relationship(device_node, "BELONG_TO", room_node))

    print(queue)
    for i in queue:
        if len(i[2].split(".")) == 1:
            node_1 = get_node_by_name(i[0])
            node_2 = get_node_by_name(i[2])
            relationship = Relationship(node_1, i[1], node_2)
            graph.create(relationship)
        else:
            print(i[2].split("."))
            print(graph.run("MATCH (m)-[r:HAS]->(n) WHERE m.name='" + i[2].split(".")[0] + "' and n.name='" + i[2].split(".")[1] + "' RETURN n").data()[0])
            node_1 = graph.run("MATCH (m)-[r:HAS]->(n) WHERE m.name='" + i[2].split(".")[0] + "' and n.name='" + i[2].split(".")[1] + "' RETURN n").data()[0]['n']
            relationship = Relationship(i[0], i[1], node_1)
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
    # delete_all(graph)
    buid_env(graph)
    # build_event(graph, EVENT_PATH)
                
