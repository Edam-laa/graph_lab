"""
Welsh-Powell Graph Coloring Algorithm Test Suite

NOTES FOR DEVELOPMENT TEAM:
============================
1. TEST FIXTURES CONSOLIDATION
   - All test cases consolidated in data/welsh_powell_test_graphs.json
   - Format: {"graphs": {"case_name": {...graph_data...}, ...}}

2. ADAPTER PATTERN
   - load_wp_graph(case_name) adapter function:
     * Loads collection JSON
     * Extracts named test case
     * Wraps as {"graph": ...} for app/utils/file_loader.py
     * Returns Graph object via load_graph_from_json()
   - Original loader remains UNMODIFIED and immutable

3. ADDING NEW TEST CASES
   - Add entries to data/welsh_powell_test_graphs.json under "graphs" key
   - Use: graph = load_wp_graph("case_name")

4. WELSH-POWELL ALGORITHM
   - Returns dict with "coloring" (node -> color mapping)
   - Colors are typically 0, 1, 2, ... (integers)
   - Must satisfy: no two adjacent nodes have the same color
"""

import json
from pathlib import Path

import pytest

from app.algorithms.coloring import welsh_powell as wp_module
from app.core.graph import Graph
from app.utils.file_loader import load_graph_from_json


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
WP_CASES_FILE = DATA_DIR / "welsh_powell_test_graphs.json"


def load_wp_graph(case_name):
	"""Load a Welsh-Powell test case from the consolidated collection.
	
	Args:
		case_name (str): Name of the test case in welsh_powell_test_graphs.json
		
	Returns:
		Graph: Loaded and validated graph object
	"""
	with open(WP_CASES_FILE, "r", encoding="utf-8") as f:
		collection = json.load(f)

	graph_data = collection["graphs"][case_name]
	wrapped = {"graph": graph_data}
	return load_graph_from_json(wrapped)


def _is_valid_coloring(graph, coloring):
	"""Check if a coloring is valid for the given graph.
	
	A coloring is valid if:
	- All nodes in the graph are assigned a color
	- No two adjacent nodes have the same color
	
	Args:
		graph: Graph object
		coloring (dict): node -> color mapping
		
	Returns:
		bool: True if valid, False otherwise
	"""
	nodes = graph.get_nodes()
	edges = graph.get_edges()
	
	# Check all nodes are colored
	if not all(node in coloring for node in nodes):
		return False
	
	# Check no adjacent nodes have same color
	for u, v, _, _ in edges:
		if coloring[u] == coloring[v]:
			return False
	
	return True


def _get_chromatic_number(coloring):
	"""Get the chromatic number from a coloring.
	
	Args:
		coloring (dict): node -> color mapping
		
	Returns:
		int: Number of colors used
	"""
	if not coloring:
		return 0
	return max(coloring.values()) + 1


def _get_coloring_result(result):
	"""Normalize Welsh-Powell output to a plain node->color mapping."""
	if isinstance(result, dict) and "coloring" in result and isinstance(result["coloring"], dict):
		return result["coloring"]
	return result


# ============================================================================
# BASIC FUNCTIONALITY TESTS
# ============================================================================

def test_empty_graph():
	"""Empty graph requires 0 colors."""
	graph = load_wp_graph("empty")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert isinstance(result, dict)
	assert coloring == {}
	assert _get_chromatic_number(coloring) == 0


def test_single_vertex():
	"""Single vertex requires 1 color."""
	graph = load_wp_graph("single_vertex")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 1


def test_two_vertices_no_edge():
	"""Two isolated vertices require 1 color."""
	graph = load_wp_graph("two_vertices_no_edge")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 1


def test_single_edge():
	"""Two vertices with one edge require 2 colors."""
	graph = load_wp_graph("single_edge")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 2


# ============================================================================
# COMPLETE GRAPHS
# ============================================================================

def test_complete_k3():
	"""Complete graph K_3 (triangle) requires 3 colors."""
	graph = load_wp_graph("complete_k3")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 3


def test_complete_k4():
	"""Complete graph K_4 requires 4 colors."""
	graph = load_wp_graph("complete_k4")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 4


# ============================================================================
# BIPARTITE GRAPHS
# ============================================================================

def test_complete_bipartite_k33():
	"""Complete bipartite K_{3,3} requires 2 colors."""
	graph = load_wp_graph("complete_bipartite_k33")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 2


def test_incomplete_bipartite():
	"""Incomplete bipartite graph requires 2 colors."""
	graph = load_wp_graph("incomplete_bipartite")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 2


# ============================================================================
# SPECIAL GRAPH STRUCTURES
# ============================================================================

def test_star_graph():
	"""Star graph with n leaves requires 2 colors."""
	graph = load_wp_graph("star_graph")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 2


def test_path_graph():
	"""Path graph requires 2 colors."""
	graph = load_wp_graph("path_graph")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 2


def test_cycle_even():
	"""Even cycle requires 2 colors."""
	graph = load_wp_graph("cycle_even")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 2


def test_cycle_odd():
	"""Odd cycle (triangle) requires 3 colors."""
	graph = load_wp_graph("cycle_odd")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 3


# ============================================================================
# DISCONNECTED GRAPHS
# ============================================================================

def test_disconnected_two_components():
	"""Disconnected graph with two edges requires 2 colors."""
	graph = load_wp_graph("disconnected_two_components")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 2


