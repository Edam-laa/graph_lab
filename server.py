import traceback
from flask import Flask, request, jsonify
from app.services.graph_service import execute_algorithm

app = Flask(__name__)
ALGO_NAME_MAP = {
    # ─── Shortest Path ─────────────────────
    "Dijkstra": "dijkstra",
    "Bellman-Ford": "bellman_ford",
    "Bellman": "bellman_ford",

    # ─── MST ───────────────────────────────
    "Kruskal": "kruskal",
    "Prim": "prim",

    # ─── Traversal / Connectivity ──────────
    "Composantes Connexes": "connected_components",
    "BFS": "bfs",
    "DFS": "dfs",

    # ─── Euler ─────────────────────────────
    "Chemin Eulérien": "eulerian",
    "Circuit Eulérien": "eulerian",

    # ─── Coloring ──────────────────────────
    "Welsh-Powell": "welsh_powell",
    "Greedy Coloring": "graph_coloring",

    # ─── Flow ──────────────────────────────
    "Ford-Fulkerson": "ford_fulkerson",
    "Edmonds-Karp": "edmonds_karp",

    # ─── Fallback safety ───────────────────
}
COLOR_PALETTE = {
    1: "#ff5555",
    2: "#50fa7b",
    3: "#8be9fd",
    4: "#ffb86c",
    5: "#bd93f9",
    6: "#f1fa8c",
    7: "#ff79c6",
    8: "#6272a4"
}
def resolve_algorithm_name(front_name: str) -> str:
    if not front_name:
        #return "dijkstra"  # Default algorithm if none provided
        raise ValueError("Algorithm name is missing")
    if front_name not in ALGO_NAME_MAP:
        print(f"[WARNING] Unknown algorithm from frontend: {front_name}")

    return ALGO_NAME_MAP.get(front_name, front_name.lower().replace(" ", "_"))
def translate_colors(node_colors):
    translated = {}

    for node, color_id in node_colors.items():
        color_id = int(color_id)+1  # Ensure it's an integer
        translated[node] = COLOR_PALETTE.get(color_id, "#cccccc")  # fallback gray

    return translated
# ─────────────────────────────────────────────
# FRONT ➜ BACKEND FORMAT TRANSLATOR
# ─────────────────────────────────────────────
def to_backend_format(data):
    algo_name_raw = data.get("algorithm", {}).get("name")
    print(data)
    return {
        "graph": data.get("graph", {}),
        "algorithm": {
            "name": resolve_algorithm_name(algo_name_raw),
            "category": data.get("algorithm", {}).get("category"),
            "params": data.get("algorithm", {}).get("params", {}),

            # You can later compute this dynamically if needed
            "constraints_check": {
                "requires_positive_weights": False,
                "requires_positive_capacity": False,
                "requires_connected": False,
                "requires_dag": False
            }
        },

        "execution": {
            "execution_time": None,
            "complexity": None,
            "status": "not_started",
            "message": "",
            "warnings": []
        },

        "result": {
            "type": None,
            "distances": {},
            "predecessors": {},
            "path": [],
            "paths": {},
            "mst_edges": [],
            "components": [],
            "cycles": [],
            "eulerian_path": [],
            "eulerian_circuit": [],
            "coloring": {
                "node_colors": {},
                "edge_colors": {}
            },
            "flow": {
                "value": None,
                "augmenting_paths": [],
                "edge_flows": {}
            },
            "traversal": {
                "order": [],
                "tree_edges": [],
                "levels": {},
                "times": {}
            },
            "graph_properties": {},
            "steps": []
        },

        "options": {
            "return_path": True,
            "return_steps": True,
            "measure_time": True,
            "visualize": False
        }
    }
def to_frontend_format(backend_result):
    res = backend_result.get("result", backend_result)

    # 🎨 Handle coloring translation
    coloring = res.get("coloring", {})
    node_colors = coloring.get("node_colors", {})

    # Convert IDs → HEX
    translated_colors = translate_colors(node_colors) if node_colors else {}

    return {
        "graph": backend_result.get("graph", {}),

        "algorithm": backend_result.get("algorithm", {}),

        "execution": backend_result.get("execution", {}),

        "result": {
            "type": res.get("type"),

            "distances": res.get("distances", {}),
            "predecessors": res.get("predecessors", {}),
            "path": res.get("path", []),
            "paths": res.get("paths", []),

            "mst_edges": res.get("mst_edges", []),
            "components": res.get("components", []),
            "cycles": res.get("cycles", []),

            "eulerian_path": res.get("eulerian_path", []),
            "eulerian_circuit": res.get("eulerian_circuit", []),

            "coloring": {
                "node_colors": translated_colors,
                "edge_colors": coloring.get("edge_colors", {})
            },

            "flow": res.get("flow", {}),

            "traversal": res.get("traversal", {}),

            "graph_properties": res.get("graph_properties", {}),

            "steps": res.get("steps", [])
        }
    }

@app.route("/run-algorithm", methods=["POST"])
def run_algorithm():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON received"}), 400

         # 🔁 FRONT → BACKEND FORMAT
        backend_input = to_backend_format(data)

        # 🧠 RUN ALGORITHM ENGINE
        backend_output = execute_algorithm(backend_input)

        # 🔁 BACKEND → FRONTEND FORMAT
        frontend_result = to_frontend_format(backend_output)
        print("\n=== FRONTEND RESULT ===\n")
        print(frontend_result)
        return jsonify({
            "status": "success",
            "result": frontend_result
        })

    except Exception as e:
        traceback.print_exc()  # 🔥 ADD THIS

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)