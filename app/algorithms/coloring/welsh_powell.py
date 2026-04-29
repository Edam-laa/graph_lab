def welsh_powell(graph):
    """
    Attribue une couleur à chaque nœud du graphe en utilisant l'algorithme de Welsh-Powell.
    Retourne un dictionnaire {nœud: couleur}.
    """
    # 1. Récupérer tous les nœuds avec leur degré et les trier par ordre décroissant
    # On utilise la méthode .degree(node) de votre classe
    nodes_sorted = sorted(graph.get_nodes(), key=lambda x: graph.degree(x), reverse=True)
    
    # Dictionnaire pour stocker le résultat {nœud: index_couleur}
    color_map = {}
    
    # 2. Initialiser la liste des couleurs disponibles
    current_color = 0
    
    # Tant qu'il reste des nœuds non colorés
    print(nodes_sorted)
    while len(color_map) < len(nodes_sorted):
        print(len(color_map),len(nodes_sorted))
        # On parcourt les nœuds dans l'ordre du tri
        for node in nodes_sorted:
            print(node)
            if node not in color_map:
                # Vérifier si aucun voisin n'a déjà la couleur actuelle
                can_color = True
                print(graph.get_all_adjacent(node))
                for neighbor in graph.get_all_adjacent(node):
                 
                    if color_map.get(neighbor) == current_color:
                       
                        can_color = False
                        break
                
                if can_color:
                    color_map[node] = current_color
        
        # Passer à la couleur suivante pour le prochain passage
        current_color += 1
        print(current_color)
    return color_map