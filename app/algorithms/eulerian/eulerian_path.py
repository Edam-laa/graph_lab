def check_eulerian_status(graph):
    """
    Returns: 0 (No Eulerian path/circuit), 1 (Eulerian Path), 2 (Eulerian Circuit)
    """
    from connectivity import is_connected
    
    if not is_connected(graph):
        return 0

    nodes = graph.get_nodes()
    
    if not graph.directed:
        # Undirected Logic: Based on nodes with odd degrees
        odd_degrees = 0
        for node in nodes:
            if graph.degree(node) % 2 != 0:
                odd_degrees += 1
        
        if odd_degrees == 0: return 2  # Circuit
        if odd_degrees == 2: return 1  # Path
        return 0
    else:
        # Directed Logic: Based on In-degree vs Out-degree
        in_degree = {node: 0 for node in nodes}
        out_degree = {node: 0 for node in nodes}
        
        for u in graph.adj_list:
            for v, _, _ in graph.adj_list[u]:
                out_degree[u] += 1
                in_degree[v] += 1
        
        start_nodes = 0
        end_nodes = 0
        balanced_nodes = 0
        
        for node in nodes:
            if in_degree[node] == out_degree[node]:
                balanced_nodes += 1
            elif out_degree[node] - in_degree[node] == 1:
                start_nodes += 1
            elif in_degree[node] - out_degree[node] == 1:
                end_nodes += 1
            else:
                return 0 # Gap too large
                
        if balanced_nodes == len(nodes): return 2 # Circuit
        if start_nodes == 1 and end_nodes == 1 and balanced_nodes == len(nodes) - 2:
            return 1 # Path
        return 0

def find_eulerian_tour(graph):
    """Finds the actual path/circuit using Hierholzer's Algorithm."""
    status = check_eulerian_status(graph)
    if status == 0:
        return None

    # Work on a copy of the adjacency list to "consume" edges
    adj = {u: [v for v, w, c in graph.adj_list[u]] for u in graph.adj_list}
    
    # Determine starting node
    start_node = graph.get_nodes()[0]
    if graph.directed:
        # Find node where out_degree > in_degree if it's a path
        for u in adj:
            in_d = sum(1 for src in adj for dest in adj[src] if dest == u)
            if len(adj[u]) > in_d:
                start_node = u
                break
    else:
        # Find node with odd degree if it's a path
        for u in adj:
            if len(adj[u]) % 2 != 0:
                start_node = u
                break

    stack = [start_node]
    path = []

    while stack:
        u = stack[-1]
        if adj.get(u):
            v = adj[u].pop()
            if not graph.directed:
                # Remove the reverse edge for undirected graphs
                if u in adj[v]: adj[v].remove(u)
            stack.append(v)
        else:
            path.append(stack.pop())

    return path[::-1]