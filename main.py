'''from app.utils.file_loader import load_graph_from_json

if __name__ == "__main__":
    graph = load_graph_from_json("data/simple_graph.json")

    print("Nodes:", graph.get_nodes())
    print("Edges:", graph.get_edges())

    print("Has negative weights:", graph.has_negative_weights())
    print("Has capacity:", graph.has_capacity())'''



import json
from app.services.graph_service import execute_algorithm

import os
if __name__ == "__main__":
    # 1. Load full JSON (not just graph)
    print(os.getcwd())
    with open("data/simple_graph.json", "r") as f:
        data = json.load(f)

    # 2. Execute algorithm
    result = execute_algorithm(data)

    print("\n=== FINAL RESULT JSON ===\n")
print(json.dumps(result, indent=4))