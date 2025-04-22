import networkx as nx
from utils.tree_visualizer import draw_graph

# Create a basic tree graph manually
graph = nx.DiGraph()

# Example tree structure:
#         0
#       / | \
#      1  2  3
#         |
#         4
#        / \
#       5   6

# Add edges to represent the tree
graph.add_edges_from([
    (0, 1),
    (0, 2),
    (0, 3),
    (2, 4),
    (4, 5),
    (4, 6)
])

# Add labels to the nodes
labels = {
    0: "Root",
    1: "Child 1",
    2: "Child 2",
    3: "Child 3",
    4: "Grandchild",
    5: "Leaf A",
    6: "Leaf B"
}
nx.set_node_attributes(graph, labels, "label")

# Draw the interactive graph
draw_graph(graph)
