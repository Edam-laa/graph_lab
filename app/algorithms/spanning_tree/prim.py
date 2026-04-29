import heapq

def prim(graph):
    nodes = graph.get_nodes()
    if not nodes:
        return {}

    start = nodes[0]
    visited = set([start])
    edges = []
    steps = []

    heap = []
    for v, w, _ in graph.get_neighbors(start):
        heapq.heappush(heap, (w, start, v))

    mst = []

    while heap:
        w, u, v = heapq.heappop(heap)
        if v in visited:
            continue

        visited.add(v)
        mst.append((u, v, w))
        steps.append(f"Add edge {u}-{v} (weight={w})")

        for to, weight, _ in graph.get_neighbors(v):
            if to not in visited:
                heapq.heappush(heap, (weight, v, to))

    return {
        "mst_edges": mst,
        "steps": steps
    }