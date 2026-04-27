def test_dijkstra_simple():
    graph = load_graph("data/simple_graph.json") #on doit implementer load_graph
    result = dijkstra(graph , source = "A" , target="C")

    assert result["distance"] == 3
    assert result["path"] == ["A","B","C"]