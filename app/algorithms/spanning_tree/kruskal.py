def kruskal(graph):
    parent = {}
    rank = {}

    def find(u):
        if parent[u] != u:
            parent[u] = find(parent[u])
        return parent[u]

    def union(u, v):
        root_u = find(u)
        root_v = find(v)

        if root_u != root_v:
            if rank[root_u] > rank[root_v]:
                parent[root_v] = root_u
            else:
                parent[root_u] = root_v
                if rank[root_u] == rank[root_v]:
                    rank[root_v] += 1

    # Initialize
    for node in graph.get_nodes():
        parent[node] = node
        rank[node] = 0

    # Sort edges by weight
    edges = sorted(graph.get_edges(), key=lambda x: x[2])

    mst = []
    total_weight = 0
    steps = []

    for u, v, w, _ in edges:
        if find(u) != find(v):
            union(u, v)
            mst.append((u, v, w))
            total_weight += w
            steps.append(f"Add edge {u}-{v} (weight={w})")

    return {
        "mst_edges": mst,
        "total_weight": total_weight,
        "steps": steps
    }