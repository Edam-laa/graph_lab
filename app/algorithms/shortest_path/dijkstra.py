import heapq


def dijkstra(graph, start):
    # ---------------------------
    # VALIDATION
    # ---------------------------
    if start not in graph.get_nodes():
        raise ValueError("Start node does not exist")

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