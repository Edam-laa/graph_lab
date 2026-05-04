def _detect_cycle_dfs_directed(adj_list, nodes):
    """Detect if a cycle exists in the graph using DFS."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in nodes}
    
    def dfs(node):
        color[node] = GRAY
        for neighbor, _, _ in adj_list.get(node,[]):
            if color[neighbor] == GRAY:
                return True  # Back edge found, cycle detected
            if color[neighbor] == WHITE and dfs(neighbor):
                return True
        color[node] = BLACK
        return False
    
    for node in nodes:
        if color[node] == WHITE:
            if dfs(node):
                return True
    return False
def _detect_cycle_dfs_undirected(adj_list, nodes):
    visited = set()

    def dfs(node, parent):
        visited.add(node)
        for neighbor, _, _ in adj_list.get(node,[]):
            if neighbor not in visited:
                if dfs(neighbor, node):
                    return True
            elif neighbor != parent:
                return True  # real cycle

        return False
    for node in nodes:
        if node not in visited:
            if dfs(node, None):
                return True

    return False

def _detect_self_loops(adj_list):
    """Detect if there are any self-loops in the graph."""
    for u in adj_list:
        for v, _, _ in adj_list[u]:
            if u == v:
                return True
    return False


def bellman(graph, source):
    """
    Bellman-Ford algorithm for finding shortest paths in a weighted directed graph.
    
    Args:
        graph: Graph object with adjacency list
        source: Starting node for shortest path calculation
    
    Raises:
        ValueError: If graph is empty, source doesn't exist, cycles are detected,
                   self-loops exist, or negative cycles are detected
    
    Returns:
        dict: Contains 'distances', 'previous', and 'steps' keys
    """
    # anas badel begin
    metadata = getattr(graph, "metadata", {})
    target = metadata.get("target", metadata.get("sink"))
    nodes = graph.get_nodes()
    
    # Validation 1: Check if graph is empty
    if not nodes:
        raise ValueError("Graph contains no vertices")
    
    # Validation 2: Check if source exists
    if source not in nodes:
        raise ValueError(f"Source vertex '{source}' does not exist in the graph")

    # Validation 2b: Check if target exists when the fixture declares one
    if target is not None and target not in nodes:
        raise ValueError(f"Target vertex '{target}' does not exist in the graph")
    
    # Validation 3: Detect self-loops
    if _detect_self_loops(graph.adj_list):
        raise ValueError("Graph contains self-loops (u → u)")
    
    # Validation 4: Detect cycles using DFS
    if graph.directed:
        if _detect_cycle_dfs_directed(graph.adj_list, nodes):
            raise ValueError("Graph contains a cycle")
    else:
        if _detect_cycle_dfs_undirected(graph.adj_list, nodes):
            raise ValueError("Graph contains a cycle")
    
    distances = {node: float("inf") for node in nodes}
    previous = {node: None for node in nodes}
    steps = []

    distances[source] = 0

    # Relax edges V-1 times
    for i in range(len(nodes) - 1):
        for u in graph.adj_list:
            for v, w, _ in graph.adj_list[u]:
                if distances[u] + w < distances[v]:
                    distances[v] = distances[u] + w
                    previous[v] = u
                    steps.append(f"Iteration {i+1}: Relax {u}->{v}, new dist={distances[v]}")

    # Validation 5: Detect negative cycles after V-1 relaxations
    for u in graph.adj_list:
        for v, w, _ in graph.adj_list[u]:
            if distances[u] != float("inf") and distances[u] + w < distances[v]:
                raise ValueError("Graph contains a negative-weight cycle")

    return {
        "distances": distances,
        "previous": previous,
        "steps": steps
    }
    # anas badel end