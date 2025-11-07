import networkx as nx
import json 
from difflib import SequenceMatcher
import os
from xke.LocalEmbeddingStore import add_embedding_to_local_store
from sklearn.metrics.pairwise import cosine_similarity
from xke.LocalEmbeddingStore import get_embedding_from_local_store

INFO_SINK_PENALTY = 20


#define struct EdgeCandidate:
#    src: str
#    target: str
#    cost: float

class EdgeCandidate:
    def __init__(self, src: str, target: str, cost: float):
        self.src = src
        self.target = target
        self.cost = cost



vertex_cost_list = []
edge_cost_list = []
other_cost_list = []

def build_info_flow_graph(graph: nx.DiGraph, mapping: dict):
    info_sources = []
    info_sinks = []

    for vertex in graph.nodes():
        if graph.nodes[vertex].get('type') == 'user': 
            info_sources.append(vertex)
        elif graph.nodes[vertex].get('type') == 'database' or graph.nodes[vertex].get('type') == 'file' or graph.nodes[vertex].get('type') == 'eventsource' :
            info_sinks.append(vertex)

    G = nx.DiGraph()
    for node in info_sources:
        G.add_node(node)

    if mapping is not None:
        info_sinks__new_graph = list(set([mapping.get(node) for node in info_sinks]))
        for node in info_sinks__new_graph:
            G.add_node(node)
    else:
        for node in info_sinks:
            G.add_node(node)
        
    #for each pair of correct_info_source and correct_info_sink, find the shortest path between them
    edgeCandidates = {}
    for info_source in info_sources:
        for info_sink in info_sinks:
            try:
                shortest_path = nx.shortest_path(graph, info_source, info_sink)
            except nx.NetworkXNoPath:
                continue
            print(f"shortest path: {shortest_path}")

            src = info_source
            if mapping is not None:
                target = mapping.get(info_sink)
            target = info_sink
            edgeID = src + "->" + target
            if edgeCandidates.get(edgeID) is not None:
                if len(shortest_path) < edgeCandidates[edgeID].cost:
                    edgeCandidates[edgeID].cost = len(shortest_path)
            else:
                edgeCandidates[edgeID] = EdgeCandidate(src, target, len(shortest_path))

    for edgeID, edgeCandidate in edgeCandidates.items():
        G.add_edge(edgeCandidate.src, edgeCandidate.target, cost=edgeCandidate.cost)
    return G

def get_info_sinks(graph: nx.DiGraph):
    info_sinks = []
    for vertex in graph.nodes():
        if graph.nodes[vertex].get('type') == 'database' or graph.nodes[vertex].get('type') == 'file' or graph.nodes[vertex].get('type') == 'eventsource' :
            info_sinks.append(vertex)
    return info_sinks

def get_info_sources(graph: nx.DiGraph):
    info_sources = []
    for vertex in graph.nodes():
        if graph.nodes[vertex].get('type') == 'user':
            info_sources.append(vertex)
    return info_sources

def map_info_sinks(correct_graph: nx.DiGraph, candidate_graph: nx.DiGraph):
    candidate_info_sinks = get_info_sinks(candidate_graph)
    correct_info_sinks = get_info_sinks(correct_graph)
    mapping = {}
    if len(correct_info_sinks) <= len(candidate_info_sinks):
        for candidate_info_sink in candidate_info_sinks:
            best_similarity = 5
            best_correct_info_sink = None
            for correct_info_sink in correct_info_sinks:
                #select the caondiate that match the type and closests emebdding similarity
                if correct_graph.nodes[correct_info_sink].get('type') == candidate_graph.nodes[candidate_info_sink].get('type'):
                    emb1 = get_embedding_from_local_store(correct_graph.nodes[correct_info_sink].get('name'))
                    emb2 = get_embedding_from_local_store(candidate_graph.nodes[candidate_info_sink].get('name'))
                    similarity = cosine_similarity([emb1], [emb2])[0][0]
                    if similarity < best_similarity:
                        best_similarity = similarity
                        best_correct_info_sink = correct_info_sink
            if best_correct_info_sink is not None:
                mapping[best_correct_info_sink] = candidate_info_sink
            else:
                # this means sinked can't be mapped, we can give large penalty for this
                raise ValueError(f"TODO handle this case: No correct info sink found for candidate info sink: {candidate_info_sink}")
        return mapping
    else:
        raise ValueError("TODO handle this case: Number of correct info sinks is greater than number of candidate info sinks")

