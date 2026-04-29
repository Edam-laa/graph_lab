def strongly_connected_components(graph):
    stack = []
    visited = set()
    steps = []

    # -----------------------
    # 1. First DFS (fill stack)
    # -----------------------
    def dfs_fill(u):
        visited.add(u)
        for v, _, _ in graph.get_neighbors(u):
            if v not in visited:
                dfs_fill(v)
        stack.append(u)

    for node in graph.get_nodes():
        if node not in visited:
            dfs_fill(node)

    # -----------------------
    # 2. Reverse graph
    # -----------------------
    reversed_adj = {u: [] for u in graph.get_nodes()}
    for u in graph.get_nodes():
        for v, w, c in graph.get_neighbors(u):
            reversed_adj[v].append((u, w, c))

    # -----------------------
    # 3. DFS on reversed graph
    # -----------------------
    visited.clear()
    components = []

    def dfs_reverse(u, comp):
        visited.add(u)
        comp.append(u)
        for v, _, _ in reversed_adj[u]:
            if v not in visited:
                dfs_reverse(v, comp)

    while stack:
        node = stack.pop()
        if node not in visited:
            comp = []
            dfs_reverse(node, comp)
            components.append(comp)
            steps.append(f"SCC found: {comp}")

    return {
        "components": components,
        "steps": steps
    }