# GraphAlgo Pro

Plateforme Python d'expérimentation et de visualisation des algorithmes de graphes, développée par l'équipe **GrafixLab**.

GraphAlgo Pro combine un backend algorithmique, un serveur Flask et une interface graphique PySide6 afin de permettre la création de graphes, l'exécution d'algorithmes classiques et l'affichage visuel des résultats.

---

## 1. Présentation du projet

GraphAlgo Pro est un projet académique orienté expérimentation, démonstration et intégration logicielle autour des graphes.

L'application permet de :

- construire un graphe depuis une interface graphique
- gérer les graphes orientés et non orientés
- travailler avec des poids et des capacités
- exécuter plusieurs familles d'algorithmes
- visualiser les résultats dans une fenêtre dédiée
- lancer des tests sur le backend et les composants principaux

---

## 2. Équipe

**Nom de l'équipe : GrafixLab**

Le projet a été conçu comme une plateforme commune réunissant :

- une partie backend pour les algorithmes
- une partie frontend pour l'édition et la visualisation
- une couche serveur pour la communication
- une base de tests pour la validation

---

## 3. Fonctionnalités principales

- Édition graphique d'un graphe avec sommets et arêtes
- Support des graphes orientés / non orientés
- Support des poids et des capacités
- Exécution des algorithmes depuis l'interface
- Affichage des résultats de calcul
- Visualisation des chemins, arbres, couleurs et propriétés
- Mesure du temps d'exécution
- Affichage de la complexité et des étapes de traitement
- Packaging en exécutables Windows via PyInstaller

---

## 4. Algorithmes implémentés

### Plus court chemin

- Dijkstra
- Bellman-Ford
- Bellman

### Arbre couvrant minimum

- Kruskal
- Prim

### Connexité

- Composantes connexes
- Composantes fortement connexes

### Parcours

- BFS
- DFS

### Autres algorithmes

- Chemin eulérien
- Circuit eulérien
- Welsh-Powell
- Ford-Fulkerson

---

## 5. Technologies utilisées

- **Python 3** pour le cœur du projet
- **Flask** pour le serveur backend
- **PySide6** pour l'interface graphique
- **requests** pour les appels HTTP du frontend vers le backend
- **pytest** pour les tests
- **PyInstaller** pour la génération des exécutables

---

## 6. Structure du projet

```text
graph_lab/
├── app/
│   ├── algorithms/
│   │   ├── coloring/
│   │   ├── connectivity/
│   │   ├── eulerian/
│   │   ├── flow/
│   │   ├── shortest_path/
│   │   ├── spanning_tree/
│   │   └── traversal/
│   ├── core/
│   ├── services/
│   └── utils/
├── front/
│   ├── theme/
│   ├── widgets/
│   ├── Main.py
│   ├── MainWindow.py
│   ├── GraphScene.py
│   ├── GraphView.py
│   ├── NodeItem.py
│   ├── EdgeItem.py
│   ├── ResultWindow.py
│   ├── WeightDialog.py
│   ├── Algobtn.py
│   └── Toolbtn.py
├── data/
├── tests/
│   ├── algorithms/
│   └── core/
├── dist/
│   ├── GraphAlgoPro_Server.exe
│   └── GraphAlgoPro_Front.exe
├── build/
├── server.py
├── main.py
├── requirements.txt
├── GraphAlgoPro_Server.spec
├── GraphAlgoPro_Front.spec
├── instructions_execution.txt
├── Structure.md
└── EXPLICATION.md
```

### Rôle des principaux éléments

| Élément | Rôle |
|---|---|
| `app/core/graph.py` | structure principale du graphe |
| `app/algorithms/` | implémentation des algorithmes |
| `app/services/graph_service.py` | orchestration de l'exécution des algorithmes |
| `app/utils/file_loader.py` | conversion JSON vers objet `Graph` |
| `server.py` | serveur Flask et point d'entrée backend |
| `front/Main.py` | point d'entrée du frontend |
| `front/MainWindow.py` | fenêtre principale de l'application |
| `front/ResultWindow.py` | affichage du résultat |
| `data/` | jeux de données JSON |
| `tests/` | tests unitaires et de validation |
| `dist/` | exécutables générés |

---

## 7. Installation depuis GitHub

Clonez le dépôt, puis placez-vous à la racine du projet.

```bash
git clone <URL_DU_DEPOT>
cd graph_lab
```

