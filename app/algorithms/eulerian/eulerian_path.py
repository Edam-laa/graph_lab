def eulerian_path(graph):
    from collections import defaultdict

    if graph.directed:
        raise ValueError("Eulerian path implemented only for undirected graphs")

    adj = defaultdict(list)

    for u in graph.get_nodes():
        for v, _, _ in graph.get_neighbors(u):
            adj[u].append(v)

    # -----------------------
    # 1. Check degrees
    # -----------------------
    odd_nodes = [u for u in adj if len(adj[u]) % 2 == 1]

    if len(odd_nodes) not in [0, 2]:
        raise ValueError("Graph is not Eulerian")

    start = odd_nodes[0] if odd_nodes else graph.get_nodes()[0]

    # -----------------------
    # 2. Hierholzer's Algorithm
    # -----------------------
    stack = [start]
    path = []
    steps = []

    while stack:
        u = stack[-1]
        if adj[u]:
            v = adj[u].pop()
            adj[v].remove(u)
            stack.append(v)
            steps.append(f"Traverse edge {u}-{v}")
        else:
            path.append(stack.pop())

    path.reverse()

    return {
        "path": path,
        "steps": steps
    }