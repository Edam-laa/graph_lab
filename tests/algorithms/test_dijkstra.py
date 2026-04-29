"""
Dijkstra Algorithm Test Suite

NOTES FOR DEVELOPMENT TEAM:
============================
1. TEST FIXTURES CONSOLIDATION
   - All test cases are now consolidated in data/dijkstra_test_graphs.json
   - Individual fixture files (simple_graph.json, etc.) have been removed
   - Format: {"graphs": {"case_name": {...graph_data...}, ...}}

2. ADAPTER PATTERN
   - load_dijkstra_graph(case_name) is an adapter function that:
     a) Loads the collection JSON
     b) Extracts the named test case
     c) Wraps it as {"graph": ...} for the original file_loader.py
     d) Returns a Graph object via load_graph_from_json()
   
   - This adapter DOES NOT modify app/utils/file_loader.py
   - The original loader remains immutable and only accepts:
     * String filepath (to load from file)
     * Dict with {"graph": {...}} structure (to load from dict)

3. ADDING NEW TEST CASES
   - Add new entries to data/dijkstra_test_graphs.json under "graphs" key
   - Follow this structure:
     {
       "case_name": {
         "nodes": ["A", "B", "C", ...],
         "edges": [{"id": "e1", "from": "A", "to": "B", "weight": 1, "capacity": null}, ...],
         "directed": true|false,
         "metadata": {"name": "...", "description": "...", "allow_negative_weights": false}
       }
     }
   - Then reference with: graph = load_dijkstra_graph("case_name")

4. CURRENT TEST COVERAGE (23 cases)
   Simple paths, multiple paths, tie-breaking, multi-edges, self-loops,
   large weights, star hub topology, relaxation order, dead nodes,
   indirect vs direct paths, directed/undirected graphs, negative weights,
   empty graph, single vertex, disconnected, cycle, zero weights, etc.

5. MIGRATION COMPLETE
   - Original file_loader.py: UNCHANGED ✓
   - Test structure: ADAPTED to work with immutable loader ✓
   - Fixture organization: CONSOLIDATED to single collection ✓
   - Data directory: CLEANED UP (33 individual files deleted) ✓
"""

import json
import math

import pytest

from app.algorithms.shortest_path.dijkstra import dijkstra, reconstruct_path
from app.core.graph import Graph
from app.utils.file_loader import load_graph_from_json


DIJKSTRA_CASES_FILE = "data/dijkstra_test_graphs.json"


def load_dijkstra_graph(case_name):
    """Load a Dijkstra test case from the consolidated collection.
    
    Args:
        case_name (str): Name of the test case in dijkstra_test_graphs.json
        
    Returns:
        Graph: Loaded and validated graph object
        
    Implementation:
        1. Loads dijkstra_test_graphs.json collection
        2. Extracts named case from "graphs" dict
        3. Wraps as {"graph": ...} for the original file_loader
        4. Passes to load_graph_from_json() which returns Graph object
    """
    with open(DIJKSTRA_CASES_FILE, "r") as f:
        collection = json.load(f)
    
    graph_data = collection["graphs"][case_name]
    wrapped = {"graph": graph_data}
    return load_graph_from_json(wrapped)


def build_sparse_performance_graph(node_count=1000):
    graph = Graph(directed=True)

    for index in range(node_count):
        graph.add_node(f"N{index}")

    for index in range(node_count - 1):
        graph.add_edge(f"N{index}", f"N{index + 1}", 1)

    return graph


def test_dijkstra_simple():
    graph = load_dijkstra_graph("simple")
    result = dijkstra(graph, start="A")

    assert result["distances"]["C"] == 3
    assert reconstruct_path(result["previous"], "A", "C") == ["A", "B", "C"]


def test_dijkstra_multiple_paths_choose_shortest():
    graph = load_dijkstra_graph("multiple_paths")
    result = dijkstra(graph, start="A")

    assert result["distances"]["D"] == 3
    assert reconstruct_path(result["previous"], "A", "D") == ["A", "C", "D"]


def test_dijkstra_tie_breaking_is_deterministic():
    graph = load_dijkstra_graph("tie_breaking")
    result = dijkstra(graph, start="A")

    assert result["distances"]["D"] == 3
    assert reconstruct_path(result["previous"], "A", "D") == ["A", "B", "D"]
    assert result["previous"]["D"] == "B"


def test_dijkstra_multiple_edges_choose_minimum_weight_edge():
    graph = load_dijkstra_graph("multi_edges")
    result = dijkstra(graph, start="A")

    assert result["distances"]["B"] == 2
    assert result["distances"]["C"] == 3
    assert reconstruct_path(result["previous"], "A", "C") == ["A", "B", "C"]


def test_dijkstra_self_loop_does_not_change_source_distance():
    graph = load_dijkstra_graph("self_loop")
    result = dijkstra(graph, start="A")

    assert result["distances"]["A"] == 0
    assert result["distances"]["C"] == 2
    assert reconstruct_path(result["previous"], "A", "C") == ["A", "B", "C"]


