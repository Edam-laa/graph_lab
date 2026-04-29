import time
from app.utils.file_loader import load_graph_from_json
from app.algorithms.shortest_path.dijkstra import dijkstra, reconstruct_path

<<<<<<< HEAD

def execute_algorithm(json_data):
    try:
        # -----------------------
        # 1. Build graph
        # -----------------------
        graph = load_graph_from_json(json_data)

        algo_name = json_data["algorithm"]["name"]
        params = json_data["algorithm"]["params"]

        # -----------------------
        # 2. Start timer
        # -----------------------
        start_time = time.time()

        # -----------------------
        # 3. Run algorithm
        # -----------------------
        if algo_name == "dijkstra":
            source = params["source"]
            target = params.get("target")

            result = dijkstra(graph, source)

            path = []
            if target:
                path = reconstruct_path(result["previous"], source, target)

            output = {
                "type": "shortest_path",
                "distances": result["distances"],
                "path": path,
                "steps": result["steps"]
            }

            complexity = "O((V + E) log V)"

        else:
            raise ValueError("Algorithm not supported")
        # -----------------------
        # 4. Stop timer

        # -----------------------
        end_time = time.time()
        # -----------------------
        # 5. Fill EXECUTION (HERE)
        # -----------------------
        json_data["execution"]["execution_time"] = round(end_time - start_time, 6)
        json_data["execution"]["complexity"] = complexity
        json_data["execution"]["status"] = "success"
        json_data["execution"]["message"] = f"{algo_name} executed successfully"

        # 6. Fill result
        json_data["result"].update(output)

        return json_data
    except Exception as e:
        # -----------------------
        # ERROR HANDLING (IMPORTANT)
        # -----------------------
        json_data["execution"]["status"] = "error"
        json_data["execution"]["message"] = str(e)
        json_data["execution"]["execution_time"] = None
=======
from app.algorithms.connectivity.connected_components import is_connected
from app.algorithms.connectivity.strongly_connected import is_strongly_connected
from app.algorithms.eulerian.eulerian_path import check_eulerian_status, find_eulerian_tour
from app.algorithms.coloring.welsh_powell import welsh_powell

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
        "path": path,
        "steps": result.get("steps", []),
        "complexity": "O((V + E) log V)"
    }

def handle_connectivity(graph, params):
    return {
        "type": "connectivity_check",
        "components": [list(graph.nodes)] if is_connected(graph) else [], # Simplified
        "complexity": "O(V + E)"
    }

def handle_strong_connectivity(graph, params):
    return {
        "type": "strong_connectivity_check",
        "is_strongly_connected": is_strongly_connected(graph),
        "complexity": "O(V + E)"
    }

def handle_eulerian(graph, params):
    status_code = check_eulerian_status(graph)
    tour = find_eulerian_tour(graph) if status_code > 0 else []
    
    # Map to your JSON result fields
    res = {"type": "eulerian_analysis", "complexity": "O(V + E)"}
    if status_code == 2:
        res["eulerian_circuit"] = tour
    elif status_code == 1:
        res["eulerian_path"] = tour
    return res

def handle_welsh_powell(graph, params):
    coloring = welsh_powell(graph)
    return {
        "type": "graph_coloring",
        "coloring": {"node_colors": coloring},
        "complexity": "O(V² + V log V)"
    }

# --- THE MAPPING DICTIONARY ---

ALGO_REGISTRY = {
    "dijkstra": handle_dijkstra,
    "connectivity": handle_connectivity,
    "strong_connectivity": handle_strong_connectivity,
    "eulerian": handle_eulerian,
    "welsh_powell": handle_welsh_powell
}


def execute_algorithm(json_data):
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
        json_data["result"].update(output)

        return json_data

    except Exception as e:
        json_data["execution"].update({
            "status": "error",
            "message": str(e),
            "execution_time": None
        })
>>>>>>> origin/Taki
        return json_data