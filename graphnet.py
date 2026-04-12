class Node:
    def __init__(self, id):
        self.id = id

class Edge:
    def __init__(self, source, target, weight=None):
        self.source = source
        self.target = target
        self.weight = weight

class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)
