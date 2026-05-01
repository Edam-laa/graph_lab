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

    if not nodes:
        log("SC1", "Empty graph → considered strongly connected")
        return {
            "strongly_connected": True,
            "steps": steps
        }

    # If undirected graph → reuse simple connectivity
    if not graph.directed:
        log("SC2", "Graph is undirected → fallback to connectivity check")
        from connectivity import is_connected
        result = is_connected(graph)
        return {
            "strongly_connected": result["connected"],
            "steps": result["steps"]
        }

    start_node = nodes[0]
    log("SC3", f"Starting node selected: {start_node}")

    # -------------------------
    # PASS 1: normal graph DFS
    # -------------------------
    log("SC4", "PASS 1: DFS on original graph")

    if not _can_reach_all_with_steps(graph.adj_list, graph, start_node, steps, "SC5"):
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

    for u in graph.adj_list:
        for v, w, c in graph.adj_list[u]:
            reversed_adj[v].append((u, w, c))
            log("SC7", f"Reverse edge {u} → {v} becomes {v} → {u}")

    log("SC4", "PASS 2: DFS on reversed graph")

    if not _can_reach_all_with_steps(reversed_adj, graph, start_node, steps, "SC5"):
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