## Plus court chemin

### Dijkstra

* Graphe pondéré (sinon trivial)
* Tous les poids ≥ 0
* Peut être orienté ou non
* Connexité non obligatoire (il calcule juste pour la composante atteignable)

> Pourquoi cette condition ?
>> Parce que Dijkstra “fige” une distance comme optimale. Si un poids négatif existe, une meilleure route peut apparaître plus tard → erreur."

### Bellman-Ford

* Graphe pondéré
* Poids peuvent être négatifs
* Pas de cycle de poids négatif accessible depuis la source
* Orienté ou non

> Bonus :
>> Permet de détecter un cycle négatif

### Bellman (DAG / sans circuit)

* Graphe orienté acyclique (DAG)
* Poids quelconques (positifs, négatifs, peu importe)
* Nécessite un ordre topologique

> Pourquoi c’est puissant ?
>> Parce que l’absence de cycles élimine tout risque de contradiction → calcul en une seule passe.

## Arbre couvrant minimum (MST)

### Kruskal

Graphe non orienté
Graphe connexe (sinon → forêt couvrante)
Graphe pondéré
Pas de contrainte sur les poids (peuvent être négatifs)

Condition clé implicite :

Il faut pouvoir tester les cycles (Union-Find en pratique)

### Prim

Graphe non orienté
Graphe connexe
Graphe pondéré
Poids quelconques

### Différence conceptuelle :

Kruskal = approche globale (tri des arêtes)
Prim = croissance locale (comme Dijkstra mais pour MST)

## Connexité

### Composantes connexes (CC)

* Graphe non orienté

### Composantes fortement connexes (CFC)

* Graphe orienté

#### Condition implicite :

Nécessite parcours type DFS/BFS (ou Kosaraju/Tarjan en pratique)
## Eulerien

### Chaîne eulérienne

* Graphe connexe
* Exactement 2 sommets de degré impair

### Circuit eulérien

* Graphe connexe
* Tous les sommets de degré pair
## Coloration

### Welsh-Powell (coloration des sommets)

* Graphe quelconque
* Non orienté en général (ou orienté ignoré comme non orienté)

#### Condition importante :

* C’est heuristique, pas optimal garanti

### Coloration des arêtes (Vizing)

* Graphe non orienté
* Résultat théorique :
`nombre de couleurs = Δ(G) ou Δ(G)+1`
## Flot maximum

### Ford-Fulkerson

* Graphe orienté
* Capacités ≥ 0
* Source et puits définis
* Pas de contrainte de connexité stricte

### Attention pratique :

* Peut ne pas terminer si capacités réelles (version naïve)
* Edmonds-Karp garantit terminaison (BFS)