def test_disconnected_different_sizes():
	"""Disconnected graph with components of different sizes."""
	graph = load_wp_graph("disconnected_different_sizes")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	# Triangle requires 3 colors, dominates
	assert _get_chromatic_number(coloring) == 3


# ============================================================================
# REGULAR AND DEGREE-BASED TESTS
# ============================================================================

def test_regular_graph_3():
	"""3-regular graph requires 4 colors."""
	graph = load_wp_graph("regular_graph_3")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	# This is K_4, requires 4 colors
	assert _get_chromatic_number(coloring) == 4


def test_identical_degrees():
	"""All vertices with identical degree (tie-break case)."""
	graph = load_wp_graph("identical_degrees")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 2


def test_multiple_max_degree():
	"""Multiple vertices with maximum degree."""
	graph = load_wp_graph("multiple_max_degree")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 2


# ============================================================================
# CHALLENGE CASES
# ============================================================================

def test_order_dependent():
	"""Graph where processing order affects coloring quality."""
	graph = load_wp_graph("order_dependent")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 3


def test_bad_greedy_choice():
	"""Graph where greedy choice impacts coloring."""
	graph = load_wp_graph("bad_greedy_choice")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 3


def test_dense_non_complete():
	"""Dense but not complete graph."""
	graph = load_wp_graph("dense_non_complete")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 4


def test_sparse_graph():
	"""Sparse graph with few edges."""
	graph = load_wp_graph("sparse_graph")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 2


def test_isolated_vertex():
	"""Graph with isolated vertex."""
	graph = load_wp_graph("isolated_vertex")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 3


# ============================================================================
# STRESS AND ROBUSTNESS TESTS
# ============================================================================

def test_large_complete_k10():
	"""Stress test with complete graph K_10."""
	graph = load_wp_graph("large_complete_k10")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	assert _is_valid_coloring(graph, coloring)
	assert _get_chromatic_number(coloring) == 10


# ============================================================================
# ALGORITHM PROPERTIES AND STRUCTURE
# ============================================================================

def test_result_structure():
	"""Test that result has expected structure."""
	graph = load_wp_graph("single_edge")
	result = wp_module.welsh_powell(graph)
	
	assert isinstance(result, dict)
	assert "coloring" in result
	assert "steps" in result
	coloring = result["coloring"]
	assert all(node in coloring for node in graph.get_nodes())
	assert all(isinstance(color, int) for color in coloring.values())


def test_all_nodes_colored():
	"""Verify all nodes receive a color."""
	graph = load_wp_graph("complete_k4")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	nodes = graph.get_nodes()
	
	assert all(node in coloring for node in nodes)


def test_colors_are_non_negative_integers():
	"""Verify colors are non-negative integers."""
	graph = load_wp_graph("complete_k3")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	for node, color in coloring.items():
		assert isinstance(color, int)
		assert color >= 0


def test_colors_sequential():
	"""Verify colors are sequential (0, 1, 2, ...)."""
	graph = load_wp_graph("complete_k4")
	result = wp_module.welsh_powell(graph)
	coloring = _get_coloring_result(result)
	
	colors_used = set(coloring.values())
	max_color = max(colors_used) if colors_used else -1
	expected_colors = set(range(max_color + 1))
	
	assert colors_used == expected_colors


# ============================================================================
# EDGE CASE VALIDATION
# ============================================================================

def test_coloring_validity_comprehensive():
	"""Comprehensive validation of coloring validity across all test cases."""
	test_cases = [
		"empty",
		"single_vertex",
		"two_vertices_no_edge",
		"single_edge",
		"complete_k3",
		"complete_k4",
		"complete_bipartite_k33",
		"star_graph",
		"path_graph",
		"cycle_even",
		"cycle_odd",
	]
	
	for case_name in test_cases:
		graph = load_wp_graph(case_name)
		result = wp_module.welsh_powell(graph)
		coloring = _get_coloring_result(result)
		
		assert _is_valid_coloring(graph, coloring), f"Invalid coloring for {case_name}"


def test_coloring_with_metadata_chromatic_number():
	"""Compare result against expected chromatic number in metadata (where available)."""
	cases_with_chromatic = [
		("single_vertex", 1),
		("single_edge", 2),
		("complete_k3", 3),
		("complete_k4", 4),
		("complete_bipartite_k33", 2),
		("star_graph", 2),
		("path_graph", 2),
		("cycle_even", 2),
		("cycle_odd", 3),
	]
	
	for case_name, expected_chromatic in cases_with_chromatic:
		graph = load_wp_graph(case_name)
		result = wp_module.welsh_powell(graph)
		coloring = _get_coloring_result(result)
		chromatic = _get_chromatic_number(coloring)
		
		assert chromatic == expected_chromatic, \
			f"{case_name}: expected {expected_chromatic} colors, got {chromatic}"


def test_directed_graph_is_rejected():
	graph = Graph(directed=True)
	graph.add_edge("A", "B", 1)
	graph.add_edge("B", "C", 1)

	with pytest.raises(ValueError):
		wp_module.welsh_powell(graph)


def test_self_loop_is_rejected():
	graph = Graph(directed=False)
	graph.add_edge("A", "A", 1)
	graph.add_edge("A", "B", 1)

	with pytest.raises(ValueError):
		wp_module.welsh_powell(graph)
