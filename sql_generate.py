def construct_sql(graph_name=None, nodes=None, edges=None):
    '''
    Converts a list of nodes and edges into an SQL query that creates and populates node and edge tables.

    Args:
        nodes (list[Node]): The nodes for the graph.
        edges (list[Edge]): The edges of the graph.
    
    Returns:
        str: The table creation query and the node/edge table population queries.
    ''' 
    return_graph: list = []

    if graph_name:
      base_query: str = f"""
      CREATE TABLE Devices (
      node_id INTEGER PRIMARY KEY,
      device_name VARCHAR(8000),
      cost INT,
      is_source BIT,
      is_destination BIT,
      is_active BIT
      ) AS NODE;

      CREATE TABLE Conveyers (
      cost INT
      ) AS EDGE;
      """
      return_graph.append(base_query)

    if nodes:
        node_cumulative: list = [f"({node.node_id}, '{node.device_name}', {int(node.cost)}, {int(node.is_source)}, {int(node.is_destination)}, 1)" for node in nodes]
        node_delimited: str = ", ".join(node_cumulative)
        node_insert_query: str = f"INSERT INTO Devices (node_id, device_name, cost, is_source, is_destination, is_active) VALUES {node_delimited};"
        return_graph.append(node_insert_query)

    if edges:
        edge_cumulative = []
        for edge in edges:
          edge_cf = next((node for node in nodes if node.device_name == edge.connect_from), None)
          edge_ct = next((node for node in nodes if node.device_name == edge.connect_to), None)
          edge_cumulative.append(f"((SELECT $node_id FROM Devices WHERE node_id = {edge_cf.node_id}), (SELECT $node_id FROM Devices WHERE node_id = {edge_ct.node_id}), {edge.cost})")
        edge_delimited: str = ", ".join(edge_cumulative)
        edge_insert_query: str = f"INSERT INTO Conveyers VALUES {edge_delimited};"
        return_graph.append(edge_insert_query)

    return return_graph
