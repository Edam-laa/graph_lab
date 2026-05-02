import json


# anas badel begin
def _is_numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_graph_payload(graph_data):
    if not isinstance(graph_data, dict):
        raise ValueError("Graph payload must be an object")

    nodes = graph_data.get("nodes")
    edges = graph_data.get("edges")

    if not isinstance(nodes, list):
        raise ValueError("Graph nodes must be provided as a list")

    if not isinstance(edges, list):
        raise ValueError("Graph edges must be provided as a list")

    node_set = set(nodes)
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("Each edge must be an object")
        if "from" not in edge:
            raise ValueError("Each edge must define a 'from' field")
        if "to" not in edge:
            raise ValueError("Each edge must define a 'to' field")

        weight = edge.get("weight", 1)
        capacity = edge.get("capacity", None)

        if not _is_numeric(weight):
            raise ValueError("Edge weight must be numeric")
        if capacity is not None and not _is_numeric(capacity):
            raise ValueError("Edge capacity must be numeric or None")
        if edge["from"] not in node_set or edge["to"] not in node_set:
            raise ValueError("Edge references a node that is not declared in nodes")
# anas badel end


def load_graph(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    return load_graph_from_json(json_data)


def load_graph_from_json(json_data):
    if isinstance(json_data, str):
        return load_graph(json_data)

    from app.core.graph import Graph
    graph_data = json_data["graph"]

    # anas badel begin
    _validate_graph_payload(graph_data)
    # anas badel end

    g = Graph(directed=graph_data["directed"])
    g.metadata = graph_data.get("metadata", {})

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