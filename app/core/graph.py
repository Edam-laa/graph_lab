import json
import numpy as np


class Graph:
    def __init__(self, json_path):
        self.json_path = json_path

        # Primary structure (SOURCE OF TRUTH)
        self.adj_list = {}  # node -> list of (neighbor, weight)

        # Helper structures
        self.nodes = []
        self.node_index = {}

        # Cached matrix
        self._adj_matrix = None

        self._load_from_json()

    # ----------------------------
    # Load graph into adjacency list
    # ----------------------------
    def _load_from_json(self):
        with open(self.json_path, "r") as f:
            data = json.load(f)

        self.nodes = data["nodes"]
        self.node_index = {node: i for i, node in enumerate(self.nodes)}

        # init empty adjacency list
        self.adj_list = {node: [] for node in self.nodes}

        for e in data["edges"]:
            u = e["from"]
            v = e["to"]
            w = e.get("weight", 1)

            self.adj_list[u].append((v, w))

            # If undirected graph, uncomment:
            # self.adj_list[v].append((u, w))

    # ----------------------------
    # Primary operations on adjacency list
    # ----------------------------
    def add_edge(self, u, v, w=1):
        self.adj_list[u].append((v, w))
        self._adj_matrix = None  # invalidate cache

    def add_node(self, node):
        if node not in self.adj_list:
            self.adj_list[node] = []
            self.nodes.append(node)
            self.node_index = {n: i for i, n in enumerate(self.nodes)}
            self._adj_matrix = None

    # ----------------------------
    # Lazy adjacency matrix (cached)
    # ----------------------------
    def get_adjacency_matrix(self):
        if self._adj_matrix is not None:
            return self._adj_matrix

        n = len(self.nodes)
        mat = np.zeros((n, n))

        for u in self.adj_list:
            for v, w in self.adj_list[u]:
                i = self.node_index[u]
                j = self.node_index[v]
                mat[i][j] = w

        self._adj_matrix = mat
        return mat

    # ----------------------------
    # Optional utility
    # ----------------------------
    def print_adj_list(self):
        for node, neighbors in self.adj_list.items():
            print(node, "->", neighbors)

    def print_matrix(self):
        print(self.get_adjacency_matrix())