def compare_architectures(correct_graph: nx.DiGraph, candidate_graph: nx.DiGraph):
    penalty = 0
    candidate_info_sources = get_info_sources(candidate_graph)
    correct_info_sources = get_info_sources(correct_graph)

    if len(correct_info_sources) != len(candidate_info_sources):
        #we give up
        return 200

    candidate_info_sinks = get_info_sinks(candidate_graph)
    correct_info_sinks = get_info_sinks(correct_graph)
    
    mapping = {}
    g1 = None
    g2 = None
    #we map info sinks and add panelty 
    penalty += INFO_SINK_PENALTY * (len(correct_info_sinks) - len(candidate_info_sinks))
    if len(correct_info_sinks) <= len(candidate_info_sinks):
        mapping = map_info_sinks(correct_graph, candidate_graph)
        g1 = build_info_flow_graph(correct_graph, mapping)
        g2 = build_info_flow_graph(candidate_graph, None)
    else:
        mapping = map_info_sinks(candidate_graph, correct_graph)
        g1 = build_info_flow_graph(correct_graph, None)
        g2 = build_info_flow_graph(candidate_graph, mapping)
    
    return compare_graphs(g1, g2) + penalty

    

def add_graphs_to_embedding_store(graphs: list[nx.DiGraph]):
    strings_to_embed = []
    for graph in graphs:
        for vertex in graph.nodes():
            strings_to_embed.append(vertex)
            strings_to_embed.append(graph.nodes[vertex].get('type', ''))
            strings_to_embed.append(graph.nodes[vertex].get('description', ''))
        for edge in graph.edges():
            strings_to_embed.append(graph.edges[edge].get('type', ''))
            strings_to_embed.append(graph.edges[edge].get('description', ''))
            strings_to_embed.append(graph.edges[edge].get('src', '') + graph.edges[edge].get('target', ''))
    add_embedding_to_local_store(strings_to_embed)

def create_graph_from_json(json_data: dict) -> nx.DiGraph:
    """
    Creates a NetworkX DiGraph from a JSON object with 'Vertices' and 'Edges'.

    Node attributes are read from the 'Vertices' list.
    Edge attributes are read from the 'Edges' list.
    """
    # Initialize a new directed graph
    G = nx.DiGraph()

    # Process and add nodes
    if 'Vertices' in json_data:
        for node_data in json_data['Vertices']:
            # The 'name' key is used as the node ID
            node_name = node_data['name']
            
            # Use all other keys as node attributes
            attributes = node_data.copy()
            #del attributes['name'] 
            
            G.add_node(node_name, **attributes)

    # Process and add edges
    if 'Edges' in json_data:
        for edge_data in json_data['Edges']:
            # Get the source and target node names
            source = edge_data['src']
            target = edge_data['target']
            
            # Use all other keys as edge attributes
            attributes = edge_data.copy()
            #del attributes['src']
            #del attributes['target']
            
            G.add_edge(source, target, **attributes)
    return G

#based on embedding similarity
def string_similarity_cost(s1: str, s2: str) -> float:
    s1 = s1.strip().lower()
    s2 = s2.strip().lower()
    if s1 == '' or s2 == '':
        return 2.0
    emb1 = get_embedding_from_local_store(s1)
    emb2 = get_embedding_from_local_store(s2)
    similarity = cosine_similarity([emb1], [emb2])[0][0]
    return 1.0 - similarity
   


def string_similarity_cost_using_sequence_matcher(s1: str, s2: str) -> float:
    """
    Calculates a cost between 0.0 and 1.0 based on string similarity.
    Cost = 1.0 - similarity_ratio
    """
    ratio = SequenceMatcher(None, s1, s2).ratio()
    #print(f"string_similarity_cost: {s1} - {s2} - {1.0 -ratio}")
    return 1.0 - ratio

# --- 2. Define Custom Cost Functions ---
"""
    Calculates the cost of substituting node1 for node2.
    Cost is 0.0 for identical, 1.0 for completely different.
"""

def custom_node_subst_cost(node1_attrs: dict, node2_attrs: dict) -> float:
    # Get attributes, with defaults
    type1 = node1_attrs.get('type', '')
    type2 = node2_attrs.get('type', '')
    desc1 = node1_attrs.get('description', '')
    desc2 = node2_attrs.get('description', '')

    #get node name
    name1 = node1_attrs.get('name', '')
    name2 = node2_attrs.get('name', '')
    name_cost = string_similarity_cost(name1, name2)

    # --- Calculate cost for each part ---
    
    # Type cost: 0.0 if same, 1.0 if different (binary)
    if type1 == type2:
        type_cost = 0.0
    else:
        type_cost = string_similarity_cost(type1, type2)
    
    desc_cost = string_similarity_cost(desc1, desc2)    
    #cost = (type_cost + min(name_cost, desc_cost))/2
    cost = (2*type_cost + name_cost)/3 
    vertex_cost_list.append(cost)
    #print(f"{cost.round(2)} vertex_cost: {name1} = {name2} | {type1} = {type2} | {desc1} = {desc2}")
    return cost

def custom_edge_subst_cost(edge1_attrs: dict, edge2_attrs: dict) -> float:
    """
    Calculates the cost of substituting edge1 for edge2.
    Based entirely on the 'type' attribute.
    """
    type1 = edge1_attrs.get('type', '')
    type2 = edge2_attrs.get('type', '')
    type_cost = string_similarity_cost(type1, type2)

    edge1 = edge1_attrs.get('src', '') + edge1_attrs.get('target', '')
    edge2 = edge2_attrs.get('src', '') + edge2_attrs.get('target', '')
    edge_cost = string_similarity_cost(edge1, edge2)
    cost = (type_cost + edge_cost)/2
    edge_cost_list.append(cost)
    print(f"edge_cost: {edge1} - {edge2} - {cost}")
    return cost

