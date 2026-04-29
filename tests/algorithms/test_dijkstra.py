import math
import pytest

from app.algorithms.shortest_path.dijkstra import dijkstra, reconstruct_path
from app.utils.file_loader import load_graph_from_json


def test_dijkstra_simple():
    graph = load_graph_from_json("data/simple_graph.json")
    result = dijkstra(graph, start="A")

    assert result["distances"]["C"] == 3
    assert reconstruct_path(result["previous"], "A", "C") == ["A", "B", "C"]


def test_dijkstra_multiple_paths_choose_shortest():
    graph = load_graph_from_json("data/multiple_paths_graph.json")
    result = dijkstra(graph, start="A")

    assert result["distances"]["D"] == 3
    assert reconstruct_path(result["previous"], "A", "D") == ["A", "C", "D"]


def test_dijkstra_directed_graph_respects_edge_direction():
    graph = load_graph_from_json("data/directed_graph.json")
    result = dijkstra(graph, start="B")

    assert math.isinf(result["distances"]["A"])
    assert reconstruct_path(result["previous"], "B", "A") == []


def test_dijkstra_undirected_graph():
    graph = load_graph_from_json("data/undirected_graph.json")
    result = dijkstra(graph, start="A")

    assert result["distances"]["C"] == 3
    assert reconstruct_path(result["previous"], "A", "C") == ["A", "B", "C"]


def test_dijkstra_sum_of_weights_is_correct():
    graph = load_graph_from_json("data/sum_weights_graph.json")
    result = dijkstra(graph, start="A")

    assert result["distances"]["C"] == 7
    assert reconstruct_path(result["previous"], "A", "C") == ["A", "B", "C"]


def test_dijkstra_source_equals_destination():
    graph = load_graph_from_json("data/simple_graph.json")
    result = dijkstra(graph, start="A")

    assert result["distances"]["A"] == 0
    assert reconstruct_path(result["previous"], "A", "A") == ["A"]


def test_dijkstra_single_vertex_graph():
    graph = load_graph_from_json("data/single_vertex_graph.json")
    result = dijkstra(graph, start="A")

    assert result["distances"]["A"] == 0
    assert reconstruct_path(result["previous"], "A", "A") == ["A"]


def test_dijkstra_disconnected_graph_no_path():
    graph = load_graph_from_json("data/disconnected_graph.json")
    result = dijkstra(graph, start="A")

    assert math.isinf(result["distances"]["D"])
    assert reconstruct_path(result["previous"], "A", "D") == []


def test_dijkstra_valid_graph_without_path_between_two_nodes():
    graph = load_graph_from_json("data/valid_graph_no_path.json")
    result = dijkstra(graph, start="A")

    assert math.isinf(result["distances"]["D"])
    assert reconstruct_path(result["previous"], "A", "D") == []


def test_dijkstra_cycles_do_not_cause_infinite_loop():
    graph = load_graph_from_json("data/cycle_graph.json")
    result = dijkstra(graph, start="A")

    assert result["distances"]["D"] == 3
    assert reconstruct_path(result["previous"], "A", "D") == ["A", "B", "C", "D"]


def test_dijkstra_negative_weights_raise_error():
    graph = load_graph_from_json("data/negative_weights.json")

    with pytest.raises(ValueError):
        dijkstra(graph, start="A")


def test_dijkstra_source_vertex_missing():
    graph = load_graph_from_json("data/simple_graph.json")

    with pytest.raises(ValueError):
        dijkstra(graph, start="Z")


def test_dijkstra_empty_graph():
    graph = load_graph_from_json("data/empty_graph.json")

    with pytest.raises(ValueError):
        dijkstra(graph, start="A")


def test_dijkstra_zero_weight_edges():
    graph = load_graph_from_json("data/zero_weights_graph.json")
    result = dijkstra(graph, start="A")

    assert result["distances"]["C"] == 0
    assert reconstruct_path(result["previous"], "A", "C") == ["A", "B", "C"]


def test_dijkstra_output_structure_is_coherent():
    graph = load_graph_from_json("data/simple_graph.json")
    result = dijkstra(graph, start="A")

    assert "distances" in result
    assert "previous" in result
    assert "steps" in result
    assert isinstance(result["distances"], dict)
    assert isinstance(result["previous"], dict)
    assert isinstance(result["steps"], list)
    assert result["distances"]["C"] == 3