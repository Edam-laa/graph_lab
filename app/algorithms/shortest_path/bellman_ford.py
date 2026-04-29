def bellman_ford(graph, source):
    nodes = graph.get_nodes()
    edges = graph.get_edges()

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