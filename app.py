import argparse
import textwrap

from sql_communication import MSSQLHandler
from sql_generate import construct_sql
from utils import loadxlsx

def calculateSubpath(paths, connection):
    common = subpathCost(paths)
    cost = 0
    for pattern in common:
        for index, node in enumerate(pattern):
            nodeQuery = f"SELECT cost FROM Devices WHERE device_name = '{node}' AND is_source = 0 and is_destination = 0"
            result = connection.send_query(nodeQuery, True)
            
            # checks for out of range
            if result:
                nodeCost = result[0][0]
            else:
                nodeCost = 0
            
            if index > 0:
                prevNode = pattern[index - 1]
                pathQuery = f"SELECT cost FROM Conveyers WHERE $from_id = (SELECT $node_id FROM Devices WHERE device_name = '{node}') AND $to_id = (SELECT $node_id FROM Devices WHERE device_name = '{prevNode}')"
                pathCostResult = connection.send_query(pathQuery, True)
                if pathCostResult:
                    pathCost = pathCostResult[0][0]
                else:
                    # Assuming paths cost = 1 
                    pathCost = 1 
            else:
                pathCost = 0
            
            cost = cost + nodeCost + pathCost
    return (cost, common)


def subpathCost(paths):
    splitpaths = [path[0].split(',') for path in paths if path is not None]
    common = [splitpaths[0]]
    if len(splitpaths) > 1:
        allCommon = []
        for path in splitpaths[1:]:
            foundCommon = []
            for commonSet in common:
                for index, commonNode in enumerate(commonSet):
                    try:
                        foundInPath = path.index(commonSet[index])
                        if foundInPath < len(path) - 1:
                            if index == 0 and len(commonSet) > 1:
                                if path[foundInPath + 1] == commonSet[index + 1]:
                                        foundCommon.append(commonNode)
                            elif len(commonSet) > 1 and not index == len(commonSet) - 1:
                                if foundInPath == 0 and path[foundInPath + 1] == commonSet[index + 1]:
                                    foundCommon.append(commonNode)
                                elif path[foundInPath - 1] == commonSet[index - 1]:
                                    foundCommon.append(commonNode)
                                    if not path[foundInPath + 1] == commonSet[index + 1]:
                                        allCommon.append(foundCommon)
                                        foundCommon = []
                                elif path[foundInPath + 1] == commonSet[index + 1]:
                                    foundCommon.append(commonNode)
                            elif index == len(commonSet) - 1 :
                                if foundInPath > 0:
                                    if path[foundInPath - 1] == commonSet[index - 1]:
                                        foundCommon.append(commonNode)
                                        if foundCommon not in allCommon:
                                            allCommon.append(foundCommon)
                        else:
                            if index > 0 and commonSet[index - 1] == path[foundInPath - 1]:
                                foundCommon.append(commonNode)
                                if foundCommon not in allCommon:
                                    allCommon.append(foundCommon)
                                foundCommon = []
                        if index == len(commonSet)-1:
                            common = allCommon
                    except ValueError:
                        if index == len(commonSet)-1:
                            common = allCommon
                        foundCommon = []
    return common

def printReturn(results, connection) -> None:
    numdests = len(results)
    parsedresults = [[(results[value][bigvalue][0], results[value][bigvalue][1]) for value in range(0, numdests) if bigvalue < len(results[value])] for bigvalue in range(0, 5)]
    sortedList = []
    for result in parsedresults:
        if result:
            value = [result, calculateSubpath(result, connection)]
            if len(value[0]) > 1:
                cumulativeCost = 0
                index = 0
                for index, paths in enumerate(value[0]):
                    cumulativeCost += paths[1] - value[1][0]
                cumulativeCost += value[1][0]
            else:
                cumulativeCost = value[0][0][1]
            
            value.append(cumulativeCost)
            if len(sortedList) > 0:
                for index, listval in enumerate(sortedList):
                    if listval[2] > cumulativeCost:
                        sortedList.insert(index, value)
                        break
                    if index == len(sortedList)-1:
                        sortedList.append(value)
                        break
            else:
                sortedList.append(value)

    for index, row in enumerate(sortedList):
        if len(row[0]) > 0:
            print(f"\u001b[4;32mPath {index+1}\u001b[0m")
            totalcost, patterns = row[2], row[1][1]
            for path in row[0]:
                if path:
                    value = path[0]
                    value = value.replace(",", " -> ")
                    for pattern in patterns:
                        pattern = " -> ".join(pattern)
                        findpattern = value.find(pattern)
                        value =  value[:findpattern+ len(pattern)] + "\u001b[0m" + value[findpattern+len(pattern):]
                        value = value[:findpattern] + "\u001b[1;3m" + value[findpattern:]
                    if len(row[0]) > 1:
                        print(value + "\n\u001b[33mSubpath Cost: \u001b[35m" + str(path[1]) + "\u001b[0m")
                    else:
                        print(value)
            print("\u001b[33mTotal Path Cost: \u001b[35m" + str(totalcost) + "\u001b[0m\n")

