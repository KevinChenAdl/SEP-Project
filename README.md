
To install dependencies, in your CLI write:
```
pip install -r requirements.txt
```

# How to run

You will need to have a local MSSQL instance running on your computer with the TCP/IP for IPAll set to 1433.
To run the program, in your CLI write:
```
python app.py [-dr / --drop] [-tr / --truncate] [-f / --filepath FILEPATH] [-d / --database DATABASE] [-s / --start START NODE] [-e / --end [END NODES]] [-x / --exclude [EXCLUDED NODES]] [-i / --include [INCLUDED NODES]] [-a / --add [ADDED NODES]] [-c / --cost [COST CHANGES]]
```
| Argument/Flag | Expected Input | Effect |
| -------- | -------------- | ---- |
| -dr --drop | Optional. None. | Will drop Devices and Conveyers tables in the current database.
| -tr --truncate  | Optional. None. | Will truncate data from Devices and Conveyers tables in the current database.
| -f --filepath | Optional. The name of an XLSX file to parse from. If not added pre-existing data in the database will be used. | Will parse and input data from file into Devices and Conveyers.
| -d --database | Optional. Defaults to `graph_db`. The name of a database on the MSSQL Server. | Will use a MSSQL 2022 database of a specified name |
| -s --start | The name of the start device for the path. | Sets the starting destination to a specified node.
| -e --end | Optional. The name of the end device for the path. If not added then all potential destinations will be checked. If split with a space, the program will explore potential subpaths (eg. `-e DEST1 DEST2`). If split with a comma, the 5 shortest paths from the potential end points will be explored (eg. `-e DEST1,DEST2`) | Sets the end points to a specific node or set of nodes. |
| -x --exclude | Optional. The names of any nodes to be ignored by the path search separated by spaces. | Disables specific nodes from being searched through until they are included again.
| -i --include | Optional. The names of any nodes to un-exclude. | Re-includes nodes to the path search. |
| -a --add | Optional. A new node or edge to be added. For nodes use the format `NODE,[Name],[Souce/Path/Destination],[Cost]` and for edges use `EDGE,[From],[To],[Cost]`. | Adds new nodes or edges to the specified database. |
| -c --cost | Optional. Changes the cost of nodes or edges. For nodes use `NODE,[Name],[Cost]` and for edges use `EDGE,[From],[To],[Cost]` | Updates the cost of nodes and edges. |


# How to use Testing Suite
1. You must have a database called test_case on your local MSSQL server that has no tables.
2. You must have the GetShortestPath procedure stored on your test_case database
3. Modify test_cases.json to include your test case properties. Copy the schema of the example test cases and append it to the end of the root tests array.
4. To run the test, in your CLI write:
```
python test.py
```
Here is the test case schema:
```
{
    "name": "Test Name",
    "description": "Test Description",
    "input-nodes": [
        [Node ID, "Node Name", Is Source, Is Destination, Cost]
    ],
    "input-edges": [
        [From ID, To ID, Cost]
    ],
    "start-node": "Start Node Name",
    "end-node": "End Node Name",
    "excluded-nodes": [Names of Excluded Nodes],
    "expected": [
        ["Expected path 1, delimited by commas", Path Length],
        ["Expected path 2, delimited by commas", Path Length],
        ...
        ["Expected path 5, delimited by commas", Path Length]
    ]
},```
