def check_eulerian_status(graph):
    nodes = graph.get_nodes()
    
    # CAS 1: Graphe vide (test_empty_graph_raises_value_error)
    if not nodes:
        raise ValueError("Le graphe est vide.")
    
    # CAS 2: Graphe avec un seul nœud (test_single_vertex_graph_raises_value_error)
    if len(nodes) == 1:
        # Un nœud seul sans arêtes ne permet pas de définir un parcours eulérien valide ici
        raise ValueError("Graphe à sommet unique sans arêtes.")
    
    # CAS 3: Graphe sans arêtes (test_undirected_non_eulerian_or_disconnected_graphs[zero_edge_graph])
    has_edges = any(graph.adj_list.get(node) for node in nodes)
    if not has_edges:
        raise ValueError("Le graphe ne contient aucune arête.")
    
    # CAS 4: Vérifier la connexité appropriée
    if not graph.directed:
        if not _is_connected_undirected(graph):
            raise ValueError("Le graphe non-orienté n'est pas connexe.")
    else:
        if not _is_eulerian_connected_directed(graph):
            raise ValueError("Le graphe orienté n'est pas suffisamment connecté.")
    
    # CAS 5: Vérifier les degrés
    status = _check_undirected_degrees(graph) if not graph.directed else _check_directed_degrees(graph)
    
    if status == 0:
        raise ValueError("Les degrés des sommets ne permettent pas un chemin/circuit eulérien.")
    
    return status
def _is_connected_undirected(graph):
    """Vérifie si le graphe non-orienté est connexe (en ignorant les nœuds isolés)."""
    nodes = graph.get_nodes()
    
    # Trouver le premier nœud qui a des arêtes
    start = None
    for node in nodes:
        if graph.adj_list.get(node):
            start = node
            break
    
    if start is None:
        return False  # Pas d'arêtes
    
    # DFS pour vérifier connexité
    visited = set()
    stack = [start]
    
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        
        for neighbor, _, _ in graph.adj_list.get(node, []):
            if neighbor not in visited:
                stack.append(neighbor)
    
    # Vérifier que tous les nœuds avec arêtes sont visités
    nodes_with_edges = {node for node in nodes if graph.adj_list.get(node)}
    return visited == nodes_with_edges


def _is_eulerian_connected_directed(graph):
    """
    Vérifie la connexité pour graphe orienté eulérien.
    
    Pour un circuit eulérien: forte connexité requise
    Pour un chemin eulérien: connexité faible + structure spéciale
    """
    nodes = graph.get_nodes()
    
    # Calculer in-degree et out-degree
    in_degree = {node: 0 for node in nodes}
    out_degree = {node: 0 for node in nodes}
    
    for u in graph.adj_list:
        for v, _, _ in graph.adj_list[u]:
            out_degree[u] += 1
            in_degree[v] += 1
    
    # Identifier les nœuds avec arêtes
    nodes_with_edges = set()
    for node in nodes:
        if in_degree[node] > 0 or out_degree[node] > 0:
            nodes_with_edges.add(node)
    
    if not nodes_with_edges:
        return False
    
    # Vérifier connexité faible (graphe sous-jacent non-orienté est connexe)
    start = next(iter(nodes_with_edges))
    visited = set()
    stack = [start]
    
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        
        # Explorer dans les deux directions (ignorer orientation)
        for neighbor, _, _ in graph.adj_list.get(node, []):
            if neighbor not in visited:
                stack.append(neighbor)
        
        # Explorer aussi les arêtes entrantes
        for other_node in graph.adj_list:
            for neighbor, _, _ in graph.adj_list[other_node]:
                if neighbor == node and other_node not in visited:
                    stack.append(other_node)
    
    return visited == nodes_with_edges


def _check_undirected_degrees(graph):
    """Vérifie les degrés pour graphe non-orienté."""
    nodes = graph.get_nodes()
    odd_degree_count = 0
    
    for node in nodes:
        degree = len(graph.adj_list.get(node, []))
        if degree % 2 != 0:
            odd_degree_count += 1
    
    if odd_degree_count == 0:
        return 2  # Circuit eulérien
    elif odd_degree_count == 2:
        return 1  # Chemin eulérien
    else:
        return 0  # Pas eulérien


