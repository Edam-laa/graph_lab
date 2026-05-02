def bfs(graph, start):
    visited = set()
    queue = [start]

    order = []
    tree_edges = []
    levels = {start: 0}

    steps = []

    visited.add(start)

    while queue:
        u = queue.pop(0)
        order.append(u)
        steps.append(f"Visit {u}")

        for v, _, _ in graph.get_neighbors(u):
            if v not in visited:
                visited.add(v)
                queue.append(v)

                levels[v] = levels[u] + 1
                tree_edges.append((u, v))

                steps.append(f"Discover {v} from {u}")

    return {
        "order": order,
        "tree_edges": tree_edges,
        "levels": levels,
        "steps": steps
    }