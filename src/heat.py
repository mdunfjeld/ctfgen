from collections import OrderedDict

class Router(object):
    subnets = []
    def __init__(self, data):
        self.data = data
        self.structure = OrderedDict()
       # self.router_count = num_of_routers()
       # self.node_count = num_of_nodes()
      
        
        self.subnet_count = len(data['properties']['networks'])

    def create_subnets(self):
        for i in self.data['properties']['networks'].keys():
            i = {i: {}}
            self.subnets.append(i)
        print(self.subnets)

    def num_of_routers(self):
        pass

    def foo(self):
        print(self.data)

    def change_subnet_address(self):
        pass


class Node(object):
    #flavor_= 
    def __init__(self, data):
        self.data = data
        self.structure = OrderedDict()
        #self.flavor = 
        #self.os = 
        #self.floating_ip = True
    def foo(self):
        print(self.data)