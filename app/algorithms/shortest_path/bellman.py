def bellman(graph, source):
    distances = {node: float("inf") for node in graph.get_nodes()}
    previous = {node: None for node in graph.get_nodes()}
    steps = []

    distances[source] = 0

    nodes = graph.get_nodes()

    # Relax edges V-1 times
    for i in range(len(nodes) - 1):
        for u in graph.adj_list:
            for v, w, _ in graph.adj_list[u]:
                if distances[u] + w < distances[v]:
                    distances[v] = distances[u] + w
                    previous[v] = u
                    steps.append(f"Iteration {i+1}: Relax {u}->{v}, new dist={distances[v]}")

    return {
        "distances": distances,
        "previous": previous,
        "steps": steps
    }