class Link:
    def __init__(self, ltype, node1, node2):
        self.name = None
        self.type = ltype

        self.node1 = node1["node"]
        self.intf1 = node1["interface"]

        self.node2 = node2["node"]
        self.intf2 = node2["interface"]

    def get_name(self):
        return self.name

    def get_link_type(self):
        return self.type

    def get_node1(self):
        return self.node1

    def get_intf1(self):
        return self.intf1

    def get_node2(self):
        return self.node2

    def get_intf2(self):
        return self.intf2

    def create(self):
        pass
