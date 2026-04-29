def welsh_powell(graph):
    # ---------------------------
    # STEP 1: Sort nodes by degree (descending)
    # ---------------------------
    nodes = sorted(graph.get_nodes(), key=lambda x: graph.degree(x), reverse=True)

    color_map = {}
    current_color = 0

    steps = []

    # ---------------------------
    # STEP 2: Assign colors
    # ---------------------------
    for node in nodes:
        if node not in color_map:
            current_color += 1
            color_map[node] = current_color

            steps.append(f"Assign color {current_color} to {node}")

            for other in nodes:
                if other not in color_map:
                    # Check if adjacent to any node with current_color
                    conflict = False

                    for neighbor, _, _ in graph.get_neighbors(other):
                        if neighbor in color_map and color_map[neighbor] == current_color:
                            conflict = True
                            break

                    if not conflict:
                        color_map[other] = current_color
                        steps.append(f"Assign color {current_color} to {other}")

    return {
        "node_colors": color_map,
        "steps": steps
    }