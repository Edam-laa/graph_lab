
import json


def load_graph(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    return load_graph_from_json(json_data)
def load_graph_from_json(json_data):
    if isinstance(json_data, str):
        return load_graph(json_data)

    from app.core.graph import Graph
    
    if "graph" not in json_data:
        raise ValueError("Le JSON doit contenir une clé 'graph'")
        
    graph_data = json_data["graph"]

    # 1. Vérification que 'nodes' et 'edges' sont des listes
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not isinstance(nodes, list):
        raise ValueError("'nodes' doit être une liste")
    if not isinstance(edges, list):
        raise ValueError("'edges' doit être une liste")

    g = Graph(directed=graph_data.get("directed", False))

    # Ajout des nœuds
    for node in nodes:
        g.add_node(node)

    # 2. Validation et ajout des arêtes
    for edge in edges:
        # Vérification de la présence des clés "from" et "to"
        if "from" not in edge or "to" not in edge:
            raise ValueError("Chaque arête doit avoir les clés 'from' et 'to'")

        u = edge["from"]
        v = edge["to"]

        # Vérification que les sommets référencés existent
        # (Hypothèse : g.nodes contient la liste des identifiants ajoutés)
        if u not in nodes or v not in nodes:
            raise ValueError(f"L'arête ({u} -> {v}) référence un nœud inexistant")

        # Validation du poids (weight)
        w = edge.get("weight", 1)
        if not isinstance(w, (int, float)):
            raise ValueError(f"Le poids '{w}' doit être numérique")

        # Validation de la capacité (capacity)
        c = edge.get("capacity", None)
        if c is not None and not isinstance(c, (int, float)):
            raise ValueError(f"La capacité '{c}' doit être numérique ou None")

        g.add_edge(u, v, w, c)

    return g