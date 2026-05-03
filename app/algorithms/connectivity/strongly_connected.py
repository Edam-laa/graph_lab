def is_strongly_connected(graph):
    """
    Verifies strong connectivity using DFS + reversed graph (Kosaraju logic).
    Returns:
        {
            "strongly_connected": bool,
            "steps": [...]
        }
    """
    steps = []

    def log(code, msg):
        steps.append({
            "indexCode": code,
            "message": msg
        })

    log("SC0", "Start strong connectivity check")

    nodes = graph.get_nodes()
    adj = graph.adj_list

    # --- AJOUT : Validation de l'intégrité ---
    # On vérifie que chaque nœud déclaré possède une entrée dans la liste d'adjacence
    # ----------------------------------------

    if not nodes:
        log("SC1", "Empty graph → considered strongly connected")
        return {
            "strongly_connected": True,
            "steps": steps
        }

    # If undirected graph → reuse simple connectivity

    for node in nodes:
        if node not in adj:
            raise ValueError(f"Node '{node}' is missing from the adjacency list")

    # If the graph is undirected, strong connectivity is just connectivity
    if not graph.directed:
        log("SC2", "Graph is undirected → fallback to connectivity check")
        from app.algorithms.connectivity.connected_components import is_connected
        result = is_connected(graph)
        return {
            "strongly_connected": result.get("connected", False),
            "steps": result["steps"]
        }

    start_node = nodes[0]
    log("SC3", f"Starting node selected: {start_node}")

    # -------------------------
    # PASS 1: normal graph DFS
    # -------------------------
    log("SC4", "PASS 1: DFS on original graph")

    if not _dfs_reach_all_with_steps(adj, start_node, nodes,steps, "SC5"):
        log("SC8", "Not all nodes reachable in original graph → not strongly connected")
        return {
            "strongly_connected": False,
            "steps": steps
        }

    log("SC6", "All nodes reachable in original graph")

    # -------------------------
    # PASS 2: reversed graph
    # -------------------------
    log("SC7", "Building reversed graph (transpose)")

    reversed_adj = {node: [] for node in nodes}

    for u in adj:
        for v, w, c in adj[u]:
            reversed_adj[v].append((u, w, c))
            log("SC7", f"Reverse edge {u} → {v} becomes {v} → {u}")

    log("SC4", "PASS 2: DFS on reversed graph")

    if not _dfs_reach_all_with_steps(reversed_adj, start_node, nodes, steps, "SC5"):
        log("SC8", "Not all nodes reachable in reversed graph → not strongly connected")
        return {
            "strongly_connected": False,
            "steps": steps
        }

    log("SC9", "All nodes reachable in reversed graph")

    log("SC10", "Graph is strongly connected")

    return {
        "strongly_connected": True,
        "steps": steps
    }
def _dfs_reach_all_with_steps(adj, start, nodes, steps, code):
    visited = set()
    stack = [start]

    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            steps.append({
                "indexCode": code,
                "message": f"Visit {node}"
            })

            for edge in adj.get(node, []):
                neighbor = edge[0]
                if neighbor not in visited:
                    stack.append(neighbor)

    return len(visited) == len(nodes)