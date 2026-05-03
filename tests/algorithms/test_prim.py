"""
Prim Algorithm Test Suite

NOTES FOR DEVELOPMENT TEAM:
============================
1. TEST FIXTURES CONSOLIDATION
   - All test cases consolidated in data/prim_test_graphs.json
   - Format: {"graphs": {"case_name": {...graph_data...}, ...}}

2. ADAPTER PATTERN
   - load_prim_graph(case_name) adapter function:
     * Loads collection JSON
     * Extracts named test case
     * Wraps as {"graph": ...} for app/utils/file_loader.py
     * Returns Graph object via load_graph_from_json()
   - Original loader remains UNMODIFIED and immutable

3. PRIM IMPLEMENTATION BEHAVIOR
   - Returns dict with keys:
     * "mst_edges": list of (u, v, weight) tuples
     * "total_weight": numeric total
     * "steps": list of trace messages
   - Raises ValueError for empty graphs, directed graphs, and disconnected graphs
"""

import json
from pathlib import Path

import pytest

from app.algorithms.spanning_tree import prim as prim_module
from app.core.graph import Graph
from app.utils.file_loader import load_graph_from_json


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
PRIM_CASES_FILE = DATA_DIR / "prim_test_graphs.json"


def load_prim_graph(case_name):
	"""Load a Prim test case from the consolidated collection.
	
	Args:
		case_name (str): Name of the test case in prim_test_graphs.json
	
	Returns:
		Graph: Loaded and validated graph object
	"""
	with open(PRIM_CASES_FILE, "r", encoding="utf-8") as f:
		collection = json.load(f)

	graph_data = collection["graphs"][case_name]
	wrapped = {"graph": graph_data}
	return load_graph_from_json(wrapped)


def _get_result_edges(result):
	assert isinstance(result, dict)
	assert "mst_edges" in result
	assert isinstance(result["mst_edges"], list)
	return result["mst_edges"]


def _get_total_weight(result):
	assert isinstance(result, dict)
	assert "total_weight" in result
	return result["total_weight"]


def _get_steps(result):
	assert isinstance(result, dict)
	assert "steps" in result
	assert isinstance(result["steps"], list)
	return result["steps"]


def _normalize_edge(edge):
	if isinstance(edge, dict):
		return edge["from"], edge["to"], edge["weight"]
	if isinstance(edge, (list, tuple)) and len(edge) == 3:
		return edge[0], edge[1], edge[2]
	raise AssertionError("each edge must be dict or 3-tuple")


def _contains_cycle(nodes, edges):
	parent = {node: node for node in nodes}
	rank = {node: 0 for node in nodes}

	def find(node):
		while parent[node] != node:
			parent[node] = parent[parent[node]]
			node = parent[node]
		return node

	def union(a, b):
		root_a = find(a)
		root_b = find(b)
		if root_a == root_b:
			return True
		if rank[root_a] < rank[root_b]:
			parent[root_a] = root_b
		elif rank[root_a] > rank[root_b]:
			parent[root_b] = root_a
		else:
			parent[root_b] = root_a
			rank[root_a] += 1
		return False

	for edge in edges:
		source, target, _ = _normalize_edge(edge)
		if union(source, target):
			return True
	return False


def _is_connected(nodes, edges):
	if not nodes:
		return True

	adjacency = {node: set() for node in nodes}
	for edge in edges:
		u, v, _ = _normalize_edge(edge)
		adjacency[u].add(v)
		adjacency[v].add(u)

	start = nodes[0]
	stack = [start]
	visited = set()

	while stack:
		node = stack.pop()
		if node in visited:
			continue
		visited.add(node)
		stack.extend(adjacency[node] - visited)

	return len(visited) == len(nodes)


def _snapshot_graph(graph):
	return {
		"nodes": list(graph.get_nodes()),
		"edges": list(graph.get_edges()),
		"directed": graph.directed,
	}


def _assert_graph_unchanged(graph, before_snapshot):
	after_snapshot = _snapshot_graph(graph)
	assert before_snapshot == after_snapshot


# ============================================================================
# BASIC FUNCTIONALITY TESTS
# ============================================================================

def test_empty_graph_raises():
	graph = load_prim_graph("empty")
	with pytest.raises(ValueError):
		prim_module.prim(graph)


def test_single_vertex_graph():
	graph = load_prim_graph("single_vertex")
	result = prim_module.prim(graph)

	edges = _get_result_edges(result)
	assert edges == []
	assert _get_total_weight(result) == 0
	assert _get_steps(result)


def test_two_vertices_connected():
	graph = load_prim_graph("two_vertices_with_edge")
	result = prim_module.prim(graph)

	edges = _get_result_edges(result)
	assert len(edges) == 1
	assert _get_total_weight(result) == 7
	assert not _contains_cycle(graph.get_nodes(), edges)
	assert _is_connected(graph.get_nodes(), edges)