def _check_directed_degrees(graph):


    """Vérifie les degrés pour graphe orienté."""


    nodes = graph.get_nodes()
    
    in_degree = {node: 0 for node in nodes}
    out_degree = {node: 0 for node in nodes}
    
    for u in graph.adj_list:
        for v, _, _ in graph.adj_list[u]:
            out_degree[u] += 1
            in_degree[v] += 1
    
    start_nodes = 0  # out > in
    end_nodes = 0    # in > out
    
    for node in nodes:
        diff = out_degree[node] - in_degree[node]
        
        if diff == 0:
            continue  # Nœud équilibré
        elif diff == 1:
            start_nodes += 1
        elif diff == -1:
            end_nodes += 1
        else:
            return 0  # Différence > 1, pas eulérien
    
    # Circuit eulérien: tous les nœuds équilibrés
    if start_nodes == 0 and end_nodes == 0:
        return 2
    
    # Chemin eulérien: exactement 1 start et 1 end
    if start_nodes == 1 and end_nodes == 1:
        return 1
    
    return 0


def find_eulerian_tour(graph):
    steps = []

    def log(code, msg):
        steps.append({"indexCode": code, "message": msg})

    log("E0", "Start Hierholzer algorithm")

    # Si status est 0 ou invalide, check_eulerian_status lèvera une ValueError
    # Cela règle les tests "raises_value_error"
    status = check_eulerian_status(graph) 
    log("E1", f"Eulerian status = {status}")

    nodes = graph.get_nodes()

    # trivial case
    if len(nodes) <= 1:
        log("E7", "Trivial graph → single node tour")
        return {
            "tour": nodes,
            "steps": steps
        }

    # copy adjacency list (important for edge removal)
    adj = {u: list(graph.adj_list.get(u, [])) for u in nodes}

    log("E2", "Adjacency list copied for modification")

    # find start node
    start = _find_start_node(graph, adj, status)
    log("E4", f"Start node selected: {start}")

    stack = [start]
    tour = []

    log("E4", f"Initialize stack = {stack}")

    # Hierholzer main loop
    while stack:
        u = stack[-1]
        log("E4", f"Top of stack: {u}")

        if adj[u]:
            v, w, c = adj[u].pop()

            log("E5", f"Traverse edge {u} → {v}")

            if not graph.directed:
                _remove_reverse_edge(adj, v, u)
                log("E5", f"Remove reverse edge {v} → {u}")

            stack.append(v)
            log("E5", f"Push {v} to stack → {stack}")

        else:
            popped = stack.pop()
            tour.append(popped)
            log("E6", f"Backtrack {popped}, add to tour")

    tour.reverse()

    log("E7", f"Final Eulerian tour = {tour}")

    # validation
    total_edges = sum(len(graph.adj_list.get(n, [])) for n in nodes)
    if not graph.directed:
        total_edges //= 2

    if len(tour) - 1 != total_edges:
        log("E8", "Edge count mismatch → invalid tour")
        return {
            "tour": [],
            "steps": steps
        }

    log("E7", "Valid Eulerian tour constructed")

    return {
        "tour": tour,
        "steps": steps
    }

def _find_start_node(graph, adj, status):
    """Trouve le nœud de départ optimal pour Hierholzer."""
    nodes = graph.get_nodes()
    
    if graph.directed:
        # Pour graphe orienté: chercher nœud avec out_degree > in_degree
        in_degree = {node: 0 for node in nodes}
        out_degree = {node: len(adj.get(node, [])) for node in nodes}
        
        for u in adj:
            for v, _, _ in adj[u]:
                in_degree[v] += 1
        
        for node in nodes:
            if out_degree[node] > in_degree[node]:
                return node
    else:
        # Pour graphe non-orienté: chercher nœud avec degré impair
        for node in nodes:
            if len(adj.get(node, [])) % 2 != 0:
                return node
    
    # Par défaut: premier nœud avec des arêtes
    for node in nodes:
        if adj.get(node):
            return node
    
    return nodes[0]


def _remove_reverse_edge(adj, u, v):
    """Supprime l'arête v->u de la liste d'adjacence (pour graphes non-orientés)."""
    if u not in adj:
        return
    
    # Trouver et supprimer l'arête
    for i, (neighbor, w, c) in enumerate(adj[u]):
        if neighbor == v:
            adj[u].pop(i)
            break
