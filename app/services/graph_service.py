import time
from app.utils.file_loader import load_graph_from_json
from app.algorithms.shortest_path.dijkstra import dijkstra, reconstruct_path
from app.algorithms.shortest_path.bellman_ford import bellman_ford
from app.algorithms.shortest_path.bellman import bellman
from app.algorithms.flow.ford_fulkerson import ford_fulkerson
from app.algorithms.connectivity.connected_components import is_connected
from app.algorithms.connectivity.strongly_connected import is_strongly_connected
from app.algorithms.eulerian.eulerian_path import check_eulerian_status, find_eulerian_tour
from app.algorithms.coloring.welsh_powell import welsh_powell
from app.algorithms.spanning_tree.kruskal import kruskal
from app.algorithms.spanning_tree.prim    import prim
from app.algorithms.traversal.bfs import bfs
from app.algorithms.traversal.dfs import dfs


def _param_target(params):
    return params.get("target") or params.get("sink")


def _edge_to_dict(edge):
    if isinstance(edge, dict):
        return {
            "from": edge.get("from"),
            "to": edge.get("to"),
            "weight": edge.get("weight", 1),
            "capacity": edge.get("capacity"),
        }

    if isinstance(edge, (list, tuple)):
        if len(edge) >= 4:
            return {"from": edge[0], "to": edge[1], "weight": edge[2], "capacity": edge[3]}
        if len(edge) == 3:
            return {"from": edge[0], "to": edge[1], "weight": edge[2], "capacity": None}
        if len(edge) == 2:
            return {"from": edge[0], "to": edge[1], "weight": 1, "capacity": None}

    raise ValueError(f"Invalid edge result format: {edge!r}")


def _edge_list_to_dicts(edges):
    return [_edge_to_dict(edge) for edge in edges]


def _weak_components(graph):
    nodes = graph.get_nodes()
    adjacency = {node: set() for node in nodes}

    for node in nodes:
        for neighbor, _, _ in graph.get_neighbors(node):
            adjacency[node].add(neighbor)
            adjacency.setdefault(neighbor, set()).add(node)

    components = []
    visited = set()
    for start in nodes:
        if start in visited:
            continue

        stack = [start]
        visited.add(start)
        component = []

        while stack:
            node = stack.pop()
            component.append(node)
            for neighbor in sorted(adjacency.get(node, [])):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)

        components.append(sorted(component))

    return components


def _augmenting_path_to_frontend(path_result):
    raw_edges = path_result.get("path", [])
    edges = _edge_list_to_dicts(raw_edges)
    nodes = []

    for edge in edges:
        if not nodes:
            nodes.append(edge["from"])
        nodes.append(edge["to"])

    return {
        "path": nodes,
        "edges": edges,
        "flow": path_result.get("flow", 0),
    }


def _flow_edge_totals(augmenting_paths):
    totals = {}

    for path_result in augmenting_paths:
        flow = path_result.get("flow", 0)
        for edge in path_result.get("edges", []):
            key = f"{edge['from']}->{edge['to']}"
            totals[key] = totals.get(key, 0) + flow

    return totals


def _build_objective(algo_name, params, output):
    source = params.get("source")
    target = _param_target(params)
    sink = params.get("sink")

    if algo_name in {"dijkstra", "bellman_ford", "bellman"}:
        if source and target:
            return f"Shortest path from {source} to {target}"
        if source:
            return f"Shortest paths from source {source}"
        return "Shortest path"

    if algo_name == "ford_fulkerson":
        if source and sink:
            return f"Maximum flow from {source} to {sink}"
        return "Maximum flow"

    if algo_name in {"kruskal", "prim"}:
        return "Minimum spanning tree"

    if algo_name in {"bfs", "dfs"}:
        if source:
            return f"Traversal from source {source}"
        return "Graph traversal"

    if algo_name == "connectivity":
        return "Connectivity check"

    if algo_name == "strong_connectivity":
        return "Strong connectivity check"

    if algo_name == "eulerian":
        if output.get("eulerian_circuit"):
            return "Find an Eulerian circuit"
        if output.get("eulerian_path"):
            return "Find an Eulerian path"
        return "Eulerian analysis"

    if algo_name == "welsh_powell":
        return "Graph coloring"

    return "Algorithm result"


