from collections import defaultdict, deque

def ford_fulkerson(graph, source, sink):
    nodes = graph.get_nodes()

    # -----------------------------
    # Build residual graph
    # -----------------------------
    residual = defaultdict(lambda: defaultdict(int))

    for u in nodes:
        for v, _, capacity in graph.get_neighbors(u):
            if capacity is None:
                continue
            residual[u][v] += capacity
            residual[v]  # ensure reverse exists

    steps = []
    flow_paths = []
    max_flow = 0

    # -----------------------------
    # DFS for augmenting path
    # -----------------------------
    def dfs(u, visited, path_flow, path):
        if u == sink:
            return path_flow, path

        visited.add(u)

        for v in residual[u]:
            if v not in visited and residual[u][v] > 0:
                new_flow = min(path_flow, residual[u][v])

                result = dfs(v, visited, new_flow, path + [(u, v)])

                if result:
                    return result

        return None

    # -----------------------------
    # Main loop
    # -----------------------------
    while True:
        visited = set()
        result = dfs(source, visited, float("inf"), [])

        if not result:
            break

        flow, path = result
        max_flow += flow

        # update residual graph
        for u, v in path:
            residual[u][v] -= flow
            residual[v][u] += flow

        flow_paths.append({
            "path": path,
            "flow": flow
        })

        steps.append(f"Augmenting path {path} with flow {flow}")

    return {
        "max_flow": max_flow,
        "augmenting_paths": flow_paths,
        "steps": steps
    }