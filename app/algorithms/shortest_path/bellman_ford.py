def _detect_self_loops(edges):
    """Detect if there are any self-loops in the edges."""
    for u, v, w, _ in edges:
        if u == v:
            return True
    return False

#Ajoute pour validation


def bellman_ford(graph, source, target=None):
    # anas badel begin
    if target is None:
        metadata = getattr(graph, "metadata", {})
        target = metadata.get("target", metadata.get("sink"))

    nodes = graph.get_nodes()
    edges = graph.get_edges()

    # Validation 1: Check if graph is empty
    if not nodes:
        raise ValueError("Graph contains no vertices")
    
    # Validation 2: Check if source exists
    if source not in nodes:
        raise ValueError(f"Source vertex '{source}' does not exist in the graph")
    
    # Validation 3: Check if target exists (if provided)
    if target is not None and target not in nodes:
        raise ValueError(f"Target vertex '{target}' does not exist in the graph")
    
    # Validation 4: Detect self-loops
    if _detect_self_loops(edges):
        raise ValueError("Graph contains self-loops (u → u)")

    dist = {node: float('inf') for node in nodes}
    prev = {node: None for node in nodes}

    dist[source] = 0

    steps = []

    # Relax edges V-1 times
    for i in range(len(nodes) - 1):
        for u, v, w, _ in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                steps.append(f"Relax {u}->{v}, new dist={dist[v]}")

    # Check negative cycle
    for u, v, w, _ in edges:
        if dist[u] + w < dist[v]:
            raise ValueError("Graph contains a negative-weight cycle")

    return {
        "distances": dist,
        "previous": prev,
        "steps": steps
    }
    # anas badel end