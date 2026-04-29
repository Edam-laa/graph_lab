import time
from app.utils.file_loader import load_graph_from_json
from app.algorithms.shortest_path.dijkstra import dijkstra, reconstruct_path


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
        return json_data