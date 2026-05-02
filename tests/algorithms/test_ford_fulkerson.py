import json

import pytest

from app.algorithms.flow.ford_fulkerson import ford_fulkerson
from app.utils.file_loader import load_graph_from_json


CASES_FILE = "data/ford_fulkerson_test_graphs.json"


def load_ford_graph(case_name):
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        collection = json.load(f)

    graph_data = collection["graphs"][case_name]
    wrapped = {"graph": graph_data}
    return load_graph_from_json(wrapped), graph_data.get("metadata", {})


@pytest.mark.parametrize(
    "case,expected",
    [
        ("single_edge_graph", 7),
        ("disconnected_graph", 0),
        ("zero_capacity_edge", 0),
        ("simple_linear_graph", 3),
        ("multiple_parallel_paths", 5),
        ("bottleneck_edge_graph", 7),
        ("parallel_multi_edges", 7),
        ("unreachable_sink", 0),
        ("fully_saturated_network", 2),
        ("disconnected_source_component", 0),
    ],
)
def test_ford_fulkerson_expected_max_flow(case, expected):
    graph, meta = load_ford_graph(case)
    source = meta.get("source")
    sink = meta.get("sink")

    result = ford_fulkerson(graph, source, sink)

    assert "max_flow" in result
    assert result["max_flow"] == expected


def test_ford_fulkerson_output_structure_is_coherent():
    graph, meta = load_ford_graph("single_edge_graph")
    source = meta.get("source")
    sink = meta.get("sink")

    result = ford_fulkerson(graph, source, sink)

    assert isinstance(result, dict)
    assert "max_flow" in result
    assert "augmenting_paths" in result
    assert "steps" in result


def test_invalid_graph_structure_raises():
    # invalid_graph_structure in fixture uses malformed nodes/edges
    with pytest.raises(Exception):
        load_ford_graph("invalid_graph_structure")


def test_missing_source_or_sink_returns_zero():
    g_invalid_source, meta = load_ford_graph("invalid_source_node")
    # metadata requests a missing source
    source = meta.get("source")
    sink = meta.get("sink")

    res = ford_fulkerson(g_invalid_source, source, sink)
    assert res["max_flow"] == 0

    g_invalid_sink, meta2 = load_ford_graph("invalid_sink_node")
    source2 = meta2.get("source")
    sink2 = meta2.get("sink")

    res2 = ford_fulkerson(g_invalid_sink, source2, sink2)
    assert res2["max_flow"] == 0