# For insertion and deletion, we'll use a constant cost of 1.0.
# This means inserting or deleting any node/edge has a fixed penalty.
# You could make these more complex (e.g., cheaper to delete a 'user' 
# node than a 'service' node).
default_ins_del_cost = lambda attrs: 0.3

def custom_node_ins__del_cost(node_attrs: dict) -> float:
    """
    node_type = node_attrs.get('type', 'unknown')
    
    if node_type == 'database':
        return 0.7  # Most "expensive" to add
    elif node_type == 'service':
        return 0.4  # More "expensive" to add
    elif node_type == 'user':
        return 1.5  # "Cheaper" to add
    else:
        return 1.0  # Default cost
     """
    cost = 3
    other_cost_list.append(cost)
    return cost


"""

Use networkx.graph_edit_distance to compute the distance.
"""
def compare_graphs(graph1: nx.DiGraph, graph2: nx.DiGraph):
    """
    Compare two graphs and return the difference.
    """
    #For your 100-node graphs, you must use the upper_bound or timeout parameters to force an approximate solution.
    upper_bound = 100
    timeout = 10
    return nx.graph_edit_distance(graph1, graph2, 
        upper_bound=upper_bound, timeout=timeout, 
        node_subst_cost=custom_node_subst_cost, 
        edge_subst_cost=custom_edge_subst_cost, 
        node_del_cost=custom_node_ins__del_cost, 
        node_ins_cost=custom_node_ins__del_cost, 
        edge_del_cost=default_ins_del_cost, 
        edge_ins_cost=default_ins_del_cost)


# --- Example Usage ---
#https://jsondiff.com/

def eval_main():
    g1_json = json.load(open('/Users/srinath/code/arch-autogen/solutions/ground_truth/Library.json'))
    g2_json = json.load(open('/Users/srinath/code/arch-autogen/solutions/model-problems-output/v1/Library.json'))


    g3_json = json.load(open('/Users/srinath/code/arch-autogen/solutions/model-problems-output/v1/sea-buoy.json'))
    g1 = create_graph_from_json(g1_json)
    #save  graph as dot file
    #nx.write_dot(g1, 'g1.dot')
    #print(g1.nodes(data=True))
    #doe each vertex in graph, print the id and the data
    for node in g1.nodes():
        print("###",node, g1.nodes[node])
    #print(g1.edges(data=True))
    g2 = create_graph_from_json(g2_json)
    g3 = create_graph_from_json(g3_json)

    graphs = []
    graphs.append(g1)
    graphs.append(g2)
    graphs.append(g3)

    dir = '/Users/srinath/code/arch-autogen/solutions/model-problems-output/v1'

    for file in os.listdir(dir):
        if file.endswith('.json'):
            g_json = json.load(open(os.path.join(dir, file)))
            g = create_graph_from_json(g_json)
            graphs.append(g)
    
    add_graphs_to_embedding_store(graphs)

    #print("compare_graphs(g1, g1) - same:", compare_graphs(g1, g1))
    print("compare_graphs(g1, g2) - two solutions:", compare_graphs(g1, g2))
    #print("compare_graphs(g1, g3) - different:", compare_graphs(g1, g3))

    #for g in graphs:
    #    print(f"compare_graphs(g1, g) - {g.name}:", compare_graphs(g1, g))

    #print avg, min, max of vertex_cost, edge_cost, other_cost
    print(f"avg, min, max of vertex_cost: {sum(vertex_cost_list)/len(vertex_cost_list)}, {min(vertex_cost_list)}, {max(vertex_cost_list)}")
    print(f"avg, min, max of edge_cost: {sum(edge_cost_list)/len(edge_cost_list)}, {min(edge_cost_list)}, {max(edge_cost_list)}")
    print(f"avg, min, max of other_cost: {sum(other_cost_list)/len(other_cost_list)}, {min(other_cost_list)}, {max(other_cost_list)}")

def eval_main1(): 
    g1_json = json.load(open('/Users/srinath/code/arch-autogen/solutions/ground_truth/Library.json'))
    g1 = create_graph_from_json(g1_json)
    g2 = build_info_flow_graph(g1)
    print(g2.nodes(data=True))
    print(g2.edges(data=True))


def eval_main2():
    g1_json = json.load(open('/Users/srinath/code/arch-autogen/solutions/ground_truth/Library.json'))
    g2_json = json.load(open('/Users/srinath/code/arch-autogen/solutions/model-problems-output/v1/Library.json'))
    g1 = create_graph_from_json(g1_json)
    g2 = create_graph_from_json(g2_json)
    print("final cost:", compare_architectures(g1, g2))
