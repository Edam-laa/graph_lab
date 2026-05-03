# Result Window Feature - Complete Guide

## Overview
Your GraphAlgo Pro application now automatically displays a **Result Window** when you click an algorithm button. This window shows the algorithm results with a visual representation of the graph and detailed execution information.

## How It Works

### Step 1: Prepare Your Graph
1. Run the frontend: `python -m front.Main`
2. Create a graph by:
   - Adding nodes with "Add Node" button (◉)
   - Connecting them with "Add Edge" button (—)
   - Or load an existing graph with "⬇ Export JSON"

### Step 2: Configure Algorithm Parameters
In the bottom bar, you can optionally set:
- **Source**: Starting node (e.g., "A")
- **Target**: Ending node (e.g., "Z")
- Select graph type: **Directed** (⟶), **Weighted** (⚖), **Capacity** (📦)

### Step 3: Run an Algorithm
Click any algorithm button:
- 🔵 **Shortest Path**: Dijkstra, Bellman-Ford, Bellman
- 🔵 **Spanning Tree**: Kruskal, Prim
- 🔵 **Connectivity**: Composantes Connexes
- 🔵 **Eulerian**: Chemin Eulérien
- 🔵 **Coloring**: Welsh-Powell

### Step 4: Backend Processing
The application automatically:
1. Collects your graph data
2. Sends it to the backend server (`http://127.0.0.1:5000/run-algorithm`)
3. Backend processes the algorithm
4. Returns results

### Step 5: Result Window Opens Automatically
The **ResultWindow** appears with:

#### Left Panel - Graph Visualization
- Graph rendered with algorithm results highlighted
- Color-coded nodes/edges based on algorithm type:
  - 🟢 **Green**: Source node
  - 🟠 **Orange**: Path nodes
  - 🔴 **Red**: Target/sink node
  - 🟡 **Yellow**: MST edges
  - 🔵 **Blue**: Traversal edges
  - 🟣 **Purple**: Flow edges
  - 🎨 **Colors**: Coloring algorithm results

#### Right Panel - Algorithm Details
Shows four key information groups:

1. **Result Summary**
   - Algorithm name
   - Status (success/error)
   - Time complexity
   - Execution time (milliseconds)
   - Found path (if applicable)
   - Total cost/distance

2. **Distances from Source** (for shortest path algorithms)
   - Table showing distance to each node
   - Highlighted rows for nodes in the path

3. **Execution Steps**
   - Detailed log of algorithm steps
   - Useful for understanding how the algorithm works

4. **Toolbar**
   - "Load JSON" button: Load a previously saved result
   - Algorithm badge: Shows algorithm name

## Example: Running Dijkstra's Algorithm

```
1. Create nodes: A, B, C, D, Z
2. Add edges with weights:
   A → B (4), A → C (2), B → D (5)
   C → B (1), C → D (8), D → Z (3)
3. Set Source = "A", Target = "Z"
4. Click "Dijkstra" button
5. Backend calculates shortest path
6. ResultWindow opens showing:
   - Path: A → C → B → D → Z (distance 12)
   - All nodes highlighted by their role
   - Distance table for each node
```

## Features of ResultWindow

✅ **Automatic Display**: Opens after algorithm execution
✅ **Visual Feedback**: Color-coded path highlighting
✅ **Execution Metrics**: Time, complexity, status
✅ **Step-by-Step Log**: See algorithm execution details
✅ **Distance Tables**: Compare distances to all nodes
✅ **Error Handling**: Shows errors if algorithm fails
✅ **JSON Export**: Save results to JSON file
✅ **Resizable**: Drag divider between graph and info panel

## Troubleshooting

### Issue: Result Window doesn't appear
**Solution**: 
- Check if server is running: `python server.py`
- Check terminal for error messages
- Verify graph has at least 2 nodes

### Issue: Backend error
**Solution**:
- Ensure algorithm parameters are valid
- Check source/target nodes exist in graph
- Verify graph is appropriate for algorithm (e.g., positive weights for Dijkstra)

### Issue: Result Window shows wrong graph
**Solution**:
- This is normal for shortest-path algorithms - only path nodes/edges are shown
- Load the full JSON to see complete graph

## Technical Details

### Backend Response Format
```json
{
  "result": {
    "path": ["A", "C", "B", "D"],
    "distances": {"A": 0, "B": 3, "C": 2, "D": 8},
    "steps": ["Step 1", "Step 2", ...],
    "mst_edges": [], // for MST algorithms
    "coloring": {}, // for coloring algorithms
    "traversal": {} // for traversal algorithms
  },
  "execution": {
    "status": "success",
    "execution_time": 0.0045,
    "complexity": "O((V + E) log V)"
  }
}
```

### File Locations
- Frontend: `front/MainWindow.py`, `front/ResultWindow.py`
- Backend: `server.py`, `app/services/graph_service.py`
- Sample graphs: `data/*.json`

## Next Steps

1. **Test different algorithms** to see how they display
2. **Experiment with different graph sizes** to see performance
3. **Export results** as JSON for analysis
4. **Create your own graphs** using the editor

Happy graphing! 🎉
