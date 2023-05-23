from json.tool import main
from py2neo import Graph, Node, Relationship, NodeMatcher
# import snowflake.client
import json

#
# graph_local = Graph('http://localhost:7474', auth=('neo4j', '1234'))
# graph_server = Graph('http://10.177.29.226:7474', auth=('neo4j', '123456'))
graph_server2 = Graph('http://10.177.21.173:7474', auth=('neo4j', '123456'))
# graph_xinhai = Graph('http://106.15.102.123:6102', auth=('neo4j', '123456'))
origin = ['Space', 'Action', 'Device', 'PhysicalEnvironment', 'DynamicObject', 'EventType']
Space = ['EntranceArea', 'LeisureArea', 'WorkArea', 'DiningArea']


def get_room_device_id(graph):
    room_node = []
    device_node = []
    space_concept_all = graph.run("MATCH (n:Concept)-[r:subclassOf]->(nn) WHERE nn.name='Space' RETURN n").data()
    device_concept_all = graph.run("MATCH (n:Concept)-[r:subclassOf]->(nn) WHERE nn.name='Device' RETURN n").data()

    print(space_concept_all)

    for i in space_concept_all:
        rooms = graph.run("MATCH (n)-[r:isA]->(nn) WHERE nn.name='%s' RETURN n"%(i['n']['name'])).data()
        for j in rooms:
            room_node.append(j['n']['id'])

    for i in device_concept_all:
        devices = graph.run("MATCH (n)-[r:isA]->(nn) WHERE nn.name='%s' RETURN n"%(i['n']['name'])).data()
        for j in devices:
            device_node.append(j['n']['id'])

    print(room_node)
    print(device_node)


    with open('x2_room_device.txt', 'a') as file:
        for i in room_node:
            file.writelines(i + "\n")
        for i in device_node:
            file.writelines(i + "\n")


def get_device(graph):
    device_node = []
    device_concept_all = graph.run("MATCH (n:Concept)-[r:subclassOf]->(nn) WHERE nn.name='Device' RETURN n").data()
    for i in device_concept_all:
        devices = graph.run("MATCH (n)-[r:isA]->(nn) WHERE nn.name='%s' RETURN n"%(i['n']['name'])).data()

        for j in devices:
            device = Device(j['n']['id'], property=j['n']['Property'], state=j['n']['State'])
            device_node.append(device)

    
    for i in device_node:
        print(i.id, i.property, i.state)
    
def get_eventType(graph):
    events = graph.run("MATCH (n:Concept)-[r:subclassOf]->(nn) WHERE nn.name='EventType' RETURN n").data()
    with open('x2_eventType.txt', 'a') as file:
        for i in events:
            file.writelines(i['n']['name'] + "\n")
        
    
class Device():
    def __init__(self, id, property, state):
        self.id = id
        self.property = property
        self.state = state


if __name__ == '__main__':
    # get_room_device_id()

    # get_device(graph_server2)
    get_eventType(graph_server2)