def test_two_vertices_no_edge_raises():
	graph = load_prim_graph("two_vertices_no_edge")
	with pytest.raises(ValueError):
		prim_module.prim(graph)


# ============================================================================
# CONNECTIVITY BEHAVIOR
# ============================================================================

def test_non_connected_graph_raises():
	graph = load_prim_graph("non_connected_two_components")
	with pytest.raises(ValueError):
		prim_module.prim(graph)


def test_isolated_vertex_raises():
	graph = load_prim_graph("isolated_vertex")
	with pytest.raises(ValueError):
		prim_module.prim(graph)


def test_multiple_components_raises():
	graph = load_prim_graph("multiple_components")
	with pytest.raises(ValueError):
		prim_module.prim(graph)


# ============================================================================
# STANDARD MST CASES
# ============================================================================

def test_already_tree_graph():
	graph = load_prim_graph("connected_tree")
	result = prim_module.prim(graph)

	edges = _get_result_edges(result)
	assert len(edges) == len(graph.get_nodes()) - 1
	assert _get_total_weight(result) == 10
	assert not _contains_cycle(graph.get_nodes(), edges)
	assert _is_connected(graph.get_nodes(), edges)


def test_complete_k4():
	graph = load_prim_graph("complete_k4")
	result = prim_module.prim(graph)

	edges = _get_result_edges(result)
	assert len(edges) == len(graph.get_nodes()) - 1
	assert _get_total_weight(result) == 6
	assert not _contains_cycle(graph.get_nodes(), edges)
	assert _is_connected(graph.get_nodes(), edges)


def test_undirected_graph_standard_case():
	graph = load_prim_graph("undirected_graph")
	result = prim_module.prim(graph)

	edges = _get_result_edges(result)
	assert len(edges) == 3
	assert _get_total_weight(result) == 6
	assert not _contains_cycle(graph.get_nodes(), edges)
	assert _is_connected(graph.get_nodes(), edges)


def test_weighted_complete_graph():
	graph = load_prim_graph("weighted_complete_graph")
	result = prim_module.prim(graph)

	edges = _get_result_edges(result)
	assert len(edges) == len(graph.get_nodes()) - 1
	assert _get_total_weight(result) == 6
	assert not _contains_cycle(graph.get_nodes(), edges)
	assert _is_connected(graph.get_nodes(), edges)


def test_unique_mst_case():
	graph = load_prim_graph("unique_mst")
	result = prim_module.prim(graph)

	edges = _get_result_edges(result)
	assert len(edges) == 3
	assert _get_total_weight(result) == 6
	assert not _contains_cycle(graph.get_nodes(), edges)
	assert _is_connected(graph.get_nodes(), edges)


def test_already_mst_valid():
	graph = load_prim_graph("already_mst_valid")
	result = prim_module.prim(graph)

	edges = _get_result_edges(result)
	assert len(edges) == len(graph.get_nodes()) - 1
	assert _get_total_weight(result) == 6
	assert not _contains_cycle(graph.get_nodes(), edges)
	assert _is_connected(graph.get_nodes(), edges)


# ============================================================================
# GRAPH SHAPE AND EDGE-WEIGHT BEHAVIOR
# ============================================================================

def test_dense_non_complete_graph():
	graph = load_prim_graph("dense_non_complete")
	result = prim_module.prim(graph)

	edges = _get_result_edges(result)
	assert len(edges) == len(graph.get_nodes()) - 1
	assert _get_total_weight(result) == 12
	assert not _contains_cycle(graph.get_nodes(), edges)


def test_sparse_graph():
	graph = load_prim_graph("sparse_graph")
	result = prim_module.prim(graph)

	edges = _get_result_edges(result)
	assert len(edges) == len(graph.get_nodes()) - 1
	assert _get_total_weight(result) == 15
	assert not _contains_cycle(graph.get_nodes(), edges)


def test_positive_weights():
	graph = load_prim_graph("positive_weights")
	result = prim_module.prim(graph)

	assert _get_total_weight(result) == 9
	assert len(_get_result_edges(result)) == 3


def test_zero_weight_edges():
	graph = load_prim_graph("zero_weight_edges")
	result = prim_module.prim(graph)

	edges = _get_result_edges(result)
	assert len(edges) == len(graph.get_nodes()) - 1
	assert _get_total_weight(result) == 1
	assert not _contains_cycle(graph.get_nodes(), edges)


def test_negative_weights_are_accepted():
	graph = load_prim_graph("negative_weights")
	result = prim_module.prim(graph)

	edges = _get_result_edges(result)
	assert len(edges) == 2
	assert _get_total_weight(result) == -1
	assert not _contains_cycle(graph.get_nodes(), edges)


def test_parallel_edges_choose_minimum_candidate():
	graph = load_prim_graph("parallel_edges")
	result = prim_module.prim(graph)

	assert _get_total_weight(result) == 3
	assert len(_get_result_edges(result)) == 2


