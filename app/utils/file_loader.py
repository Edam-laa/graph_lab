import json


<<<<<<< HEAD
def load_graph(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    return load_graph_from_json(json_data)


def load_graph_from_json(json_data):
    if isinstance(json_data, str):
        return load_graph(json_data)

=======
def load_graph_from_json(json_data):
>>>>>>> origin/Taki
    from app.core.graph import Graph
    graph_data = json_data["graph"]

    g = Graph(directed=graph_data["directed"])

    # Add nodes
    for node in graph_data.get("nodes", []):
        g.add_node(node)

    # Add edges
    for edge in graph_data.get("edges", []):
        u = edge["from"]
        v = edge["to"]
        w = edge.get("weight", 1)
        c = edge.get("capacity", None)

        g.add_edge(u, v, w, c)

    return g  