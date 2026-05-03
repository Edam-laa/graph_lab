'''import time

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

    # ---------------------------
    # ÉVALUATION TEMPS + COMPLEXITÉ
    # ---------------------------
    def evaluate_algorithm(self, algo_name, *args):
        start_time = time.time()

        if algo_name == "Dijkstra":
            result = self.dijkstra(*args)
            complexity = "O(V^2 log V) (matrice)"

        else:
            return None, "Algorithme non implémenté"

        end_time = time.time()
        exec_time = end_time - start_time

        return {
            "result": result,
            "execution_time": exec_time,
            "complexity": complexity
        }

    # ---------------------------
    # AFFICHAGE RÉSULTATS
    # ---------------------------
    def display_results(self, evaluation):
        print("Résultat :", evaluation["result"])
        print("Temps d’exécution :", evaluation["execution_time"], "secondes")
        print("Complexité :", evaluation["complexity"])


graph = [
    [0, 2, 0, 6],
    [2, 0, 3, 8],
    [0, 3, 0, 0],
    [6, 8, 0, 0]
]
g=Graph()'''
class Graph:
    def __init__(self, directed=False):
        self.directed = directed
        self.nodes = set()
	# {node: [(neighbor, weight, capacity)]}
        self.adj_list = {}

    # ---------------------------
    # ADD NODES & EDGES
    # ---------------------------

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.add(node)
            self.adj_list[node] = []

    def add_edge(self, u, v, weight=1,capacity=None):
        self.add_node(u)
        self.add_node(v)

        self.adj_list[u].append((v, weight,capacity))

        if not self.directed:
            self.adj_list[v].append((u, weight,capacity))

    # ---------------------------
    # ACCESS METHODS
    # ---------------------------
    def get_neighbors(self, node):
        return self.adj_list.get(node, [])
    def get_all_adjacent(self, node):
        """
        Returns all nodes connected to this node, 
        ignoring direction. Crucial for Welsh-Powell.
        """
        adjacent = set()
        # Outgoing
        for v, w, c in self.adj_list.get(node, []):
            adjacent.add(v)
        
        # Incoming (We have to scan the whole graph)
        if self.directed:
            for u in self.adj_list:
                for v, w, c in self.adj_list[u]:
                    if v == node:
                        adjacent.add(u)
        
        return list(adjacent)
    def get_nodes(self):
        return sorted(self.nodes)

    def get_edges(self):
        edges = []
        seen = set()
        for u in self.adj_list:
            for v, w,c in self.adj_list[u]:
                edge=(u, v, w,c)
                if self.directed:
                    edges.append(edge)
                else:
                    key = (tuple(sorted((u, v))), w, c) if u != v else ((u, u), w, c)
                    if key not in seen:
                        edges.append(edge)
                        seen.add(key)
        return edges

    # ---------------------------
    # VALIDATION HELPERS
    # ---------------------------
    def has_negative_weights(self):
        for u in self.adj_list:
            for v, w,c in self.adj_list[u]:
                try:
                    if float(w) < 0:
                        return True
                except (TypeError, ValueError):
                    return False
        return False

    def is_weighted(self):
        for u in self.adj_list:
            for v, w,c in self.adj_list[u]:
                if w != 1:
                    return True
        return False
    def has_capacity(self):
        for u in self.adj_list:
            for v, _, c in self.adj_list[u]:
                if c is not None:
                    return True
        return False
    def degree(self, node):
        return len(self.adj_list.get(node, []))    
'''  "graph": {
    "nodes": ["A", "B", "C"],
    "edges": [
      {
        "id": "e1",
        "from": "A",
        "to": "B",
        "weight": 1,
        "capacity": null
      }
    ],
    "directed": true,
    "metadata": {
      "name": "Example Graph",
      "description": "Any graph type",
      "allow_negative_weights": false
    }
  },

  "algorithm": {
    "name": "dijkstra",
    "category": "shortest_path",

    "params": {
      "source": "A",
      "target": "C",
      "start": null,
      "end": null,
      "k": null
    },

    "constraints_check": {
      "requires_positive_weights": true,
      "requires_connected": false,
      "requires_dag": false
    }
  },

  "execution": {
    "execution_time": null,
    "complexity": null
  },
  "result": {
    "type": null,

    "distances": {},
    "path": [],
    "paths": {},

    "mst_edges": [],
    "components": [],
    "cycles": [],

    "eulerian_path": [],
    "eulerian_circuit": [],

    "coloring": {
      "node_colors": {},
      "edge_colors": {}
    },

    "max_flow": null,

    "steps": []
  },

  "options": {
    "return_path": true,
    "return_steps": true,
    "measure_time": true,
    "visualize": true
  }
}  '''