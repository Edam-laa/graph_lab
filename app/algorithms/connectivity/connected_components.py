from collections import deque


class ConnectivityChecker:
    @staticmethod
    def is_connected(graph):
        if not graph.nodes:
            return True

        visited = set()
        start = graph.nodes[0]

        q = deque([start])
        visited.add(start)

        while q:
            node = q.popleft()

            for nei in graph.adj[node]:
                if nei not in visited:
                    visited.add(nei)
                    q.append(nei)

        return len(visited) == len(graph.nodes)