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
from app.algorithms.connectivity.connected_components import is_connected
from app.algorithms.connectivity.strongly_connected import is_strongly_connected
from app.algorithms.eulerian.eulerian_path import check_eulerian_status, find_eulerian_tour
from app.algorithms.coloring.welsh_powell import welsh_powell
from app.algorithms.spanning_tree.kruskal import kruskal
from app.algorithms.spanning_tree.prim    import prim
from app.algorithms.traversal.bfs import bfs
from app.algorithms.traversal.dfs import dfs
def handle_kruskal(graph, params):
    result = kruskal(graph)
    return {
        "type":       "mst",
        "mst_edges": result["mst_edges"],
        "distances":  {"total_weight": result["total_weight"]},
        
        "steps":      result.get("steps", []),
        "complexity": "O(E log E)"
    }


def handle_prim(graph, params):
    # Sommet de départ optionnel depuis params
    start  = params.get("source", None)
    result = prim(graph, start=start)

    return {
        "type":       "mst",
        "mst_edges": result["mst_edges"],
        "distances":  {"total_weight": result["total_weight"]},
        "steps":      result.get("steps", []),
        "complexity": "O((V + E) log V)"
    }
def handle_dijkstra(graph, params):
    source = params.get("source")
    target = params.get("target")
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
    target = params.get("target")
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
    target = params.get("target")
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
    
    return {
        "type": "max_flow",
        "flow": {
            "value": result["max_flow"],
            "augmenting_paths": result["augmenting_paths"]
        },
        "steps": result.get("steps", []),
        "complexity": "O(E * max_flow)"
    }
def handle_connectivity(graph, params):
    result=is_connected(graph)
    print(result)
    print("aa")
    return {
        "type": "connectivity_check",
        "components": [list(graph.nodes)] if result["connected"] else [], # Simplified
        "steps":result["steps"],
        "graph_properties": {
            "is_connected": result["connected"]
        },
        "complexity": "O(V + E)"
    }

def handle_strong_connectivity(graph, params):
    result=is_strongly_connected(graph)
    return {
        "type": "strong_connectivity_check",
        "graph_properties": {
            "is_strongly_connected": result["strongly_connected"]
        },
        "steps":result["steps"],
        "complexity": "O(V + E)"
    }

def handle_eulerian(graph, params):
    status_code = check_eulerian_status(graph)
    result = find_eulerian_tour(graph) if status_code > 0 else []
    tour=result["tour"]
    # Map to your JSON result fields
    res = {
        "type": "eulerian_analysis",
        "eulerian_path": tour if status_code == 1 else [],
        "eulerian_circuit": tour if status_code == 2 else [], 
        "graph_properties": {
            "is_eulerian": status_code > 0
        },
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
            "tree_edges": result["tree_edges"],
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
            "tree_edges": result["tree_edges"],
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
    "strong_connectivity": handle_strong_connectivity,
    "eulerian":          handle_eulerian,
    "welsh_powell":      handle_welsh_powell,
    "kruskal":           handle_kruskal,   # ← ton ajout
    "prim":              handle_prim,      # ← ton ajout
    "bfs":               handle_bfs,
    "dfs":               handle_dfs
}
def execute_algorithm(json_data):
    try:
        # 1. Build graph
        graph = load_graph_from_json(json_data)
        
        algo_name = json_data["algorithm"]["name"].lower()
        params = json_data["algorithm"].get("params", {})
        print("XDDDD")
        if algo_name not in ALGO_REGISTRY:
            raise ValueError(f"Algorithm '{algo_name}' is not registered.")

        # 2. Start timer
        start_time = time.time()

        # 3. Run selected function from dict
        handler = ALGO_REGISTRY[algo_name]
        output = handler(graph, params)
        print(output)
        # 4. Stop timer
        end_time = time.time()
        print("XDDDD")
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