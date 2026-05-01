"""
Kruskal Algorithm Test Suite

NOTES FOR DEVELOPMENT TEAM:
============================
1. TEST FIXTURES CONSOLIDATION
   - All test cases consolidated in data/kruskal_test_graphs.json
   - Individual kruskal_*.json files have been removed
   - Format: {"graphs": {"case_name": {...graph_data...}, ...}}

2. ADAPTER PATTERN
   - load_kruskal_graph(case_name) adapter function:
     * Loads collection JSON
     * Extracts named test case
     * Wraps as {"graph": ...} for app/utils/file_loader.py
     * Returns Graph object via load_graph_from_json()
   - Original loader remains UNMODIFIED and immutable

3. ADDING NEW TEST CASES
   - Add entries to data/kruskal_test_graphs.json under "graphs" key
   - Use: graph = load_kruskal_graph("case_name")
"""

import json
from pathlib import Path

from app.algorithms.spanning_tree import kruskal as kruskal_module
from app.utils.file_loader import load_graph_from_json


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
KRUSKAL_CASES_FILE = DATA_DIR / "kruskal_test_graphs.json"


def load_kruskal_graph(case_name):
	"""Load a Kruskal test case from the consolidated collection.
	
	Args:
		case_name (str): Name of the test case in kruskal_test_graphs.json
		
	Returns:
		Graph: Loaded and validated graph object
	"""
	with open(KRUSKAL_CASES_FILE, "r", encoding="utf-8") as f:
		collection = json.load(f)
	
	graph_data = collection["graphs"][case_name]
	wrapped = {"graph": graph_data}
	return load_graph_from_json(wrapped)


def _extract_edges(result):
	assert isinstance(result, dict)
	assert "edges" in result
	assert isinstance(result["edges"], list)
	return result["edges"]


def _extract_total_weight(result):
	assert isinstance(result, dict)
	assert "total_weight" in result
	return result["total_weight"]


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


def test_kruskal_simple_graph():
	graph = load_kruskal_graph("simple")
	result = kruskal_module.kruskal(graph)

	assert _extract_total_weight(result) == 3
	assert len(_extract_edges(result)) == 2


def test_kruskal_multiple_choices_global_min_cost():
	graph = load_kruskal_graph("choice")
	result = kruskal_module.kruskal(graph)

	assert _extract_total_weight(result) == 4
	assert len(_extract_edges(result)) == 3


def test_kruskal_undirected_standard_case():
	graph = load_kruskal_graph("simple")
	result = kruskal_module.kruskal(graph)

	assert _extract_total_weight(result) == 3
	assert len(_extract_edges(result)) == 2


def test_kruskal_result_is_tree_without_cycles_and_n_minus_one_edges():
	graph = load_kruskal_graph("choice")
	result = kruskal_module.kruskal(graph)

	edges = _extract_edges(result)
	assert len(edges) == len(graph["nodes"]) - 1
	assert not _contains_cycle(graph["nodes"], edges)


def test_kruskal_total_weight_is_minimal():
	graph = load_kruskal_graph("min_cost")
	result = kruskal_module.kruskal(graph)

	assert _extract_total_weight(result) == 6


def test_kruskal_negative_weights_are_supported():
	graph = load_kruskal_graph("negative_weights")
	result = kruskal_module.kruskal(graph)

	assert _extract_total_weight(result) == 1
	assert len(_extract_edges(result)) == 3


def test_kruskal_cycles_are_avoided():
	graph = load_kruskal_graph("cycle")
	result = kruskal_module.kruskal(graph)

	edges = _extract_edges(result)
	assert len(edges) == len(graph["nodes"]) - 1
	assert not _contains_cycle(graph["nodes"], edges)


def test_kruskal_unsorted_edges_input_still_works():
	graph = load_kruskal_graph("unsorted_edges")
	result = kruskal_module.kruskal(graph)

	assert _extract_total_weight(result) == 6


def test_kruskal_disconnected_graph_returns_forest():
	graph = load_kruskal_graph("disconnected")
	result = kruskal_module.kruskal(graph)

	edges = _extract_edges(result)
	assert len(edges) < len(graph["nodes"]) - 1
	assert _extract_total_weight(result) == 3
	assert not _contains_cycle(graph["nodes"], edges)


def test_kruskal_single_vertex_graph():
	graph = load_kruskal_graph("single_vertex")
	result = kruskal_module.kruskal(graph)

	assert _extract_total_weight(result) == 0
	assert _extract_edges(result) == []


def test_kruskal_graph_without_edges():
	graph = load_kruskal_graph("no_edges")
	result = kruskal_module.kruskal(graph)

	assert _extract_total_weight(result) == 0
	assert _extract_edges(result) == []


def test_kruskal_duplicate_edges():
	graph = load_kruskal_graph("duplicate_edges")
	result = kruskal_module.kruskal(graph)

	assert _extract_total_weight(result) == 3
	assert len(_extract_edges(result)) == 2


def test_kruskal_self_loops_are_ignored():
	graph = load_kruskal_graph("self_loop")
	result = kruskal_module.kruskal(graph)

	assert _extract_total_weight(result) == 4
	assert len(_extract_edges(result)) == 2


def test_kruskal_equal_weights():
	graph = load_kruskal_graph("equal_weights")
	result = kruskal_module.kruskal(graph)

	assert _extract_total_weight(result) == 3
	assert len(_extract_edges(result)) == 3


def test_kruskal_output_structure_is_coherent():
	graph = load_kruskal_graph("simple")
	result = kruskal_module.kruskal(graph)

	assert isinstance(result, dict)
	assert "total_weight" in result
	assert "edges" in result
	assert isinstance(result["edges"], list)
	assert isinstance(result["total_weight"], (int, float))
