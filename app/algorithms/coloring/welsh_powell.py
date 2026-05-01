def welsh_powell(graph):
    """
    Welsh-Powell graph coloring with step-by-step trace.
    Returns:
        {
            "coloring": {node: color},
            "steps": [...]
        }
    """

    steps = []

    def log(code, msg):
        steps.append({
            "indexCode": code,
            "message": msg
        })

    log("WP0", "Start Welsh-Powell algorithm")

    # 1. Sort nodes by degree
    nodes_sorted = sorted(
        graph.get_nodes(),
        key=lambda x: graph.degree(x),
        reverse=True
    )

    log("WP1", f"Nodes sorted by degree: {nodes_sorted}")

    color_map = {}
    current_color = 0

    # 2. Coloring loop
    while len(color_map) < len(nodes_sorted):

        log("WP2", f"Starting coloring phase with color {current_color}")

        for node in nodes_sorted:

            if node in color_map:
                continue

            neighbors = graph.get_all_adjacent(node)
            log("WP3", f"Checking node {node}, neighbors = {neighbors}")

            can_color = True

            for neighbor in neighbors:
                if color_map.get(neighbor) == current_color:
                    can_color = False
                    log(
                        "WP4",
                        f"Conflict: {node} cannot take color {current_color} "
                        f"because neighbor {neighbor} has same color"
                    )
                    break

            if can_color:
                color_map[node] = current_color
                log("WP5", f"Assign color {current_color} to node {node}")

        current_color += 1
        log("WP6", f"Moving to next color → {current_color}")

    log("WP7", f"Final coloring completed: {color_map}")

    return {
        "coloring": color_map,
        "steps": steps
    }