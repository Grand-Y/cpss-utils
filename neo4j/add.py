from py2neo import Graph, Node, Relationship, NodeMatcher
import snowflake.client

#
# graph_local = Graph('http://localhost:7474', auth=('neo4j', '1234'))
graph_server2 = Graph('http://10.177.21.173:7474', auth=('neo4j', '123456'))
# graph_xinhai = Graph('http://106.15.102.123:6102', auth=('neo4j', '123456'))
origin = ['Space', 'Action', 'Device', 'PhysicalEnvironment', 'DynamicObject', 'EventType']
Space = ['EntranceArea', 'LeisureArea', 'WorkArea', 'DiningArea']
rooms = ['laboratory01', 'meetingroom01', 'meetingroom02', 'corridor01', 'tearoom01']

def add_seLab(graph):
    Space = graph.run("MATCH (n:Concept) WHERE n.name='Space' RETURN n").data()[0]['n']
    concept_node = Node('Concept', name='SeLab', uuid=snowflake.client.get_guid())
    se_lab = Node('SeLab', Property='', State='{"signed_in_count":0}', id='selab01', name='selab01', type='SeLab',
                                 uuid=snowflake.client.get_guid())
    graph.create(concept_node)
    graph.create(se_lab)
    relationship = Relationship(se_lab, 'isA', concept_node, relationID=snowflake.client.get_guid())
    graph.create(relationship)
    relationship = Relationship(concept_node, 'subclassOf', Space, relationID=snowflake.client.get_guid())
    graph.create(relationship)

    for i in rooms:
        room = graph.run("MATCH (n) WHERE n.name='" + i + "' RETURN n").data()[0]['n']
        graph.create(Relationship(room, 'contended', se_lab, relationID=snowflake.client.get_guid()))


def add_space(graph):
    Instance_num = [2, 1, 1, 5]
    matcher = NodeMatcher(graph)
    NMD = 10
    # a = 10
    # aaa = str(a) if a >= 10 else '0' + str(a)
    # print(aaa)

    for i in range(len(Space)):
        concept_node = matcher.match('Concept').where(name=Space[i]).first()
        type = concept_node['name']
        for j in range(Instance_num[i]):
            num = str(j + 1) if j >= 9 else '0' + str(j + 1)
            instance_node = Node(concept_node['name'], Property='', State='', id=type + num, name=type + num, type=type,
                                 uuid=snowflake.client.get_guid())
            graph.create(instance_node)
            relationship = Relationship(instance_node, 'isA', concept_node, relationID=snowflake.client.get_guid())
            graph.create(relationship)
    oncept_node = graph.run("MATCH (n:Concept) WHERE n.name='Action' RETURN n").data()[0]['n']

def add_device(graph):
    a = {'meetingroom01':{'Door':1, 'Window':1, 'TV':1},  
         'laboratory01':{'Door':1, 'Window':2}, 
         'tearoom01':{'Window':1, 'WaterDispenser':1}}
    b = {'meetingroom02':{'Door':1, 'Window':1, 'TV':1}}
    matcher = NodeMatcher(graph)
                                                
    for i in b:
        print(i)
        room = graph.run("MATCH (n) WHERE n.id='%s' RETURN n"%(i)).data()[0]['n']
        # room = matcher.match().where(name=j).first()
        for j in b.get(i):
            low = j.lower()
            concept_node = matcher.match('Concept').where(name=j).first()
            for k in range(0, b.get(i).get(j)):
                num = str(k + 1) if k >= 9 else '0' + '0' + str(k + 1)
                instance_node = Node(concept_node['name'], Property='', State='{"current_' + low + '_state" : "off"}', id=i + '_' + low + num, name=i + '_' + low + num, type=j,
                                    uuid=snowflake.client.get_guid())
                graph.create(instance_node)
                relationship = Relationship(instance_node, 'isA', concept_node, relationID=snowflake.client.get_guid())
                graph.create(relationship)
                relationship = Relationship(instance_node, 'deployedIn', room, relationID=snowflake.client.get_guid())
                graph.create(relationship)


def add_action(graph):
    action_list = ['Robot_Guiding', 'Make_Order', 'Make_Coffee', 'Deliver_Coffee', 'Clean_Table']
    concept_node = graph.run("MATCH (n:Concept) WHERE n.name='Action' RETURN n").data()[0]['n']

    graph.run("MATCH (n:Concept)-[r:subclassOf]->(nn) WHERE nn.name='Action' DETACH DELETE n")
    for i in action_list:
        instance_node = Node('Concept', name=i, uuid=snowflake.client.get_guid())
        graph.create(instance_node)
        relationship = Relationship(instance_node, 'hasAction', concept_node, relationID=snowflake.client.get_guid())
        graph.create(relationship)


def add_device2action(graph):
    d2c = {'Light':['Light_Turn_On', 'Light_Turn_Off'], 'AC':["AC_Turn_On", "AC_Turn_Off"], 'Speaker':['Speak_VoiceMessage']}

    for i in d2c:
        device_list = graph.run("MATCH (n:%s)-[r:isA]->(nn) WHERE nn.name='%s' RETURN n"%(i, i)).data()
        action_list = []
        for j in d2c.get(i):
            action_list.append(graph.run("MATCH (n:Concept) WHERE n.name='%s' RETURN n"%(j)).data()[0]['n'])
        for device in device_list:
            for action in action_list:
                relationship = Relationship(device['n'], 'hasAction', action, relationID=snowflake.client.get_guid())
                graph.create(relationship)



if __name__ == '__main__':
    # add_action(graph_xinhai)

    # add_device2action(graph_server)
    
    add_seLab(graph_server2)