def handle_kruskal(graph, params):
    result = kruskal(graph)
    return {
        "type":       "mst",
        "mst_edges": _edge_list_to_dicts(result["mst_edges"]),
        "total_weight": result["total_weight"],
        "steps":      result.get("steps", []),
        "complexity": "O(E log E)"
    }


def handle_prim(graph, params):
    # Sommet de départ optionnel depuis params
    start  = params.get("source", None)
    result = prim(graph, start=start)

    return {
        "type":       "mst",
        "mst_edges": _edge_list_to_dicts(result["mst_edges"]),
        "total_weight": result["total_weight"],
        "steps":      result.get("steps", []),
        "complexity": "O((V + E) log V)"
    }
def handle_dijkstra(graph, params):
    source = params.get("source")
    target = _param_target(params)
    if not source:
        raise ValueError("Dijkstra requires a 'source' parameter.")
    
    result = dijkstra(graph, source)
    path = reconstruct_path(result["previous"], source, target) if target else []
    
    return {
        "type": "shortest_path",
        "distances": result["distances"],
        "predecessors": result["previous"],
        "path": path,        
        "steps": result.get("steps", []),
        "complexity": "O((V + E) log V)"
    }
def handle_bellman_ford(graph, params):
    source = params.get("source")
    target = _param_target(params)
    if not source:
        raise ValueError("Bellman-Ford requires a 'source' parameter.")
    
    result = bellman_ford(graph, source)
    path = reconstruct_path(result["previous"], source, target) if target else []
    return {
        "type": "shortest_path",
        "distances": result["distances"],
        "predecessors": result["previous"],
        "path": path,
        "steps": result.get("steps", []),
        "complexity": "O(V * E)"
    }
def handle_bellman(graph, params):
    source = params.get("source")
    target = _param_target(params)
    if not source:
        raise ValueError("Bellman requires a 'source' parameter.")

    result = bellman(graph, source)
    path = reconstruct_path(result["previous"], source, target) if target else []

    return {
        "type": "shortest_path",
        "distances": result["distances"],
        "predecessors": result["previous"],
        "path": path,
        "steps": result.get("steps", []),
        "complexity": "O(V * E)"
    }
def handle_ford_fulkerson(graph, params):
    source = params.get("source")
    sink = params.get("sink")
    if not source or not sink:
        raise ValueError("Ford-Fulkerson requires 'source' and 'sink' parameters.")
    
    result = ford_fulkerson(graph, source, sink)
    augmenting_paths = [
        _augmenting_path_to_frontend(path_result)
        for path_result in result["augmenting_paths"]
    ]
    
    return {
        "type": "max_flow",
        "flow": {
            "value": result["max_flow"],
            "augmenting_paths": augmenting_paths,
            "edge_flows": _flow_edge_totals(augmenting_paths),
        },
        "steps": result.get("steps", []),
        "complexity": "O(E * max_flow)"
    }
def handle_connectivity(graph, params):
    result=is_connected(graph)
    components = _weak_components(graph)
    return {
        "type": "connectivity_check",
        "components": components,
        "steps":result["steps"],
        "graph_properties": {
            "is_connected": result["connected"],
            "component_count": len(components),
        },
        "complexity": "O(V + E)"
    }

def handle_strong_connectivity(graph, params):
    result=is_strongly_connected(graph)
    return {
        "type": "strong_connectivity_check",
        "graph_properties": {
            "is_strongly_connected": result["strongly_connected"],
            "component_count": len(_weak_components(graph)),
        },
        "steps":result["steps"],
        "complexity": "O(V + E)"
    }

def handle_eulerian(graph, params):
    status_code = check_eulerian_status(graph)
    result = find_eulerian_tour(graph) if status_code > 0 else None

    if isinstance(result, dict):
        tour = result.get("tour", [])
        steps = result.get("steps", [])
    else:
        tour = result or []
        steps = []

    # Map to your JSON result fields
    res = {
        "type": "eulerian_analysis",
        "eulerian_path": tour if status_code == 1 else [],
        "eulerian_circuit": tour if status_code == 2 else [], 
        "graph_properties": {
            "is_eulerian": status_code > 0,
            "has_eulerian_path": status_code == 1,
            "has_eulerian_circuit": status_code == 2,
        },
        "steps": steps,
        "complexity": "O(V + E)"}
    #if status_code == 2:
    #    res["special_paths"]["eulerian_circuit"] = tour
    #elif status_code == 1:
    #    res["special_paths"]["eulerian_path"] = tour
    return res


