import json


def load_graph_from_json(json_data):
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