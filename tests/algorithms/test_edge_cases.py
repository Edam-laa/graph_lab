import pytest

from app.utils.file_loader import load_graph_from_json


def _wrap_graph(graph_data):
	return {"graph": graph_data}


def test_loader_rejects_nodes_not_list():
	graph_data = {
		"nodes": "not_a_list",
		"edges": [],
		"directed": True,
	}

	with pytest.raises(ValueError):
		load_graph_from_json(_wrap_graph(graph_data))


def test_loader_rejects_edges_not_list():
	graph_data = {
		"nodes": ["A", "B"],
		"edges": "not_a_list",
		"directed": True,
	}

	with pytest.raises(ValueError):
		load_graph_from_json(_wrap_graph(graph_data))


def test_loader_rejects_edge_missing_from():
	graph_data = {
		"nodes": ["A", "B"],
		"edges": [{"to": "B", "weight": 1}],
		"directed": True,
	}

	with pytest.raises(ValueError):
		load_graph_from_json(_wrap_graph(graph_data))


def test_loader_rejects_edge_missing_to():
	graph_data = {
		"nodes": ["A", "B"],
		"edges": [{"from": "A", "weight": 1}],
		"directed": True,
	}

	with pytest.raises(ValueError):
		load_graph_from_json(_wrap_graph(graph_data))


def test_loader_rejects_non_numeric_weight():
	graph_data = {
		"nodes": ["A", "B"],
		"edges": [{"from": "A", "to": "B", "weight": "bad"}],
		"directed": True,
	}

	with pytest.raises(ValueError):
		load_graph_from_json(_wrap_graph(graph_data))


def test_loader_rejects_non_numeric_capacity():
	graph_data = {
		"nodes": ["A", "B"],
		"edges": [{"from": "A", "to": "B", "weight": 1, "capacity": "bad"}],
		"directed": True,
	}

	with pytest.raises(ValueError):
		load_graph_from_json(_wrap_graph(graph_data))


def test_loader_rejects_edge_reference_to_missing_node():
	graph_data = {
		"nodes": ["A"],
		"edges": [{"from": "A", "to": "B", "weight": 1}],
		"directed": True,
	}

	with pytest.raises(ValueError):
		load_graph_from_json(_wrap_graph(graph_data))
