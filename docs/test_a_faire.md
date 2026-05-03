Validations communes (tous les algorithmes)

Schéma d’entrée: vérifier que nodes est une liste et edges est une liste, chaque arête a from/to (string) et weight/capacity sont numériques ou absents.
Graph non vide: lever ValueError si aucun nœud (ou documenter l’acceptation explicite).
Références valides: toutes les arêtes pointent vers des nœuds existants — sinon ValueError.
Types cohérents: nœuds (str), poids/capacités (int/float) — sinon TypeError/ValueError.
Pas de modification du graphe: algorithme ne doit pas muter graph.adj_list (vérifier par deep-copy snapshot).
Déterminisme: itérations sur nœuds / arêtes dans un ordre stable (trier si nécessaire).
Self-loop policy: définir explicitement si u==v est accepté ; si rejet, lever ValueError.
Format d’erreur explicite: exceptions claires (ValueError("...")) pour permettre assertions de tests.
bellman_ford / bellman

Source existante: lever ValueError si source absent.
Target existante (optionnel): si tests exigent validation, lever ValueError si target absent.
Poids numériques: accepter négatifs; valider type.
Détection cycle négatif: passe finale standard (si une arête est encore relaxable -> ValueError("Negative cycle detected")).
Graphe vide: lever ValueError.
Immuabilité: ne pas modifier structure d’entrée.
dijkstra

Source existante.
Pas de poids négatifs: lever ValueError si une arête a weight < 0.
Poids numériques.
Graphe non vide.
Comportement pour nœud inconnu: documenter s’il faut lever ou ajouter clé (recommander lever).
kruskal / prim (MST)

Graphe non vide.
Type d’arêtes: poids numériques.
Graphe non orienté: vérifier directed==False ou adapter l’algorithme; sinon lever ValueError ou convertir.
Self-loops interdits (par défaut) — lever ValueError.
Gestion graphe non connecté: définir si retourner forêt (ok) ou lever erreur; tester les deux cas.
ford_fulkerson / flux

Source et sink valides et distincts: lever ValueError.
Capacités présentes: chaque arête a capacity numérique ≥ 0.
Pas de capacités négatives: lever ValueError.
Graphe dirigé / sens attendu: valider flag directed selon implémentation.
Pré-check chemin possible: optionnel — warning si aucun chemin initial (retourner 0 flux).
connected_components

Schéma valide.
Graphe non vide: ou accepter et retourner [] selon politique.
Ignore orientation: préciser si on traite comme non‑orienté (test).
Nœuds isolés: doivent apparaître comme composantes singleton.
strongly_connected / SCC

Graphe dirigé: recommander valider directed==True ou documenter comportement.
Schéma valide.
Graphe non vide: ou accepter [].
eulerian_path / eulerian_path.py

Schéma valide.
Conditions de degré: vérifier conditions nécessaires (degrés entrants/sortants pour dirigé, paire de sommets à degré impair pour non-dirigé).
Connectivité sur sous‑graphe non zéro-degré: tous sommets à degré>0 doivent être (fortement) connectés.
Self-loop: préciser si comptée comme degré; valider selon politique.
Retour d’erreur clair: ValueError("No Eulerian path").
welsh_powell / coloration

Graph non orienté: valider directed==False.
Aucune self-loop: sinon lever ValueError.
Nœuds bien définis.
Optionnel: limite max de couleurs (si fournie) et vérification.
Autres validations utilitaires (Graph/core/loader)

Loader stricte: file_loader.py doit valider schéma minimal et repasser erreurs explicites (KeyError -> ValueError avec message).
Unique node ids: détecter doublons dans nodes.
Edges duplicates: policy (autoriser/filtrer).
API stable: méthodes get_nodes(), get_edges() doivent retourner ordres stables (triés) pour tests déterministes.
Exposition d’infos pour tests: exposer graph.has_negative_weights() et graph.get_edges() (déjà présent) pour validations.
Tests à ajouter (recommandés, par validation)

Loader malformed: missing from/to, non-list nodes → assert exception.
Empty graph: appeler chaque algo et assert ValueError (ou comportement documenté).
Missing source/target: Dijkstra/Bellman/Ford → assert ValueError.
Negative-cycle reachable vs unreachable: Bellman → reachable raise, unreachable not raise (documenter).
Negative weight for Dijkstra: assert raise.
Non‑negative cycles accepted: If policy standard, assert non-negative cycles do NOT raise (else inverse).
Capacity negative: Ford-Fulkerson raises.
Graph immutability deep: check no mutation to nested lists/tuples.
Large-graph smoke: performance baseline (sparse and dense).