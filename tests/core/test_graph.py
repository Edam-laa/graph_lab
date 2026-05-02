from app.core.graph import Graph


def test_get_nodes_is_sorted():
	graph = Graph(directed=False)
	graph.add_node("C")
	graph.add_node("A")
	graph.add_node("B")

	assert graph.get_nodes() == ["A", "B", "C"]


def test_get_edges_undirected_has_no_duplicates():
	graph = Graph(directed=False)
	graph.add_edge("A", "B", 1)
	graph.add_edge("B", "A", 1)

	edges = graph.get_edges()
	assert len(edges) == 1
	assert edges[0][:3] in [("A", "B", 1), ("B", "A", 1)]


def test_has_negative_weights_detects_negative_edge():
	graph = Graph(directed=True)
	graph.add_edge("A", "B", -2)

	assert graph.has_negative_weights() is True


def test_has_negative_weights_false_for_non_negative_edges():
	graph = Graph(directed=True)
	graph.add_edge("A", "B", 2)

	assert graph.has_negative_weights() is False


def test_degree_counts_outgoing_edges():
	graph = Graph(directed=True)
	graph.add_edge("A", "B", 1)
	graph.add_edge("A", "C", 1)

	assert graph.degree("A") == 2
	assert graph.degree("B") == 0


def test_get_all_adjacent_includes_incoming_for_directed():
	graph = Graph(directed=True)
	graph.add_edge("A", "B", 1)
	graph.add_edge("C", "B", 1)

	adjacent = set(graph.get_all_adjacent("B"))
	assert adjacent == {"A", "C"}
