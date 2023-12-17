import openpyxl

class device:
    def __init__(self,list1,list2):
        self.nodedevice_list=list1
        self.edgedevice_list=list2

class Node:
    def __init__(self, id, name, source, destination, cost = 1, is_active=True):
        self.is_active=is_active
        self.node_id = id
        self.device_name = name
        self.is_source = source
        self.is_destination = destination
        self.cost = cost

class Edge:
    def __init__(self, id, c_from, c_to, cost = 1):
        self.eid = id
        self.connect_from = c_from
        self.connect_to = c_to
        self.cost = cost

def edge_exist_checker(edgelist, c_f_or_t, name):#CHECKS FOR EXISTING EDGES
    return any(edge.connect_from == c_f_or_t and edge.connect_to == name or
               edge.connect_from == name and edge.connect_to == c_f_or_t for edge in edgelist)

def node_exist_checker(nodelist, name):# CHECKS FOR EXISTING NODES
    return any(node.device_name == name for node in nodelist)

def loadxlsx(path:str):
    wb = openpyxl.load_workbook(path)
    sheet = wb.active

    node_list=[]
    edge_list=[]
    device_list=device(node_list,edge_list) #CREATRING DEVICE LIST OBJECT
    id = -1 #NODE ID
    eid = 0 #EDGE ID
    #GETTING THE CELL VALUE FROM THE EXCEL
    for row in sheet.iter_rows(values_only=True):
        i = 0
        for cell_value in row:
            if i == 0:
                if cell_value == "Plant Item":
                    name = None
                elif not node_exist_checker(device_list.nodedevice_list, cell_value):
                    name = cell_value
                    id += 1
            if i == 1:
                source = cell_value
            if i == 2:
                destination = cell_value
            if i == 3:
                cf = cell_value
            if i == 4:
                ct = cell_value
            i += 1
        #CREATING THE NODE AND EDGE OBJECTS APPEDINNG THEM TO THE DEVICELIST IN EDGE LIST AND NODE LIST  
        if name is not None:# CHECKS FOR BLANKS FROM EXCEL
            if not node_exist_checker(device_list.nodedevice_list, name):
                device_list.nodedevice_list.append(Node(id, name, source, destination))
            if cf != None and not edge_exist_checker(device_list.edgedevice_list, cf, name):
                device_list.edgedevice_list.append(Edge(eid, cf, name))
                eid += 1
            if ct != None and not edge_exist_checker(device_list.edgedevice_list, ct, name):
                device_list.edgedevice_list.append(Edge(eid, name, ct))
                eid += 1
    return device_list
