def is_strongly_connected(graph):
    """
    Verifies if every node is reachable from every other node 
    following the direction of the edges.
    """
    nodes = graph.get_nodes()
    if not nodes:
        return True

    # If the graph is undirected, strong connectivity is just connectivity
    if not graph.directed:
        from connectivity import is_connected
        return is_connected(graph)

    start_node = nodes[0]

    # Step 1: Check if all nodes are reachable from start_node
    if not _can_reach_all(graph, start_node, graph.adj_list):
        return False

    # Step 2: Reverse all edges and check reachability again
    # This is a standard part of Kosaraju's algorithm logic
    reversed_adj = {node: [] for node in nodes}
    for u in graph.adj_list:
        for v, w, c in graph.adj_list[u]:
            reversed_adj[v].append((u, w, c))
            
    return _can_reach_all(graph, start_node, reversed_adj)

def _can_reach_all(graph, start_node, adj):
    """Helper DFS to check reachability using a specific adjacency mapping."""
    visited = {start_node}
    stack = [start_node]
    while stack:
        curr = stack.pop()
        for edge_data in adj.get(curr, []):
            neighbor = edge_data[0]
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)
    return len(visited) == len(graph.nodes)