def test_equal_weight_edges():
	graph = load_prim_graph("equal_weight_edges")
	result = prim_module.prim(graph)

	assert _get_total_weight(result) == 3
	assert len(_get_result_edges(result)) == len(graph.get_nodes()) - 1


def test_multiple_tie_cases():
	graph = load_prim_graph("multiple_tie_cases")
	result = prim_module.prim(graph)

	assert _get_total_weight(result) == 8
	assert len(_get_result_edges(result)) == 4


def test_cycle_cases():
	for case_name, expected_weight in [
		("simple_cycle", 6),
		("multiple_cycles", 9),
		("cycle_heaviest_edge", 6),
		("cycle_lightest_edge", 12),
	]:
		graph = load_prim_graph(case_name)
		result = prim_module.prim(graph)
		assert _get_total_weight(result) == expected_weight
		assert len(_get_result_edges(result)) == len(graph.get_nodes()) - 1
		assert not _contains_cycle(graph.get_nodes(), _get_result_edges(result))


# ============================================================================
# ALGORITHM BEHAVIOR AND STRUCTURE
# ============================================================================

def test_result_structure():
	graph = load_prim_graph("two_vertices_with_edge")
	result = prim_module.prim(graph)

	assert isinstance(result, dict)
	assert "mst_edges" in result
	assert "total_weight" in result
	assert "steps" in result
	assert isinstance(result["mst_edges"], list)
	assert isinstance(result["steps"], list)
	assert isinstance(result["total_weight"], (int, float))


def test_steps_are_present():
	graph = load_prim_graph("complete_k4")
	result = prim_module.prim(graph)
	steps = _get_steps(result)

	assert steps
	assert any("Start from node" in step for step in steps)


def test_graph_not_mutated():
	graph = load_prim_graph("mutation_safety")
	before = _snapshot_graph(graph)
	prim_module.prim(graph)
	_assert_graph_unchanged(graph, before)


def test_input_graph_remains_unchanged_after_success():
	graph = load_prim_graph("weighted_complete_graph")
	before = _snapshot_graph(graph)
	prim_module.prim(graph)
	_assert_graph_unchanged(graph, before)


def test_result_is_valid_tree_for_valid_cases():
	for case_name in [
		"single_vertex",
		"two_vertices_with_edge",
		"connected_tree",
		"complete_k4",
		"weighted_complete_graph",
		"simple_cycle",
		"already_mst_valid",
	]:
		graph = load_prim_graph(case_name)
		result = prim_module.prim(graph)
		edges = _get_result_edges(result)
		assert len(edges) == max(len(graph.get_nodes()) - 1, 0)
		assert not _contains_cycle(graph.get_nodes(), edges)
		assert _is_connected(graph.get_nodes(), edges)


def test_start_node_default_is_valid():
	graph = load_prim_graph("positive_weights")
	result = prim_module.prim(graph)
	assert _get_total_weight(result) == 9


def test_invalid_start_node_raises():
	graph = load_prim_graph("positive_weights")
	with pytest.raises(ValueError):
		prim_module.prim(graph, start="Z")


# ============================================================================
# PERFORMANCE / LARGE GRAPHS
# ============================================================================

def test_large_dense_performance_case():
	graph = load_prim_graph("large_dense_performance")
	result = prim_module.prim(graph)

	assert len(_get_result_edges(result)) == len(graph.get_nodes()) - 1
	assert _get_total_weight(result) > 0


def test_large_sparse_performance_case():
	graph = load_prim_graph("large_sparse_performance")
	result = prim_module.prim(graph)

	assert len(_get_result_edges(result)) == len(graph.get_nodes()) - 1
	assert _get_total_weight(result) == 45


# ============================================================================
# GRAPH-WIDE CONSISTENCY CHECKS
# ============================================================================

def test_mst_coherence_across_key_cases():
	for case_name in [
		"complete_k4",
		"dense_non_complete",
		"weighted_complete_graph",
		"global_mst_coherence",
		"mutation_safety",
	]:
		graph = load_prim_graph(case_name)
		result = prim_module.prim(graph)
		edges = _get_result_edges(result)
		assert len(edges) == len(graph.get_nodes()) - 1
		assert not _contains_cycle(graph.get_nodes(), edges)
		assert _is_connected(graph.get_nodes(), edges)


def test_self_loop_is_rejected():
	graph = load_prim_graph("self_loop")
	with pytest.raises(ValueError):
		prim_module.prim(graph)


def test_dominant_component_raises_on_isolated_vertex():
	graph = load_prim_graph("dominant_component")
	with pytest.raises(ValueError):
		prim_module.prim(graph)


def test_directed_graph_raises():
	graph = Graph(directed=True)
	graph.add_edge("A", "B", 1)
	graph.add_edge("B", "C", 2)

	with pytest.raises(ValueError):
		prim_module.prim(graph)
