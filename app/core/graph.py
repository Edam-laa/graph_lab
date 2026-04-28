'''import time

class Graph:
    def __init__(self, directed=False):
        self.directed = directed
        self.adj_matrix = []
        self.inc_matrix = []
        self.num_vertices = 0

    # ---------------------------
    # INITIALISATION DU GRAPHE
    # ---------------------------
    def load_from_adjacency_matrix(self, matrix):
        self.adj_matrix = matrix
        self.num_vertices = len(matrix)
        self._build_incidence_matrix()

    # ---------------------------
    # MATRICE D’INCIDENCE
    # ---------------------------
    def _build_incidence_matrix(self):
        edges = []
        n = self.num_vertices

        for i in range(n):
            for j in range(n):
                if self.adj_matrix[i][j] != 0:
                    if self.directed or i < j:
                        edges.append((i, j))

        self.inc_matrix = [[0 for _ in range(len(edges))] for _ in range(n)]

        for k, (u, v) in enumerate(edges):
            if self.directed:
                self.inc_matrix[u][k] = -1
                self.inc_matrix[v][k] = 1
            else:
                self.inc_matrix[u][k] = 1
                self.inc_matrix[v][k] = 1

    # ---------------------------
    # AFFICHAGE
    # ---------------------------
    def display_adjacency_matrix(self):
        print("Matrice d’adjacence :")
        for row in self.adj_matrix:
            print(row)

    def display_incidence_matrix(self):
        print("Matrice d’incidence :")
        for row in self.inc_matrix:
            print(row)

    # ---------------------------
    # COMPATIBILITÉ DES ALGOS
    # ---------------------------
    def available_algorithms(self):
        algos = []

        if self._has_positive_weights():
            algos.append("Dijkstra")

        if not self.directed:
            algos.append("Prim")
            algos.append("Kruskal")

        algos.append("Bellman-Ford")  # toujours valide

        return algos

    def _has_positive_weights(self):
        for row in self.adj_matrix:
            for w in row:
                if w < 0:
                    return False
        return True

    # ---------------------------
    # DIJKSTRA
    # ---------------------------
    def dijkstra(self, start):
        import heapq

        n = self.num_vertices
        dist = [float('inf')] * n
        dist[start] = 0

        pq = [(0, start)]

        while pq:
            d, u = heapq.heappop(pq)

            if d > dist[u]:
                continue

            for v in range(n):
                weight = self.adj_matrix[u][v]
                if weight != 0:
                    new_d = d + weight
                    if new_d < dist[v]:
                        dist[v] = new_d
                        heapq.heappush(pq, (new_d, v))

        return dist

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

    def get_nodes(self):
        return sorted(self.nodes)

    def get_edges(self):
        edges = []
        seen = set()
        for u in self.adj_list:
            for v, w,c in self.adj_list[u]:
                edge=(u, v, w,c)
                reverse=(v, u, w,c)
                if self.directed or reverse not in seen:
                    edges.append(edge)
                    seen.add(edge)
        return edges

    # ---------------------------
    # VALIDATION HELPERS
    # ---------------------------
    def has_negative_weights(self):
        for u in self.adj_list:
            for v, w,c in self.adj_list[u]:
                if w < 0:
                    return True
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