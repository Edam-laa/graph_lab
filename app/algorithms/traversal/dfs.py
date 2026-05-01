def dfs(graph, start):
    visited = set()

    order = []
    tree_edges = []
    times = {}

    time = 0
    steps = []

    def visit(u):
        nonlocal time
        visited.add(u)

        time += 1
        times[u] = {"discover": time}

        order.append(u)
        steps.append(f"Visit {u}")

        for v, _, _ in graph.get_neighbors(u):
            if v not in visited:
                tree_edges.append((u, v))
                steps.append(f"Go deeper {u} -> {v}")
                visit(v)

        time += 1
        times[u]["finish"] = time

    visit(start)

    return {
        "order": order,
        "tree_edges": tree_edges,
        "times": times,
        "steps": steps
    }