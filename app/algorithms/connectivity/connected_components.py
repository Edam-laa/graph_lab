def is_connected(graph):
    """
    Checks if the graph is connected (weakly connected if directed).
    Returns:
        {
            "connected": bool,
            "steps": [...]
        }
    """

    steps = []
  
    def log(code, msg):
        steps.append({
            "indexCode": code,
            "message": msg
        })

    log("C0", "Start connectivity check (DFS on undirected projection)")
    nodes = graph.get_nodes()
    print("aaaaaaaaaaaaaaaaaaaaaaaaa",nodes)

    if not nodes:
        log("C1", "Empty graph → considered connected")
        return {
            "connected": True,
            "steps": steps
        }

    # Build undirected adjacency
    undirected_adj = {node: set() for node in nodes}

    for u in graph.adj_list:
        for v, _, _ in graph.adj_list[u]:
            undirected_adj[u].add(v)
            undirected_adj[v].add(u)

    log("C2", "Built undirected adjacency list for traversal")

    start_node = nodes[0]
    visited = {start_node}
    stack = [start_node]

    log("C3", f"Start DFS from node {start_node}")

    # DFS
    while stack:
        curr = stack.pop()
        log("C4", f"Visiting node {curr}")

        for neighbor in undirected_adj[curr]:
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)
                log("C5", f"Reach node {neighbor} from {curr}")

    log("C6", f"Visited nodes: {list(visited)}")

    connected = len(visited) == len(nodes)
    print("aaaaaaaaaaaaaaaaaaaaaaaaa","ouais connecté")

    if connected:
        log("C7", "All nodes reached → graph is connected")
    else:
        missing = set(nodes) - visited
        log("C8", f"Unreachable nodes detected: {list(missing)}")
    return {
        "connected": connected,
        "steps": steps
    }