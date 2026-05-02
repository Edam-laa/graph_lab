import copy
import json
import math
from pathlib import Path

import pytest

from app.algorithms.shortest_path.bellman import bellman
from app.utils.file_loader import load_graph_from_json


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
BELLMAN_CASES_FILE = DATA_DIR / "bellman_test_graphs.json"


def load_bellman_case(case_name):
    with open(BELLMAN_CASES_FILE, "r", encoding="utf-8") as fixture_file:
        collection = json.load(fixture_file)

    return collection["graphs"][case_name]


def load_bellman_graph(case_name):
    graph_data = load_bellman_case(case_name)
    wrapped = {"graph": graph_data}
    return load_graph_from_json(wrapped)


def run_case(case_name):
    case = load_bellman_case(case_name)
    graph = load_bellman_graph(case_name)
    source = case.get("metadata", {}).get("source")
    if source is None and case.get("nodes"):
        source = case["nodes"][0]
    result = bellman(graph, source)
    return case, graph, result


def reconstruct_path(previous, source, target):
    if source == target:
        return [source]

    if target not in previous:
        return []

    path = []
    current = target
    visited = set()

    while current is not None and current not in visited:
        visited.add(current)
        path.append(current)
        current = previous.get(current)

    if not path or path[-1] != source:
        return []

    return list(reversed(path))


def get_case_names():
    with open(BELLMAN_CASES_FILE, "r", encoding="utf-8") as fixture_file:
        collection = json.load(fixture_file)
    return list(collection["graphs"].keys())


def test_fixture_covers_requested_scenarios():
    expected_cases = {
        "empty_graph",
        "single_vertex",
        "source_equals_destination",
        "single_edge",
        "simple_dag",
        "dag_multiple_paths",
        "unreachable_vertex",
        "partially_reachable",
        "isolated_vertices",
        "positive_weights",
        "zero_weights",
        "negative_weights_no_cycle",
        "mixed_positive_negative",
        "long_chain",
        "cheaper_indirect_path",
        "multiple_predecessors",
        "equal_cost_paths",
        "parallel_edges",
        "path_reconstruction",
        "predecessor_validation",
        "distance_initialization",
        "valid_topological_order",
        "dense_acyclic_graph",
        "sparse_graph",
        "all_vertices_reachable",
        "final_distance_validation",
        "edge_direction_respect",
        "source_not_found",
        "destination_not_found",
        "invalid_adjacency_structure",
        "graph_immutability",
        "deterministic_results",
        "simple_cycle_rejected",
        "directed_cycle_detected",
        "self_loop_rejected",
        "negative_cycle_rejected",
        "topological_order_impossible",
    }

    assert expected_cases.issubset(set(get_case_names()))


@pytest.mark.parametrize(
    "case_name",
    [
        "single_vertex",
        "source_equals_destination",
        "single_edge",
        "simple_dag",
        "dag_multiple_paths",
        "positive_weights",
        "zero_weights",
        "negative_weights_no_cycle",
        "mixed_positive_negative",
        "long_chain",
        "cheaper_indirect_path",
        "multiple_predecessors",
        "equal_cost_paths",
        "parallel_edges",
        "valid_topological_order",
        "dense_acyclic_graph",
        "sparse_graph",
        "all_vertices_reachable",
        "final_distance_validation",
        "graph_immutability",
        "deterministic_results",
    ],
)
def test_expected_distance_cases(case_name):
    case, _, result = run_case(case_name)
    target = case["metadata"]["target"]
    expected_distance = case["metadata"]["expected_distance"]

    assert result["distances"][target] == expected_distance


@pytest.mark.parametrize("case_name,target", [("unreachable_vertex", "D"), ("isolated_vertices", "I1")])
def test_unreachable_vertices_remain_infinite(case_name, target):
    _, _, result = run_case(case_name)
    assert math.isinf(result["distances"][target])


def test_partially_reachable_has_both_finite_and_infinite_distances():
    _, _, result = run_case("partially_reachable")

    assert result["distances"]["B"] == 3
    assert math.isinf(result["distances"]["X"])
    assert math.isinf(result["distances"]["Y"])


def test_path_reconstruction_is_consistent():
    case, _, result = run_case("path_reconstruction")
    expected_path = case["metadata"]["expected_path"]
    source = case["metadata"]["source"]
    target = case["metadata"]["target"]

    assert reconstruct_path(result["previous"], source, target) == expected_path


def test_predecessor_mapping_is_valid():
    case, _, result = run_case("predecessor_validation")
    expected_previous = case["metadata"]["expected_previous"]

    for node, expected_parent in expected_previous.items():
        assert result["previous"][node] == expected_parent


def test_only_source_is_zero_in_initialization_case():
    case, _, result = run_case("distance_initialization")
    source = case["metadata"]["source"]

    assert result["distances"][source] == 0


def test_edge_direction_is_respected():
    _, _, result = run_case("edge_direction_respect")
    assert math.isinf(result["distances"]["C"])


def test_graph_is_not_modified_by_algorithm():
    graph = load_bellman_graph("graph_immutability")
    snapshot = copy.deepcopy(graph.adj_list)

    bellman(graph, "S")

    assert graph.adj_list == snapshot


def test_results_are_stable_and_deterministic():
    graph_1 = load_bellman_graph("deterministic_results")
    graph_2 = load_bellman_graph("deterministic_results")

    result_1 = bellman(graph_1, "S")
    result_2 = bellman(graph_2, "S")

    assert result_1["distances"] == result_2["distances"]
    assert result_1["previous"] == result_2["previous"]


@pytest.mark.parametrize(
    "case_name",
    [
        "source_not_found",
        "destination_not_found",
        "simple_cycle_rejected",
        "directed_cycle_detected",
        "self_loop_rejected",
        "negative_cycle_rejected",
        "topological_order_impossible",
    ],
)
def test_invalid_or_cycle_cases_raise_value_error(case_name):
    case = load_bellman_case(case_name)
    graph = load_bellman_graph(case_name)
    source = case.get("metadata", {}).get("source", "A")

    with pytest.raises(ValueError):
        bellman(graph, source)


def test_invalid_adjacency_structure_raises_loading_error():
    with pytest.raises((TypeError, ValueError, KeyError, AttributeError)):
        _ = load_bellman_graph("invalid_adjacency_structure")


def test_empty_graph_rejected():
    graph = load_bellman_graph("empty_graph")
    with pytest.raises(ValueError):
        bellman(graph, "A")
