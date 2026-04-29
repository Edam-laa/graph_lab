def connected_components(graph):
    visited = set()
    components = []
    steps = []

    def dfs(node, comp):
        visited.add(node)
        comp.append(node)

        for neighbor, _, _ in graph.get_neighbors(node):
            if neighbor not in visited:
                dfs(neighbor, comp)

    for node in graph.get_nodes():
        if node not in visited:
            comp = []
            dfs(node, comp)
            components.append(comp)
            steps.append(f"Component found: {comp}")

    return {
        "components": components,
        "steps": steps
    }