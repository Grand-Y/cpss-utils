from py2neo import Graph, Node, Relationship, NodeMatcher
import snowflake.client

#
# graph_local = Graph('http://localhost:7474', auth=('neo4j', '1234'))
# graph_server = Graph('http://10.177.29.226:7474', auth=('neo4j', '123456'))
# graph_xinhai = Graph('http://106.15.102.123:6102', auth=('neo4j', '123456'))
origin = ['Space', 'Action', 'Device', 'PhysicalEnvironment', 'DynamicObject', 'EventType']
Space = ['EntranceArea', 'LeisureArea', 'WorkArea', 'DiningArea']



def copy_concept(graph_1, graph_2):
    # 获取所有概念节点
    nodes_data_all = graph_1.run("MATCH (n:Concept) RETURN n").data()
    nodes_list = []
    for node in nodes_data_all:
        nodes_list.append(node['n']['name'])
    print(nodes_list)

    links_data_all = graph_1.run("MATCH (n:Concept)-[r]->(t:Concept) RETURN n, r, t").data()
    matcher = NodeMatcher(graph_2)
    concepts = []

    # node_1 = Node('Concept', name=links_data_all[0]['n']['name'], uuid=snowflake.client.get_guid())
    # node_2 = Node('Concept', name=links_data_all[0]['t']['name'], uuid=snowflake.client.get_guid())
    # relationship = type(links_data_all[0]['r']).__name__
    # print(relationship)
    # node_1_include_node_2 = Relationship(node_1, relationship, node_2, relationID=snowflake.client.get_guid())
    # graph_local.create(node_1_include_node_2)
    #
    for link in links_data_all:
        name_1 = link['n']['name']
        name_2 = link['t']['name']
        if name_1 in concepts:
            node_1 = matcher.match('Concept').where(name=name_1).first()
        else:
            node_1 = Node('Concept', name=name_1, uuid=snowflake.client.get_guid())
            concepts.append(name_1)
            graph_2.create(node_1)
        if name_2 in concepts:
            node_2 = matcher.match('Concept').where(name=name_2).first()
        else:
            node_2 = Node('Concept', name=name_2, uuid=snowflake.client.get_guid())
            concepts.append(name_2)
            graph_2.create(node_2)
        # node_2 = Node('Concept', name=link['t']['name'], uuid=snowflake.client.get_guid())
        relationship = type(link['r']).__name__
        print(name_1 + ' ' + relationship + ' ' + name_2)
        node_1_include_node_2 = Relationship(node_1, relationship, node_2, relationID=snowflake.client.get_guid())
        graph_2.create(node_1_include_node_2)

if __name__ == '__main__':
    # copy_concept()
    pass