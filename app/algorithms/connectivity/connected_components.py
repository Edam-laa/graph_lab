def is_connected(graph):
    """
    Checks if the graph is connected (or weakly connected if directed).
    Treats all edges as bidirectional.
    """
    nodes = graph.get_nodes()
    if not nodes:
        return True
    
    # Build a temporary undirected mapping to check total connectivity
    undirected_adj = {node: set() for node in nodes}
    for u in graph.adj_list:
        for v, _, _ in graph.adj_list[u]:
            undirected_adj[u].add(v)
            undirected_adj[v].add(u)
    
    start_node = nodes[0]
    visited = {start_node}
    stack = [start_node]
    
    while stack:
        curr = stack.pop()
        for neighbor in undirected_adj[curr]:
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)
    
    return len(visited) == len(nodes)
