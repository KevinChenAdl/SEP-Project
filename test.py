import json

from sql_generate import construct_sql
from sql_communication import MSSQLHandler
from utils import Node,Edge


def result_tuple_to_list(returnval):
    '''
    Converts all tuples in a resulting SQL dataset to lists.

    Args:
        list[tuple(str)]: The raw dataset return values
    
    Returns:
        list[list[str]]: The converted dataset
    '''
    newval = [[value[0], value[1]] for value in returnval]
    return newval

def list_to_node(deviceList: list):
    cumulativeList = []
    for device in deviceList:
        cumulativeList.append(Node(device[0], device[1], device[2], device[3], cost=device[4]))
    return cumulativeList

def list_to_edge(edgeList: list):
    cumulativeList = []
    for index, edge in enumerate(edgeList):
        cumulativeList.append(Edge(index, edge[0], edge[1], edge[2]))
    return cumulativeList

def querytest_app():
    file = open("test_cases.json")
    testCases = json.loads(file.read())

    connection = MSSQLHandler()
    connection.connect_to_mssql()
    try:
        connection.send_query(f"USE test_case", False)
    except:
        print("Cannot connect to the test_case database. Be sure you have this database created in your local MSSQL server.")
        return
    
    clear_tables = """
    IF NOT EXISTS (SELECT 'X' FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Devices')
        CREATE TABLE Devices (node_id INTEGER PRIMARY KEY, device_name VARCHAR(8000), cost INT, is_source BIT, is_destination BIT, is_active BIT) AS NODE;
    IF NOT EXISTS (SELECT 'X' FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Conveyers')
        CREATE TABLE Conveyers (cost INT) AS EDGE;
    """
    empty_table = """
    TRUNCATE TABLE Devices;
    TRUNCATE TABLE Conveyers;
    """ 

    connection.send_query(clear_tables, False)

    for case in testCases["tests"]:
        print(f"-----------\n{case['name']}\n{case['description']}")
        connection.send_query(empty_table, False)

        test_nodes = list_to_node(case["input-nodes"])
        test_edges = list_to_edge(case["input-edges"])
        
        node_query, edge_query = construct_sql(nodes=test_nodes, edges=test_edges)
        connection.send_query(node_query, False)
        connection.send_query(edge_query, False)

        for node in case["excluded-nodes"]:
            connection.update_column('Devices', 'is_active', 0, 'device_name', node)

        returnval = connection.call_procedure("GetShortestPath", [case["start-node"], case["end-node"]])
        returnval = result_tuple_to_list(returnval)

        if returnval != case['expected']:
            print("Test failed! Incorrect return value")
            print("\n+ Expected:")
            print(case['expected'])
            print("\n")
            print("- Actual:")
            print(returnval)
            print("\n")
        else:
            print("Test passed!")
            
    connection.send_query(empty_table, False)
    return

if __name__ == "__main__":
    querytest_app()