def app() -> None:
    procedureCalls = []
    # Parse system arguments and their types
    parser = argparse.ArgumentParser(
        prog="Shortest Path Algorithm for Material Transportation",
        description="Calculates the shortest path in a graph of devices",
    )
    parser.add_argument("-dr", "--drop", help="Whether to drop the database tables", action='store_true')
    parser.add_argument("-tr", "--truncate", help="Whether to empty the database tables", action='store_true')
    parser.add_argument("-f", "--filepath", type=str, help="The filepath to an XLSX input file")
    parser.add_argument("-d", "--database", type=str, help="The database to query", default="graph_db")
    parser.add_argument("-s", "--start", type=str, help="The starting device for the path", default="")
    parser.add_argument("-e", "--end", type=str, nargs="*", help="The destination device for the path", default="")
    parser.add_argument(
        "-x", "--exclude", nargs="*", help="Any devices to be excluded from the path"
    )
    parser.add_argument(
        "-i", "--include", nargs="*", help="Any devices to be included to the path"
    )
    parser.add_argument(
        "-a", "--add", nargs="*", help="Add extra devices, use format Node,Node_Name,Source/Dest or Edge,Connect_From_Name,Connect_To_Name,Cost to add nodes"
    )
    parser.add_argument(
        "-c", "--cost", nargs="*", help="Update the cost of edges, use format Connect_From_Name,Connect_To_Name,Cost"
    )
    # Parse the entered arguments with the settings above into the arguments object
    arguments = parser.parse_args()

    print(f"\u001b[42mPATH 6 - Shortest Path Algorithm for Material Transportation\u001b[0m\n")

    # Establish a connection to SQL server
    connection = MSSQLHandler()
    connection.connect_to_mssql()

    if arguments.database:
        connection.send_query(f"USE {arguments.database};", False)

    if arguments.drop:
        connection.send_query(f"DROP TABLE Devices;", False)
        connection.send_query(f"DROP TABLE Conveyers;", False)
    
    if arguments.truncate:
        connection.send_query(f"TRUNCATE TABLE Devices;", False)
        connection.send_query(f"TRUNCATE TABLE Conveyers;", False)

    # Read XLSX and transform into Python class objects
    if arguments.filepath:
        deviceList = loadxlsx(arguments.filepath)
        table_query, node_query, edge_query = construct_sql(arguments.database, deviceList.nodedevice_list, deviceList.edgedevice_list)

        check_device_exists = connection.send_query(f"SELECT object_id FROM {arguments.database}.sys.tables WHERE name = 'Devices';", True)
        check_conveyer_exists = connection.send_query(f"SELECT object_id FROM {arguments.database}.sys.tables WHERE name = 'Conveyers';", True)
        if not (check_device_exists and check_conveyer_exists):
            connection.send_query(table_query, False)

        for query in [node_query, edge_query]:
            connection.send_query(query, False)
    
    if arguments.add:
        node_id_max = connection.get_column_max('Devices', 'node_id')[0][0]
        if not node_id_max:
            node_id_max = 0
        new_nodes = []
        new_edges = []
        for value in arguments.add:
            queryProps = value.split(',')
            if queryProps[0].upper() in ('NODE', 'N'):
                if queryProps[2].upper() in ('SOURCE', 'S'):
                    values = (node_id_max, queryProps[1],queryProps[3], 1, 0, 1)
                elif queryProps[2].upper() in ('DESTINATION', 'DEST','D'):
                    values = (node_id_max, queryProps[1],queryProps[3], 0, 1, 1)
                elif queryProps[2].upper() in ('PATH'):
                    values = (node_id_max, queryProps[1],queryProps[3], 0, 0, 1)
                node_id_max += 1
                new_nodes.append(values)
                send_query = f"INSERT INTO Devices VALUES {values}"
                connection.send_query(send_query, False)
            if queryProps[0].upper() in ('EDGE', 'E'):
                from_id = connection.send_query(f"SELECT node_id FROM Devices WHERE device_name = '{queryProps[1]}'", True)[0][0]
                to_id = connection.send_query(f"SELECT node_id FROM Devices WHERE device_name = '{queryProps[2]}'", True)[0][0]
                new_edges.append(f"((SELECT $node_id FROM Devices WHERE node_id = {from_id}), (SELECT $node_id FROM Devices WHERE node_id = {to_id}), {queryProps[3]})")
        if new_edges:
            send_query = f"INSERT INTO Conveyers VALUES "
            for edge in new_edges:
                if edge == new_edges[-1]:
                    send_query += f"{edge};"
                else:
                    send_query += f"{edge}, "
            connection.send_query(send_query, False)
    
    if arguments.cost:
        for value in arguments.cost:
            queryProps = value.split(',')
            if queryProps[0].upper() in ('EDGE', 'E'):
                query = f"UPDATE Conveyers SET cost = {queryProps[3]} WHERE Conveyers.$from_id = (SELECT Devices.$node_id FROM Devices WHERE device_name = '{queryProps[1]}') AND Conveyers.$to_id = (SELECT Devices.$node_id FROM Devices WHERE device_name = '{queryProps[2]}')"
                connection.send_query(query, False)
            elif queryProps[0].upper() in ('NODE', 'N'):
                query = f"UPDATE Conveyers SET cost = {queryProps[2]} WHERE Devices.device_name = '{queryProps[1]}')"
                connection.send_query(query, False)

    # Flip is_active for every excluded node
    if arguments.exclude:
        for value in arguments.exclude:
            connection.update_column('Devices', 'is_active', 0, 'device_name', value)

    # Flip is_active for every included node
    if arguments.include:
        for value in arguments.include:
            connection.update_column('Devices', 'is_active', 1, 'device_name', value)

    # Run the stored procedure
    if arguments.start:
        if arguments.end:
            for endpoint in arguments.end:
                procedureCalls.append(connection.call_procedure(
                    "GetShortestPath", [arguments.start, endpoint]
                ))
        else:
            procedureCalls.append(connection.call_procedure(
                    "GetShortestPath", [arguments.start, "!"]
                ))

    # Return the results in console
    if procedureCalls and (len(procedureCalls) > 0 and procedureCalls[0]):
        printReturn(procedureCalls, connection)
    elif len(procedureCalls) > 0 and (arguments.start or arguments.end):
        print("No path found")
    else:
        print("No return value")

    return


if __name__ == "__main__":
    app()
