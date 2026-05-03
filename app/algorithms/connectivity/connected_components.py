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

    if not nodes:
        log("C1", "Empty graph → considered connected")
        return {
            "connected": True,
            "steps": steps
        }

    # Build undirected adjacency
        return True
    
    # Validation: Check that all neighbors referenced in adj_list exist in nodes
    nodes_set = set(nodes)
    for u in graph.adj_list:
        for v, _, _ in graph.adj_list[u]:
            if v not in nodes_set:
                raise ValueError(f"Invalid adjacency reference: neighbor '{v}' does not exist in the graph nodes")
    
    # Build a temporary undirected mapping to check total connectivity
    undirected_adj = {node: set() for node in nodes}

    for u in graph.adj_list:
        # Vérification si le nœud source existe dans la liste des nœuds
        if u not in undirected_adj:
            raise ValueError(f"Node '{u}' in adjacency list is not in the graph nodes")
            
        for v, _, _ in graph.adj_list[u]:
            # Correction : Vérification si le voisin 'v' existe dans le graphe
            if v not in undirected_adj:
                log("E1", f"Error: Node '{v}' referenced as neighbor of '{u}' is missing")
                raise ValueError(f"Node '{v}' referenced in adjacency is not in the graph nodes")
            
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

    if connected:
        log("C7", "All nodes reached → graph is connected")
    else:
        missing = set(nodes) - visited
        log("C8", f"Unreachable nodes detected: {list(missing)}")
        
    return {
        "connected": connected,
        "steps": steps
    }