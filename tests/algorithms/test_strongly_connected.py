"""Strong connectivity test suite for strongly_connected.py."""

import json
from copy import deepcopy
from pathlib import Path
import sys

import pytest

from app.algorithms.connectivity import connected_components as connectivity_module
from app.core.graph import Graph
from app.utils.file_loader import load_graph_from_json

sys.modules.setdefault("connectivity", connectivity_module)

from app.algorithms.connectivity import strongly_connected as strongly_connected_module


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
STRONGLY_CONNECTED_CASES_FILE = DATA_DIR / "strongly_connected_test_graphs.json"


def load_strongly_connected_graph(case_name):
	with open(STRONGLY_CONNECTED_CASES_FILE, "r", encoding="utf-8") as file:
		collection = json.load(file)

	graph_data = collection["graphs"][case_name]
	return graph_data, load_graph_from_json({"graph": graph_data})


def build_graph(nodes, edges, directed=True):
	graph = Graph(directed=directed)
	for node in nodes:
		graph.add_node(node)
	for source, target, weight in edges:
		graph.add_edge(source, target, weight)
	return graph


def assert_fixture_case(case_name, expected):
	graph_data, graph = load_strongly_connected_graph(case_name)
	original_snapshot = {
		"nodes": deepcopy(graph.nodes),
		"adj_list": deepcopy(graph.adj_list),
	}

	assert strongly_connected_module.is_strongly_connected(graph) is expected
	assert graph.nodes == original_snapshot["nodes"]
	assert graph.adj_list == original_snapshot["adj_list"]


@pytest.mark.parametrize(
	"case_name, expected",
	[
		("empty_graph", True),
		("single_vertex_graph", True),
		("single_directed_self_loop", True),
		("two_nodes_one_way_edge", False),
		("two_nodes_bidirectional_edges", True),
		("simple_directed_cycle", True),
		("directed_chain", False),
		("strongly_connected_directed_graph", True),
		("directed_graph_with_sink_node", False),
		("directed_graph_with_source_node_only", False),
		("graph_with_multiple_scc_components", False),
		("disconnected_directed_graph", False),
		("undirected_connected_graph", True),
		("undirected_disconnected_graph", False),
		("graph_with_isolated_node", False),
		("graph_with_self_loop_only_nodes_except_one_isolated", False),
		("graph_forward_reachable_but_not_reverse_reachable", False),
		("graph_reverse_reachable_but_not_forward_reachable", False),
		("complete_directed_graph", True),
		("nearly_complete_graph_missing_one_edge", True),
		("graph_with_parallel_edges", True),
		("graph_with_weighted_edges", True),
		("large_strongly_connected_sparse_graph", False),
		("large_non_strongly_connected_sparse_graph", False),
		("graph_unreachable_node_forward_dfs_only", False),
		("graph_unreachable_node_reversed_dfs_only", False),
		("graph_with_cycles_and_dead_end_branch", False),
		("graph_with_multiple_incoming_no_outgoing", False),
		("graph_with_multiple_outgoing_no_incoming", False),
		("non_sequential_node_ids", True),
		("start_node_choice_changes_result", False),
	],
)
def test_is_strongly_connected_from_fixture_collection(case_name, expected):
	assert_fixture_case(case_name, expected)


def test_malformed_adjacency_missing_node_entries_is_handled():
	graph = Graph(directed=True)
	graph.nodes = {"A", "B", "C"}
	graph.adj_list = {
		"A": [("B", 1, None)],
		"B": [("A", 1, None)],
		# Node C is intentionally missing from adj_list
	}

	assert strongly_connected_module.is_strongly_connected(graph) is False


def test_graph_with_bidirectional_directed_edges_is_strongly_connected():
	graph = build_graph(
		["A", "B", "C"],
		[("A", "B", 1), ("B", "A", 1), ("B", "C", 1), ("C", "B", 1)],
		directed=True,
	)

	assert strongly_connected_module.is_strongly_connected(graph) is True


def test_start_node_choice_does_not_change_result():
	graph_one = build_graph(
		["Z", "A", "M", "Q"],
		[("Z", "A", 1), ("A", "M", 1), ("M", "Q", 1), ("Q", "Z", 1)],
		directed=True,
	)
	graph_two = build_graph(
		["Q", "M", "A", "Z"],
		[("Z", "A", 1), ("A", "M", 1), ("M", "Q", 1), ("Q", "Z", 1)],
		directed=True,
	)

	assert strongly_connected_module.is_strongly_connected(graph_one) is True
	assert strongly_connected_module.is_strongly_connected(graph_two) is True
