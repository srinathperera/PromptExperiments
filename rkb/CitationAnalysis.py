import pandas as pd
from thefuzz import process
import pandas as pd
import networkx as nx
import io


def fuzzy_match(title, titles2matches, score_cutoff=80):
    best_match = process.extractOne(title, titles2matches, score_cutoff=score_cutoff)
    if best_match is None:
        return None
    return best_match[0]

def build_citation_graph(papers_csv_file, references_csv_file):
    papers_df = pd.read_csv(papers_csv_file)
    references_df = pd.read_csv(references_csv_file)
    
    idIndex = 0
    title2id = {}
    titles2matches = []

    for _, row in papers_df.iterrows():
        title = row['title']
        if fuzzy_match(title, titles2matches, score_cutoff=85) is not None:
            continue
        title2id[title] = idIndex
        idIndex += 1
        titles2matches.append(title)
    
    citations_list = []
    for _, row in references_df.iterrows():
        title = row['src_title']
        citation = row['target_title']

        citation_title  = fuzzy_match(citation, titles2matches, score_cutoff=85)

        if citation_title is  None:
            #this is a new paper, we just add it to the list
            title2id[citation] = idIndex
            idIndex += 1
            titles2matches.append(citation)
            citation_title = citation
        ##else this paper already in the paper list, both case add ciation

        if citation_title not in title2id:
            print(citation_title, "not in title2id", title2id)
        
        paper_id = title2id[title]
        citation_id = title2id[citation_title]
        #assert both ids are not None
        assert paper_id is not None and citation_id is not None
        citations_list.append({'source': paper_id, 'target': citation_id})
    
    # Convert list to DataFrame
    citations = pd.DataFrame(citations_list)
    
    #write nodes and edge of citation graph to csv
    title2id_df = pd.DataFrame(list(title2id.items()), columns=['title', 'id'])
    title2id_df.to_csv('temp/citations_nodes.csv', index=False)    
    citations.to_csv('temp/citations_edges.csv', index=False)

def analyze_citation_graph(citations_nodes_file, citations_edges_file):
    df = pd.read_csv(citations_edges_file)

    weighted_edges = df.groupby(['source', 'target']).size().reset_index(name='weight')

    print("--- Edges with Calculated Weights ---")
    print(weighted_edges.head())
    print("-" * 35)


    # --- 3. Load the graph into NetworkX as a weighted DiGraph ---
    # A DiGraph is used because citations are directed (A cites B doesn't mean B cites A).
    # The 'weight' column in our DataFrame is passed as an edge attribute.
    G = nx.from_pandas_edgelist(
        weighted_edges,
        source='citing_paper',
        target='cited_paper',
        edge_attr='weight',
        create_using=nx.DiGraph()
    )

    print(f"\nGraph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")


    # --- 2. Find and Add Bibliographic Coupling Edges ---
    # Bibliographic coupling: Two papers are coupled if they both cite the same paper(s).
    # The strength is the number of common papers they cite.

    print("\nCalculating Bibliographic Coupling...")
    G_bib_coupling = nx.Graph() # Create a new undirected graph for this relationship
    # Use combinations to get all unique pairs of nodes
    for node1, node2 in combinations(G.nodes(), 2):
        # G.successors(n) gives the nodes that n cites
        common_citations = set(G.successors(node1)) & set(G.successors(node2))
        coupling_strength = len(common_citations)

        if coupling_strength > 0:
            G_bib_coupling.add_edge(node1, node2, weight=coupling_strength)

    print(f"Found {G_bib_coupling.number_of_edges()} bibliographic coupling edges.")
    print("Example Edges (Node1, Node2, {'weight': Strength}):")
    print(list(G_bib_coupling.edges(data=True))[:3])
    print("-" * 55)


    # --- 3. Find and Add Co-citation Edges ---
    # Co-citation: Two papers are co-cited if they are both cited by the same paper(s).
    # The strength is the number of common papers that cite them.

    print("\nCalculating Co-citation...")
    G_cocitation = nx.Graph() # Create a new undirected graph
    for node1, node2 in combinations(G.nodes(), 2):
        # G.predecessors(n) gives the nodes that cite n
        common_citors = set(G.predecessors(node1)) & set(G.predecessors(node2))
        cocitation_strength = len(common_citors)

        if cocitation_strength > 0:
            G_cocitation.add_edge(node1, node2, weight=cocitation_strength)

    print(f"Found {G_cocitation.number_of_edges()} co-citation edges.")
    print("Example Edges (Node1, Node2, {'weight': Strength}):")
    print(list(G_cocitation.edges(data=True))[:3])
    print("-" * 55)


    # --- 4. Run the PageRank algorithm ---
    # We tell PageRank to use our 'weight' attribute.
    # A higher alpha means more importance is placed on the link structure.
    pagerank_scores = nx.pagerank(G, alpha=0.85, weight='weight')


    # --- 5. List papers by their importance (PageRank score) ---
    # We sort the dictionary of scores in descending order.
    sorted_papers = sorted(pagerank_scores.items(), key=lambda item: item[1], reverse=True)

    print("\n--- Papers Ranked by PageRank Importance ---")
    for i, (paper, score) in enumerate(sorted_papers):
        print(f"{i+1}. Paper ID: {paper:<10} | PageRank Score: {score:.4f}")
    print("-" * 45)

    build_citation_graph('temp/papers.csv', 'temp/references.csv')