Si vous avez cloné un dépôt parent contenant ce dossier, adaptez simplement le `cd` au chemin réel.

---

## 8. Création d'un environnement virtuel

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Windows CMD

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 9. Installation des dépendances

Installez les dépendances depuis `requirements.txt` :

```bash
pip install -r requirements.txt
```

Le fichier recense les bibliothèques principales du projet :

- Flask
- flask-cors
- PySide6
- requests
- pytest
- pyinstaller

---

## 10. Lancement du backend

Le backend doit être démarré **avant** le frontend.

```bash
python server.py
```

Le serveur Flask écoute localement sur :

```text
http://127.0.0.1:5000
```

---

## 11. Lancement du frontend

Dans un second terminal, après le démarrage du serveur :

```bash
python -m front.Main
```

Le frontend PySide6 s'ouvre et peut alors envoyer les requêtes au backend.

---

## 12. Utilisation avec les exécutables

Le projet contient déjà deux exécutables générés dans `dist/` :

- `GraphAlgoPro_Server.exe`
- `GraphAlgoPro_Front.exe`

### Ordre de lancement

Le lancement doit se faire dans cet ordre :

1. `GraphAlgoPro_Server.exe`
2. `GraphAlgoPro_Front.exe`

### Exemple PowerShell

```powershell
.\dist\GraphAlgoPro_Server.exe
```

Puis, dans un second terminal :

```powershell
.\dist\GraphAlgoPro_Front.exe
```

Le serveur doit être actif avant l'ouverture du frontend, exactement comme en mode Python.

---

## 13. Exemple d'utilisation rapide

### En mode développement

Terminal 1 :

```bash
python server.py
```

Terminal 2 :

```bash
python -m front.Main
```

### Ensuite

1. Créez quelques sommets.
2. Ajoutez des arêtes ou des arcs.
3. Renseignez la source et la destination si nécessaire.
4. Cliquez sur un algorithme.
5. Consultez la fenêtre de résultat.

Vous pouvez par exemple :

- tester Dijkstra sur un graphe pondéré
- tester Kruskal ou Prim sur un graphe non orienté
- tester Welsh-Powell pour la coloration
- tester Ford-Fulkerson sur un réseau avec capacités

---

## 14. Tests avec pytest

Pour exécuter l'ensemble des tests du projet :

```bash
pytest -q tests/
```

Ou avec Python :

```bash
python -m pytest -q tests/
```

Les tests sont organisés en deux grands ensembles :

- `tests/algorithms/` pour les algorithmes
- `tests/core/` pour les composants centraux

---

## 15. Communication frontend / backend

Le frontend communique avec le backend via une requête HTTP locale :

```text
POST http://127.0.0.1:5000/run-algorithm
```

### Schéma simplifié

```text
Frontend PySide6
    ↓
server.py
    ↓
app/services/graph_service.py
    ↓
algorithme demandé
    ↓
résultat JSON
    ↓
ResultWindow.py
```

Le serveur traduit les noms d'algorithmes de l'interface, exécute le calcul et renvoie un résultat exploitable par le frontend.

---

## 16. Nettoyage / fichiers ignorés

Pour garder un dépôt propre, il est recommandé d'ignorer ou de nettoyer régulièrement :

- `.venv/`
- `.pytest_cache/`
- `__pycache__/`
- `*.pyc`
- `build/`

Le dossier `dist/` contient les exécutables générés.
Selon votre mode de livraison, vous pouvez :

- le conserver pour distribuer les `.exe`
- ou l'exclure du dépôt source si vous ne versionnez pas les binaires

---

## 17. Statut du projet

**Statut actuel : projet fonctionnel en local, avec interface graphique, serveur backend, jeux de tests et packaging Windows disponible.**

Le projet est adapté :

- à une démonstration académique
- à un livrable universitaire
- à un dépôt GitHub de présentation technique

---

## 18. Auteurs / équipe

Projet réalisé par l'équipe **GrafixLab**.

Répartition générale du travail :

- conception et intégration de la plateforme
- développement du backend algorithmique
- développement du frontend PySide6
- validation par les tests
- packaging et documentation

---

## 19. Lancement recommandé

Pour éviter toute erreur d'exécution :

1. démarrez toujours le **serveur** en premier
2. lancez ensuite le **frontend**
3. appliquez le même ordre pour les exécutables : **serveur puis frontend**

Commande locale recommandée :

```bash
python server.py
python -m front.Main
```
