"""Connectivity test suite for connected_components.py."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from app.algorithms.connectivity.connected_components import is_connected
from app.core.graph import Graph
from app.utils.file_loader import load_graph_from_json


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CONNECTED_CASES_FILE = DATA_DIR / "connected_components_test_graphs.json"


def load_connectivity_graph(case_name):
	with open(CONNECTED_CASES_FILE, "r", encoding="utf-8") as file:
		collection = json.load(file)

	graph_data = collection["graphs"][case_name]
	return graph_data, load_graph_from_json({"graph": graph_data})


def build_graph(nodes, edges, directed=False):
	graph = Graph(directed=directed)
	for node in nodes:
		graph.add_node(node)
	for source, target, weight in edges:
		graph.add_edge(source, target, weight)
	return graph


@pytest.mark.parametrize(
	"case_name, expected",
	[
		("empty_graph", True),
		("single_vertex_graph", True),
		("two_connected_vertices", True),
		("two_disconnected_vertices", False),
		("simple_connected_undirected_graph", True),
		("disconnected_undirected_graph", False),
		("cyclic_undirected_graph", True),
		("tree_graph", True),
		("graph_with_isolated_vertex", False),
		("graph_with_multiple_connected_components", False),
		("directed_strongly_connected_graph", True),
		("directed_weakly_connected_graph", True),
		("directed_disconnected_graph", False),
		("one_way_directed_chain", True),
		("graph_with_self_loop", False),
		("graph_with_parallel_edges", True),
		("weighted_graph_connectivity", True),
		("adjacency_symmetry_handling", True),
		("missing_adjacency_entry", False),
		("large_sparse_graph", False),
		("large_dense_graph", True),
		("disconnected_node_not_in_adjacency_list", False),
		("graph_with_bidirectional_directed_edges", True),
		("stack_traversal_completeness", True),
		("starting_node_independence", True),
		("graph_with_redundant_edges", True),
		("mixed_isolated_and_connected_subgraphs", False),
		("non_sequential_node_identifiers", True),
		("mutation_safety", True),
	],
)
def test_is_connected_from_fixture_collection(case_name, expected):
	graph_data, graph = load_connectivity_graph(case_name)
	original_snapshot = {
		"nodes": deepcopy(graph.nodes),
		"adj_list": deepcopy(graph.adj_list),
	}

	result = is_connected(graph)
	assert result["connected"] is expected
	assert graph.nodes == original_snapshot["nodes"]
	assert graph.adj_list == original_snapshot["adj_list"]


def test_malformed_adjacency_references_raise_value_error():
	graph = Graph(directed=False)
	graph.nodes = ["A", "B"]
	graph.adj_list = {
		"A": [("X", 1, None)],
		"B": [],
	}

	with pytest.raises(ValueError):
		is_connected(graph)


def test_directed_bidirectional_edges_remain_connected():
	graph = build_graph(
		["A", "B", "C"],
		[("A", "B", 1), ("B", "A", 1), ("B", "C", 1), ("C", "B", 1)],
		directed=True,
	)

	result = is_connected(graph)
	assert result["connected"] is True