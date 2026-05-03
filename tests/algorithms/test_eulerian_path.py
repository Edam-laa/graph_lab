"""Eulerian path/circuit test suite."""

import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest

from app.algorithms.eulerian import eulerian_path as eulerian_module
from app.core.graph import Graph
from app.utils.file_loader import load_graph_from_json


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
EULERIAN_CASES_FILE = DATA_DIR / "eulerian_path_test_graphs.json"


def load_eulerian_graph(case_name):
	with open(EULERIAN_CASES_FILE, "r", encoding="utf-8") as file:
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


def build_directed_graph(nodes, edges):
	return build_graph(nodes, edges, directed=True)


def build_undirected_graph(nodes, edges):
	return build_graph(nodes, edges, directed=False)


def normalize_edge_pair(source, target, directed):
	if directed:
		return source, target
	return tuple(sorted((source, target)))


def assert_tour_uses_each_edge_once(graph_data, tour):
	assert tour is not None

	directed = graph_data["directed"]
	expected = Counter(
		normalize_edge_pair(edge["from"], edge["to"], directed)
		for edge in graph_data["edges"]
	)
	actual = Counter(
		normalize_edge_pair(source, target, directed)
		for source, target in zip(tour, tour[1:])
	)

	assert actual == expected
	assert len(tour) == len(graph_data["edges"]) + 1


def test_empty_graph_raises_value_error():
	_, graph = load_eulerian_graph("empty_graph")

	with pytest.raises(ValueError):
		eulerian_module.find_eulerian_tour(graph)


def test_single_vertex_graph_raises_value_error():
	_, graph = load_eulerian_graph("single_vertex_graph")

	with pytest.raises(ValueError):
		eulerian_module.find_eulerian_tour(graph)


@pytest.mark.parametrize(
	"case_name, expected_status, expected_start, expected_end",
	[
		("single_edge_undirected_graph", 1, "A", "B"),
		("simple_undirected_eulerian_path", 1, "A", "C"),
		("simple_undirected_eulerian_circuit", 2, "A", "A"),
		("cycle_graph", 2, "A", "A"),
		("graph_with_bridge_edges", 2, "A", "A"),
		("graph_with_multiple_cycles", 2, "A", "A"),
		("graph_with_self_loop", 2, "A", "A"),
		("graph_with_parallel_edges", 1, "A", "B"),
		("weighted_graph_compatibility", 2, "A", "A"),
	],
)
def test_undirected_eulerian_graphs(case_name, expected_status, expected_start, expected_end):
	graph_data, graph = load_eulerian_graph(case_name)
	original_adj_list = deepcopy(graph.adj_list)

	assert eulerian_module.check_eulerian_status(graph) == expected_status
	tour = eulerian_module.find_eulerian_tour(graph)

	assert graph.adj_list == original_adj_list
	assert_tour_uses_each_edge_once(graph_data, tour)
	assert tour[0] == expected_start
	assert tour[-1] == expected_end
	if expected_status == 2:
		assert tour[0] == tour[-1]


@pytest.mark.parametrize(
	"case_name",
	[
		"undirected_non_eulerian_graph",
		"disconnected_undirected_graph",
		"zero_edge_graph",
	],
)
def test_undirected_non_eulerian_or_disconnected_graphs(case_name):
	_, graph = load_eulerian_graph(case_name)

	with pytest.raises(ValueError):
		eulerian_module.find_eulerian_tour(graph)


def test_returned_path_endpoints_validation():
	graph_data, graph = load_eulerian_graph("simple_undirected_eulerian_path")
	tour = eulerian_module.find_eulerian_tour(graph)

	assert tour[0] == "A"
	assert tour[-1] == "C"
	assert_tour_uses_each_edge_once(graph_data, tour)


def test_returned_circuit_start_end_equality():
	graph_data, graph = load_eulerian_graph("simple_undirected_eulerian_circuit")
	tour = eulerian_module.find_eulerian_tour(graph)

	assert tour[0] == tour[-1]
	assert_tour_uses_each_edge_once(graph_data, tour)


def test_all_edges_used_exactly_once():
	graph = build_undirected_graph(
		["A", "B", "C"],
		[
			("A", "B", 1),
			("A", "B", 1),
			("B", "C", 1),
			("B", "C", 1),
			("C", "A", 1),
			("C", "A", 1),
		],
	)
	graph_data = {
		"directed": False,
		"edges": [
			{"from": "A", "to": "B"},
			{"from": "A", "to": "B"},
			{"from": "B", "to": "C"},
			{"from": "B", "to": "C"},
			{"from": "C", "to": "A"},
			{"from": "C", "to": "A"},
		],
	}

	tour = eulerian_module.find_eulerian_tour(graph)
	assert eulerian_module.check_eulerian_status(graph) == 2
	assert_tour_uses_each_edge_once(graph_data, tour)


def test_returned_path_length_validation():
	graph = build_undirected_graph(
		["A", "B", "C"],
		[
			("A", "B", 1),
			("A", "B", 1),
			("B", "C", 1),
			("B", "C", 1),
			("C", "A", 1),
			("C", "A", 1),
		],
	)
	tour = eulerian_module.find_eulerian_tour(graph)

	assert len(tour) == 7


