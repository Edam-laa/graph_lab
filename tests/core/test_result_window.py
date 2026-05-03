#!/usr/bin/env python3
"""
Test script to verify the Result Window displays backend results correctly.

This script:
1. Creates a sample graph
2. Simulates an algorithm request
3. Verifies the ResultWindow can properly display the results
"""

import sys
import json
from pathlib import Path

import pytest

pytest.importorskip("PySide6")

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from front.MainWindow import MainWindow
from front.ResultWindow import ResultWindow


def test_result_window_with_sample_data():
    """Test ResultWindow with sample graph data and algorithm results."""
    
    # Create Qt Application
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = MainWindow()
    
    # Sample graph data (simulating what get_graph_data() returns)
    sample_data = {
        "graph": {
            "nodes": ["A", "B", "C", "D"],
            "edges": [
                {"from": "A", "to": "B", "weight": 4, "capacity": 1},
                {"from": "A", "to": "C", "weight": 2, "capacity": 1},
                {"from": "B", "to": "C", "weight": 1, "capacity": 1},
                {"from": "B", "to": "D", "weight": 5, "capacity": 1},
                {"from": "C", "to": "D", "weight": 8, "capacity": 1},
            ],
            "node_positions": {
                "A": {"x": 0, "y": 0},
                "B": {"x": 100, "y": 0},
                "C": {"x": 50, "y": 100},
                "D": {"x": 150, "y": 100},
            },
            "directed": True,
            "weighted": True,
        },
        "algorithm": {
            "name": "Dijkstra",
            "category": "shortest_path",
            "params": {"source": "A", "sink": "D"}
        },
        "result": {
            "path": ["A", "C", "B", "D"],
            "distances": {
                "A": 0,
                "B": 3,
                "C": 2,
                "D": 8,
            },
            "steps": [
                "Initialize: distance[A] = 0, all others = ∞",
                "Process A: Update B(4), C(2)",
                "Process C: Update B(3), D(10)",
                "Process B: Update D(8)",
                "Path found: A -> C -> B -> D"
            ]
        },
        "execution": {
            "status": "success",
            "execution_time": 0.0045,
            "complexity": "O((V + E) log V)",
            "message": ""
        }
    }
    
    # Store in main window (simulating what _run_algo does)
    main_window._last_graph_data = sample_data
    
    # Create and show result window
    result_window = ResultWindow(main_window)
    result_window.draw_graph(sample_data)
    result_window.apply_result(sample_data)
    result_window._populate_info(sample_data)
    result_window.show()
    
    print("✅ ResultWindow created and displayed successfully!")
    print(f"   Algorithm: {sample_data['algorithm']['name']}")
    print(f"   Path found: {' -> '.join(sample_data['result']['path'])}")
    print(f"   Execution time: {sample_data['execution']['execution_time']:.4f}s")
    
    # Run Qt event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    test_result_window_with_sample_data()
