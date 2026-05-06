# prim.py
"""
Algorithme de Prim — Arbre Couvrant Minimum (MST)
Style uniforme avec les autres algorithmes de l'équipe.
"""

import heapq


def prim(graph, start=None):
    """
    Construit l'arbre couvrant minimum d'un graphe non orienté pondéré.

    Paramètres:
        graph (Graph) : instance de la classe Graph
        start         : sommet de départ (premier sommet si None)

    Retourne:
        dict avec :
            "mst_edges"    (list)        : arêtes du MST [(u, v, poids), ...]
            "total_weight" (int/float)   : poids total du MST
            "steps"        (list)        : étapes de l'algorithme

    Lève:
        ValueError : si le graphe est orienté ou non connexe
    """'''
    # ---------------------------
    # VALIDATION
    # ---------------------------
    if graph.directed:
        raise ValueError("Prim only works on undirected graphs.")
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
    start = start if start is not None else nodes[0]

    if start not in graph.get_nodes():
        raise ValueError(f"Start node '{start}' does not exist.")

    visited      = {start}
    mst_edges    = []
    total_weight = 0
    steps        = []

    # Tas min : (poids, sommet_origine, sommet_destination)
    # get_neighbors() retourne [(neighbor, weight, capacity)]
    heap = [
        (w, start, neighbor)
        for neighbor, w, c in graph.get_neighbors(start)
    ]
    heapq.heapify(heap)

    steps.append(f"Start from node '{start}'")

    # ---------------------------
    # MAIN LOOP
    # ---------------------------
    while heap and len(visited) < len(nodes):
        w, u, v = heapq.heappop(heap)

        if v in visited:
            steps.append(f"Skip edge ({u}–{v}) → '{v}' already visited")
            continue

        # Nouveau sommet ajouté au MST
        visited.add(v)
        mst_edges.append((u, v, w))
        total_weight += w
        steps.append(f"Add edge ({u}–{v}, weight={w}) → '{v}' joins MST")

        # Pousser les voisins non visités dans le tas
        for neighbor, weight, capacity in graph.get_neighbors(v):
            if neighbor not in visited:
                heapq.heappush(heap, (weight, v, neighbor))

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