def test_directed_eulerian_circuit():
	graph_data, graph = load_eulerian_graph("directed_eulerian_circuit")
	tour = eulerian_module.find_eulerian_tour(graph)

	assert eulerian_module.check_eulerian_status(graph) == 2
	assert tour[0] == tour[-1]
	assert_tour_uses_each_edge_once(graph_data, tour)


def test_directed_eulerian_path():
	graph_data, graph = load_eulerian_graph("directed_eulerian_path")
	tour = eulerian_module.find_eulerian_tour(graph)

	assert eulerian_module.check_eulerian_status(graph) == 1
	assert tour[0] == "A"
	assert tour[-1] == "D"
	assert_tour_uses_each_edge_once(graph_data, tour)


def test_directed_non_eulerian_graph():
	graph = build_directed_graph(
		["A", "B"],
		[("A", "B", 1), ("A", "B", 1), ("A", "B", 1), ("B", "A", 1)],
	)

	assert eulerian_module.check_eulerian_status(graph) == 0
	assert eulerian_module.find_eulerian_tour(graph) is None


def test_disconnected_directed_graph():
	graph_data, graph = load_eulerian_graph("disconnected_directed_graph")

	assert eulerian_module.check_eulerian_status(graph) == 0
	assert eulerian_module.find_eulerian_tour(graph) is None


def test_directed_cycle_graph():
	graph_data, graph = load_eulerian_graph("directed_cycle_graph")
	tour = eulerian_module.find_eulerian_tour(graph)

	assert eulerian_module.check_eulerian_status(graph) == 2
	assert tour[0] == tour[-1]
	assert_tour_uses_each_edge_once(graph_data, tour)


def test_directed_eulerian_path_with_terminal_node():
	graph_data = {
		"directed": True,
		"edges": [
			{"from": "A", "to": "B"},
			{"from": "B", "to": "C"},
			{"from": "C", "to": "A"},
			{"from": "C", "to": "D"},
		],
	}
	graph = build_directed_graph(
		["A", "B", "C", "D"],
		[("A", "B", 1), ("B", "C", 1), ("C", "A", 1), ("C", "D", 1)],
	)

	tour = eulerian_module.find_eulerian_tour(graph)

	assert eulerian_module.check_eulerian_status(graph) == 1
	assert tour[0] == "C"
	assert tour[-1] == "D"
	assert_tour_uses_each_edge_once(graph_data, tour)


def test_directed_eulerian_path_with_cycle_then_terminal_node():
	graph_data = {
		"directed": True,
		"edges": [
			{"from": "A", "to": "B"},
			{"from": "B", "to": "A"},
			{"from": "B", "to": "C"},
		],
	}
	graph = build_directed_graph(
		["A", "B", "C"],
		[("A", "B", 1), ("B", "A", 1), ("B", "C", 1)],
	)

	tour = eulerian_module.find_eulerian_tour(graph)

	assert eulerian_module.check_eulerian_status(graph) == 1
	assert tour[0] == "B"
	assert tour[-1] == "C"
	assert_tour_uses_each_edge_once(graph_data, tour)


def test_large_sparse_graph():
	nodes = [f"N{i}" for i in range(50)]
	edges = [(f"N{i}", f"N{(i + 1) % 50}", 1) for i in range(50)]
	graph = build_undirected_graph(nodes, edges)
	tour = eulerian_module.find_eulerian_tour(graph)

	assert eulerian_module.check_eulerian_status(graph) == 2
	assert len(tour) == 51


def test_large_dense_graph():
	nodes = ["A", "B", "C", "D", "E"]
	edges = [
		("A", "B", 1),
		("A", "C", 1),
		("A", "D", 1),
		("A", "E", 1),
		("B", "C", 1),
		("B", "D", 1),
		("B", "E", 1),
		("C", "D", 1),
		("C", "E", 1),
		("D", "E", 1),
	]
	graph = build_undirected_graph(nodes, edges)
	tour = eulerian_module.find_eulerian_tour(graph)

	assert eulerian_module.check_eulerian_status(graph) == 2
	assert len(tour) == 11


def test_deterministic_traversal_behavior():
	_, first_graph = load_eulerian_graph("cycle_graph")
	_, second_graph = load_eulerian_graph("cycle_graph")

	assert eulerian_module.find_eulerian_tour(first_graph) == eulerian_module.find_eulerian_tour(second_graph)


def test_adjacency_list_mutation_safety():
	_, graph = load_eulerian_graph("graph_with_bridge_edges")
	original_adj_list = deepcopy(graph.adj_list)

	eulerian_module.find_eulerian_tour(graph)

	assert graph.adj_list == original_adj_list


def test_invalid_node_references_raise_error_on_malformed_adjacency():
	graph = Graph(directed=False)
	graph.nodes = {"A", "B"}
	graph.adj_list = {
		"A": [("B", 1)],
		"B": [("A", 1)],
	}

	with pytest.raises(ValueError):
		eulerian_module.find_eulerian_tour(graph)


def test_isolated_vertices_with_eulerian_component():
	graph = build_undirected_graph(
		["A", "B", "C", "D", "E"],
		[("A", "B", 1), ("B", "C", 1), ("C", "A", 1)],
	)
	graph.add_node("D")
	graph.add_node("E")

	assert eulerian_module.check_eulerian_status(graph) == 0
	assert eulerian_module.find_eulerian_tour(graph) is None
