import json

class Graph:
    def __init__(self, json_file):
        self.nodes = []
        self.node_index = {}   # Map node -> index
        self.matrix = []
        self.directed = False

        self._load_from_json(json_file)
        self._build_matrix()

    def _load_from_json(self, json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)

        self.nodes = data.get("nodes", [])
        self.edges = data.get("edges", [])
        self.directed = data.get("directed", False)

        # Create index mapping
        self.node_index = {node: i for i, node in enumerate(self.nodes)}

    def _build_matrix(self):
        n = len(self.nodes)

        # Initialize matrix with infinity (no edge)
        self.matrix = [[float('inf')] * n for _ in range(n)]

        # Distance to self = 0
        for i in range(n):
            self.matrix[i][i] = 0

        # Fill matrix
        for edge in self.edges:
            u = edge["from"]
            v = edge["to"]
            w = edge.get("weight", 1)

            i = self.node_index[u]
            j = self.node_index[v]

            self.matrix[i][j] = w

            if not self.directed:
                self.matrix[j][i] = w

    def display(self):
        print("Adjacency Matrix:")
        print("   ", "  ".join(self.nodes))
        for i, row in enumerate(self.matrix):
            print(self.nodes[i], row)

    def get_weight(self, u, v):
        i = self.node_index[u]
        j = self.node_index[v]
        return self.matrix[i][j]

    def add_edge(self, u, v, weight=1):
        i = self.node_index[u]
        j = self.node_index[v]

        self.matrix[i][j] = weight
        if not self.directed:
            self.matrix[j][i] = weight

    def __str__(self):
        result = "Adjacency Matrix:\n"
        result += "   " + "  ".join(self.nodes) + "\n"
        for i, row in enumerate(self.matrix):
            result += f"{self.nodes[i]} {row}\n"
        return result