def handle_welsh_powell(graph, params):
    result= welsh_powell(graph)
    return {
        "type": "graph_coloring",
        "coloring": {"node_colors": result["coloring"]},
        "steps": result["steps"],
        "complexity": "O(V² + V log V)"
    }
def handle_bfs(graph, params):
    source = params.get("source")
    if not source:
        raise ValueError("BFS requires 'source'.")

    result = bfs(graph, source)

    return {
        "type": "traversal",
        "traversal": {
            "order": result["order"],
            "tree_edges": _edge_list_to_dicts(result["tree_edges"]),
            "levels": result["levels"]
        },
        "steps": result["steps"],
        "complexity": "O(V + E)"
    }
def handle_dfs(graph, params):
    source = params.get("source")
    if not source:
        raise ValueError("DFS requires 'source'.")

    result = dfs(graph, source)

    return {
        "type": "traversal",
        "traversal": {
            "order": result["order"],
            "tree_edges": _edge_list_to_dicts(result["tree_edges"]),
            "times": result["times"]
        },
        "steps": result["steps"],
        "complexity": "O(V + E)"
    }


# --- THE MAPPING DICTIONARY ---

ALGO_REGISTRY = {
    "dijkstra":          handle_dijkstra,
    "bellman_ford":      handle_bellman_ford,
    "bellman":           handle_bellman,
    "ford_fulkerson":    handle_ford_fulkerson,
    "connectivity":      handle_connectivity,
    "connected_components": handle_connectivity,
    "strong_connectivity": handle_strong_connectivity,
    "strongly_connected": handle_strong_connectivity,
    "eulerian":          handle_eulerian,
    "welsh_powell":      handle_welsh_powell,
    "kruskal":           handle_kruskal,   # ← ton ajout
    "prim":              handle_prim,      # ← ton ajout
    "bfs":               handle_bfs,
    "dfs":               handle_dfs
}
def execute_algorithm(json_data):
    start_time = time.time()
    try:
        # 1. Build graph
        graph = load_graph_from_json(json_data)
        
        algo_name = json_data["algorithm"]["name"].lower()
        params = json_data["algorithm"].get("params", {})
        if algo_name not in ALGO_REGISTRY:
            raise ValueError(f"Algorithm '{algo_name}' is not registered.")

        # 2. Start timer
        start_time = time.time()

        # 3. Run selected function from dict
        handler = ALGO_REGISTRY[algo_name]
        output = handler(graph, params)
        output["objective"] = _build_objective(algo_name, params, output)
        # 4. Stop timer
        end_time = time.time()
        # 5. Fill Execution metadata
        json_data["execution"].update({
            "execution_time": round(end_time - start_time, 6),
            "complexity": output.pop("complexity", "N/A"),
            "status": "success",
            "message": f"{algo_name} executed successfully"
        })

        # 6. Update Result field
        #json_data["result"].update(output)
        deep_merge(json_data["result"], output)
        return json_data

    except Exception as e:
        end_time = time.time()
        json_data["execution"].update({
            "status": "error",
            "message": str(e),
            "execution_time": round(end_time - start_time, 6)
        })
        return json_data
    
def deep_merge(base, update):
    for key, value in update.items():
        if isinstance(value, dict) and key in base:
            deep_merge(base[key], value)
        else:
            base[key] = value

def get_empty_result_template():
    return {
        "type": None,
        "metrics": {
            "distances": {},
            "predecessors": {},
            "levels": {},
            "times": {}
        },
        "structures": {
            "path": [],
            "paths": {},
            "tree_edges": [],
            "mst_edges": [],
            "components": [],
            "cycles": []
        },
        "total_weight": None,
        "flow": {
            "value": None,
            "edge_flows": {},
            "augmenting_paths": []
        },
        "coloring": {
            "node_colors": {},
            "edge_colors": {}
        },
        "special_paths": {
            "eulerian_path": [],
            "eulerian_circuit": []
        },
        "properties": {
            "is_connected": None,
            "is_strongly_connected": None,
            "is_tree": None,
            "is_bipartite": None,
            "is_eulerian": None,
            "has_cycle": None,
            "is_weighted": None
        },
        "steps": []
    }
