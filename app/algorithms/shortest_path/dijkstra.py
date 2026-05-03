import heapq


def _detect_self_loops(graph):
    """Detect if there are any self-loops in the graph."""
    for node in graph.get_nodes():
        neighbors = graph.get_neighbors(node)
        for neighbor, _, _ in neighbors:
            if node == neighbor:
                return True
    return False


def _validate_adjacency(graph):
    """Verify that all neighbors referenced exist in the nodes list."""
    nodes_set = set(graph.get_nodes())
    for node in graph.get_nodes():
        neighbors = graph.get_neighbors(node)
        for neighbor, _, _ in neighbors:
            if neighbor not in nodes_set:
                raise ValueError(f"Invalid adjacency reference: neighbor '{neighbor}' does not exist in the graph nodes")


def _validate_numeric_weights(graph):
    """Verify that all weights are numeric."""
    for node in graph.get_nodes():
        neighbors = graph.get_neighbors(node)
        for neighbor, weight, _ in neighbors:
            try:
                float(weight)
            except (TypeError, ValueError):
                raise ValueError(f"Non-numeric weight detected: edge {node}->{neighbor} has weight '{weight}'")


def dijkstra(graph, start):
    # ---------------------------
    # VALIDATION
    # ---------------------------
    if start not in graph.get_nodes():
        raise ValueError("Start node does not exist")

    # Validation: Detect self-loops
    if _detect_self_loops(graph):
        raise ValueError("Graph contains self-loops (u → u)")
    
    # Validation: Check adjacency references
    _validate_adjacency(graph)
    
    # Validation: Check numeric weights
    _validate_numeric_weights(graph)

    if graph.has_negative_weights():
        raise ValueError("Dijkstra cannot run on graphs with negative weights")

    # ---------------------------
    # INITIALIZATION
    # ---------------------------
    distances = {node: float('inf') for node in graph.get_nodes()}
    previous = {node: None for node in graph.get_nodes()}

    distances[start] = 0

    # Priority queue: (distance, node)
    pq = [(0, start)]

    steps = []

    # ---------------------------
    # MAIN LOOP
    # ---------------------------
    while pq:
        current_distance, current_node = heapq.heappop(pq)

        # Ignore outdated entries
        if current_distance > distances[current_node]:
            continue

        steps.append(f"Visit {current_node} (distance={current_distance})")

        for neighbor, weight, capacity in graph.get_neighbors(current_node):
            new_distance = current_distance + weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node

                heapq.heappush(pq, (new_distance, neighbor))

                steps.append(
                    f"Update {neighbor}: distance={new_distance} via {current_node}"
                )

    # ---------------------------
    # RETURN RESULT
    # ---------------------------
    return {
        "distances": distances,
        "previous": previous,
        "steps": steps
    }


# ---------------------------
# PATH RECONSTRUCTION
# ---------------------------
def reconstruct_path(previous, start, end):
    path = []
    current = end

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()

    if path and path[0] == start:
        return path

    return []