def test_dijkstra_large_weights_remain_stable():
    graph = load_dijkstra_graph("large_weights")
    result = dijkstra(graph, start="A")

    assert result["distances"]["C"] == 2000000000
    assert reconstruct_path(result["previous"], "A", "C") == ["A", "B", "C"]


def test_dijkstra_star_hub_graph():
    graph = load_dijkstra_graph("star_hub")
    result = dijkstra(graph, start="A")

    assert result["distances"]["Hub"] == 1
    assert result["distances"]["B"] == 3
    assert result["distances"]["C"] == 4
    assert result["distances"]["D"] == 5
    assert reconstruct_path(result["previous"], "A", "F") == ["A", "Hub", "F"]


def test_dijkstra_relaxation_order_updates_later_distance():
    graph = load_dijkstra_graph("relaxation_order")
    result = dijkstra(graph, start="A")

    assert result["distances"]["C"] == 2
    assert reconstruct_path(result["previous"], "A", "C") == ["A", "B", "C"]
    assert result["previous"]["C"] == "B"


def test_dijkstra_dead_nodes_are_ignored():
    graph = load_dijkstra_graph("dead_nodes")
    result = dijkstra(graph, start="A")

    assert result["distances"]["C"] == 3
    assert math.isinf(result["distances"]["X"])
    assert math.isinf(result["distances"]["Y"])
    assert math.isinf(result["distances"]["Z"])
    assert reconstruct_path(result["previous"], "A", "Z") == []


def test_dijkstra_directed_graph_respects_edge_direction():
    graph = load_dijkstra_graph("directed")
    result = dijkstra(graph, start="B")

    assert math.isinf(result["distances"]["A"])
    assert reconstruct_path(result["previous"], "B", "A") == []


def test_dijkstra_undirected_graph():
    graph = load_dijkstra_graph("undirected")
    result = dijkstra(graph, start="A")

    assert result["distances"]["C"] == 3
    assert reconstruct_path(result["previous"], "A", "C") == ["A", "B", "C"]


def test_dijkstra_sum_of_weights_is_correct():
    graph = load_dijkstra_graph("sum_weights")
    result = dijkstra(graph, start="A")

    assert result["distances"]["C"] == 7
    assert reconstruct_path(result["previous"], "A", "C") == ["A", "B", "C"]


def test_dijkstra_source_equals_destination():
    graph = load_dijkstra_graph("simple")
    result = dijkstra(graph, start="A")

    assert result["distances"]["A"] == 0
    assert reconstruct_path(result["previous"], "A", "A") == ["A"]


def test_dijkstra_single_vertex_graph():
    graph = load_dijkstra_graph("single_vertex")
    result = dijkstra(graph, start="A")

    assert result["distances"]["A"] == 0
    assert reconstruct_path(result["previous"], "A", "A") == ["A"]


def test_dijkstra_disconnected_graph_no_path():
    graph = load_dijkstra_graph("disconnected")
    result = dijkstra(graph, start="A")

    assert math.isinf(result["distances"]["D"])
    assert reconstruct_path(result["previous"], "A", "D") == []


def test_dijkstra_valid_graph_without_path_between_two_nodes():
    graph = load_dijkstra_graph("valid_no_path")
    result = dijkstra(graph, start="A")

    assert math.isinf(result["distances"]["D"])
    assert reconstruct_path(result["previous"], "A", "D") == []


def test_dijkstra_cycles_do_not_cause_infinite_loop():
    graph = load_dijkstra_graph("cycle")
    result = dijkstra(graph, start="A")

    assert result["distances"]["D"] == 3
    assert reconstruct_path(result["previous"], "A", "D") == ["A", "B", "C", "D"]


def test_dijkstra_negative_weights_raise_error():
    graph = load_dijkstra_graph("negative_weights")

    with pytest.raises(ValueError):
        dijkstra(graph, start="A")


def test_dijkstra_source_vertex_missing():
    graph = load_dijkstra_graph("simple")

    with pytest.raises(ValueError):
        dijkstra(graph, start="Z")


def test_dijkstra_empty_graph():
    graph = load_dijkstra_graph("empty")

    with pytest.raises(ValueError):
        dijkstra(graph, start="A")


def test_dijkstra_zero_weight_edges():
    graph = load_dijkstra_graph("zero_weights")
    result = dijkstra(graph, start="A")

    assert result["distances"]["C"] == 0
    assert reconstruct_path(result["previous"], "A", "C") == ["A", "B", "C"]


def test_dijkstra_output_structure_is_coherent():
    graph = load_dijkstra_graph("simple")
    result = dijkstra(graph, start="A")

    assert "distances" in result
    assert "previous" in result
    assert "steps" in result
    assert isinstance(result["distances"], dict)
    assert isinstance(result["previous"], dict)
    assert isinstance(result["steps"], list)
    assert result["distances"]["C"] == 3


def test_dijkstra_light_performance_sparse_graph():
    graph = build_sparse_performance_graph()
    result = dijkstra(graph, start="N0")

    assert result["distances"]["N999"] == 999
    path = reconstruct_path(result["previous"], "N0", "N999")
    assert path[0] == "N0"
    assert path[-1] == "N999"