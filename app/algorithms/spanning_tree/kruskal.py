# kruskal.py
"""
Algorithme de Kruskal — Arbre Couvrant Minimum (MST)
Style uniforme avec les autres algorithmes de l'équipe.
"""


# ─── Union-Find ────────────────────────────────────────────────────────────────

class UnionFind:
    def __init__(self, nodes):
        self.parent = {n: n for n in nodes}
        self.rank   = {n: 0 for n in nodes}

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False  # même groupe → cycle détecté
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


# ─── Kruskal ───────────────────────────────────────────────────────────────────

def kruskal(graph):
    """
    Construit l'arbre couvrant minimum d'un graphe non orienté pondéré.

    Paramètres:
        graph (Graph) : instance de la classe Graph

    Retourne:
        dict avec :
            "mst_edges" (list)       : arêtes du MST [(u, v, poids), ...]
            "total_weight" (int/float) : poids total du MST
            "steps" (list)           : étapes de l'algorithme

    Lève:
        ValueError : si le graphe est orienté ou non connexe
    """
    # ---------------------------
    # VALIDATION
    # ---------------------------
    if graph.directed:
        raise ValueError("Kruskal only works on undirected graphs.")

    nodes = graph.get_nodes()

    if not nodes:
        raise ValueError("Graph is empty.")

    # ---------------------------
    # INITIALIZATION
    # ---------------------------
    # get_edges() retourne (u, v, weight, capacity) → tri par poids
    edges  = sorted(graph.get_edges(), key=lambda e: e[2])
    uf     = UnionFind(nodes)
    steps  = []

    mst_edges    = []
    total_weight = 0

    steps.append(f"Edges sorted by weight: {[(u, v, w) for u, v, w, c in edges]}")

    # ---------------------------
    # MAIN LOOP
    # ---------------------------
    for u, v, w, c in edges:
        if uf.union(u, v):
            # Pas de cycle → on ajoute l'arête
            mst_edges.append((u, v, w))
            total_weight += w
            steps.append(f"Add edge ({u}–{v}, weight={w}) → no cycle")

            if len(mst_edges) == len(nodes) - 1:
                steps.append(f"MST complete: {len(nodes)-1} edges reached.")
                break
        else:
            steps.append(f"Skip edge ({u}–{v}) → would create a cycle")

    # ---------------------------
    # VALIDATION CONNEXITÉ
    # ---------------------------
    if len(mst_edges) < len(nodes) - 1:
        raise ValueError("Graph is not connected: MST is impossible.")

    # ---------------------------
    # RETURN RESULT
    # ---------------------------
    return {
        "mst_edges":    mst_edges,
        "total_weight": total_weight,
        "steps":        steps
    }