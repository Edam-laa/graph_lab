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

    def representatives(self):
        """Retourne le dict noeud → représentant courant (pour les steps)."""
        return {n: self.find(n) for n in self.parent}


# ─── Kruskal ───────────────────────────────────────────────────────────────────

def kruskal(graph):
    """
    Construit l'arbre couvrant minimum d'un graphe non orienté pondéré.

    Paramètres:
        graph (Graph) : instance de la classe Graph

    Retourne:
        dict avec :
            "mst_edges"    (list)        : arêtes du MST [(u, v, poids), ...]
            "total_weight" (int/float)   : poids total du MST
            "steps"        (list)        : étapes numérotées de l'algorithme

    Lève:
        ValueError : si le graphe est orienté ou non connexe
    """
    '''
    # ---------------------------
    # VALIDATION
    # ---------------------------
    if graph.directed:
        raise ValueError("Kruskal only works on undirected graphs.")
    '''
    nodes = graph.get_nodes()

    if not nodes:
        raise ValueError("Graph is empty.")

    for u, v, w, c in graph.get_edges():
        if u == v:
            raise ValueError("Graph contains self-loops.")

    # ---------------------------
    # INITIALIZATION
    # ---------------------------
    # get_edges() retourne (u, v, weight, capacity) → tri par poids
    edges        = sorted(graph.get_edges(), key=lambda e: e[2])
    uf           = UnionFind(nodes)
    steps        = []
    mst_edges    = []
    total_weight = 0
    total_edges  = len(edges)

    steps.append(
        f"[Init] {len(nodes)} noeuds | {total_edges} aretes triees par poids : "
        f"{[(u, v, w) for u, v, w, c in edges]}"
    )

    # ---------------------------
    # MAIN LOOP
    # ---------------------------
    for i, (u, v, w, c) in enumerate(edges, start=1):
        if uf.union(u, v):
            # Pas de cycle → on ajoute l'arête
            mst_edges.append((u, v, w))
            total_weight += w
            steps.append(
                f"[{i}/{total_edges}] ADD    ({u}-{v}, w={w}) "
                f"| MST={len(mst_edges)} aretes "
                f"| total_weight={total_weight} "
                f"| representants={uf.representatives()}"
            )

            if len(mst_edges) == len(nodes) - 1:
                steps.append(
                    f"[{i}/{total_edges}] MST COMPLET : {len(nodes) - 1} aretes atteintes."
                )
                break
        else:
            steps.append(
                f"[{i}/{total_edges}] SKIP   ({u}-{v}, w={w}) → cycle detecte "
                f"| representants={uf.representatives()}"
            )

    # ---------------------------
    # VALIDATION CONNEXITÉ
    # ---------------------------
    if len(mst_edges) < len(nodes) - 1:
        raise ValueError("Graph is not connected: MST is impossible.")

    # ---------------------------
    # RÉCAPITULATIF FINAL
    # ---------------------------
    steps.append(
        f"[Final] MST = {mst_edges} | poids total = {total_weight}"
    )

    # ---------------------------
    # RETURN RESULT
    # ---------------------------
    return {
        "mst_edges":    mst_edges,
        "edges":        mst_edges,
        "total_weight": total_weight,
        "steps":        steps
    }