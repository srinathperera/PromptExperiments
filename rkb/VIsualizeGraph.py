import networkx as nx
from pyvis.network import Network

# Create a NetworkX graph
G = nx.Graph()
G.add_edge("A", "B")
G.add_edge("A", "C")
G.add_edge("B", "C")

# Create a Pyvis network
net = Network(notebook=True, cdn_resources='in_line')
net.from_nx(G)

# Generate the interactive HTML file
net.show("graph.html")