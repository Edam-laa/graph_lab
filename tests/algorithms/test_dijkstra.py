import math
import pytest

from app.algorithms.shortest_path.dijkstra import dijkstra
from app.utils.file_loader import load_graph


def test_dijkstra_simple():
    graph = load_graph("data/simple_graph.json")
    result = dijkstra(graph, source="A", target="C")

    assert result["distance"] == 3
    assert result["path"] == ["A", "B", "C"]


def test_dijkstra_multiple_paths_choose_shortest():
    graph = load_graph("data/multiple_paths_graph.json")
    result = dijkstra(graph, source="A", target="D")

    assert result["distance"] == 3
    assert result["path"] == ["A", "C", "D"]


def test_dijkstra_directed_graph_respects_edge_direction():
    graph = load_graph("data/directed_graph.json")
    result = dijkstra(graph, source="B", target="A")

    assert math.isinf(result["distance"])
    assert result["path"] == []


def test_dijkstra_undirected_graph():
    graph = load_graph("data/undirected_graph.json")
    result = dijkstra(graph, source="A", target="C")

    assert result["distance"] == 3
    assert result["path"] == ["A", "B", "C"]


def test_dijkstra_sum_of_weights_is_correct():
    graph = load_graph("data/sum_weights_graph.json")
    result = dijkstra(graph, source="A", target="C")

    assert result["distance"] == 7
    assert result["path"] == ["A", "B", "C"]


def test_dijkstra_source_equals_destination():
    graph = load_graph("data/simple_graph.json")
    result = dijkstra(graph, source="A", target="A")

    assert result["distance"] == 0
    assert result["path"] == ["A"]


def test_dijkstra_single_vertex_graph():
    graph = load_graph("data/single_vertex_graph.json")
    result = dijkstra(graph, source="A", target="A")

    assert result["distance"] == 0
    assert result["path"] == ["A"]


def test_dijkstra_disconnected_graph_no_path():
    graph = load_graph("data/disconnected_graph.json")
    result = dijkstra(graph, source="A", target="D")

    assert math.isinf(result["distance"])
    assert result["path"] == []


def test_dijkstra_valid_graph_without_path_between_two_nodes():
    graph = load_graph("data/valid_graph_no_path.json")
    result = dijkstra(graph, source="A", target="D")

    assert math.isinf(result["distance"])
    assert result["path"] == []


def test_dijkstra_cycles_do_not_cause_infinite_loop():
    graph = load_graph("data/cycle_graph.json")
    result = dijkstra(graph, source="A", target="D")

    assert result["distance"] == 3
    assert result["path"] == ["A", "B", "C", "D"]


def test_dijkstra_negative_weights_raise_error():
    graph = load_graph("data/negative_weights.json")

    with pytest.raises(ValueError):
        dijkstra(graph, source="A", target="C")


def test_dijkstra_source_vertex_missing():
    graph = load_graph("data/simple_graph.json")

    with pytest.raises(KeyError):
        dijkstra(graph, source="Z", target="C")


def test_dijkstra_target_vertex_missing():
    graph = load_graph("data/simple_graph.json")

    with pytest.raises(KeyError):
        dijkstra(graph, source="A", target="Z")


def test_dijkstra_empty_graph():
    graph = load_graph("data/empty_graph.json")

    with pytest.raises(ValueError):
        dijkstra(graph, source="A", target="A")


def test_dijkstra_zero_weight_edges():
    graph = load_graph("data/zero_weights_graph.json")
    result = dijkstra(graph, source="A", target="C")

    assert result["distance"] == 0
    assert result["path"] == ["A", "B", "C"]


def test_dijkstra_output_structure_is_coherent():
    graph = load_graph("data/simple_graph.json")
    result = dijkstra(graph, source="A", target="C")

    assert "distance" in result
    assert "path" in result
    assert isinstance(result["path"], list)
    assert result["path"][0] == "A"
    assert result["path"][-1] == "C"
    assert result["distance"] == 3