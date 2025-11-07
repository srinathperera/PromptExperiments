import json
import networkx as nx
import matplotlib.pyplot as plt

def visualize_model(file_path):
    with open(file_path, 'r') as file:
        model = json.load(file)
    #visualize the model with NetworkX
    G = nx.Graph()
    for node in model['Vertices']:
        G.add_node(node['name'], type=node['type'])
    for edge in model['Edges']:
        G.add_edge(edge['src'], edge['target'])
    nx.draw(G, with_labels=True)
    plt.show()
    return model

if __name__ == "__main__":
    model = visualize_model("data/models/s1.json")
    print(model)