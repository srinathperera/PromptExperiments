import json
import io
from typing import Dict, List, Any, Set, Tuple

def sort_and_print_edges(graph_json: Dict[str, Any]):
    buffer = io.StringIO()
    """
    Prints the graph edges in a specific order:
    1. Edges starting with a 'user' vertex (sorted by source name).
    2. Edges starting with a vertex that only has outgoing connections (sorted by source name).
    3. The rest of the edges (sorted by source name, then target name).

    Args:
        graph_json: A dictionary representing the graph containing 'Vertices' and 'Edges'.
    """
    
    vertices: List[Dict[str, str]] = graph_json.get('Vertices', [])
    edges: List[Dict[str, str]] = graph_json.get('Edges', [])

    # 1. Create lookup maps for quick access to vertex properties
    vertex_types: Dict[str, str] = {v['name']: v['type'] for v in vertices}
    
    incoming_counts: Dict[str, int] = {v['name']: 0 for v in vertices}
    outgoing_counts: Dict[str, int] = {v['name']: 0 for v in vertices}

    # Calculate incoming and outgoing degrees for all vertices
    for edge in edges:
        src = edge.get('src')
        target = edge.get('target')
        if src in outgoing_counts:
            outgoing_counts[src] += 1
        if target in incoming_counts:
            incoming_counts[target] += 1

    # 2. Identify vertices that ONLY have outgoing edges
    # FIX: Changed iteration variable and lookup key from 'name' (which was a dict) to v['name']
    # (i.e., outgoing_count > 0 AND incoming_count == 0)
    only_outgoing_vertices: Set[str] = {
        v['name'] for v in vertices 
        if outgoing_counts.get(v['name'], 0) > 0 and incoming_counts.get(v['name'], 0) == 0
    }

    def custom_sort_key(edge: Dict[str, str]) -> Tuple[int, str, str]:
        """
        Custom key function to define the sorting priority.
        The tuple's elements are used for primary, secondary, and tertiary sorting.
        """
        src = edge['src']
        target = edge['target']
        
        is_user = vertex_types.get(src) == 'user'
        is_only_outgoing = src in only_outgoing_vertices

        # Grouping Logic:
        # Group 0: Vertices of type 'user' (Highest Priority)
        # Group 1: Vertices with only outgoing edges (Second Priority)
        # Group 2: The rest of the vertices (Lowest Priority)

        priority: int
        if is_user:
            # Rule 1: Edges starting with a vertice of type users first (Priority 0)
            priority = 0
        elif is_only_outgoing:
            # Rule 2: Then print edges where starting vertice only have outgoing edges (Priority 1)
            priority = 1
        else:
            # Rule 3: The rest of the edges (Priority 2)
            priority = 2
        
        # All groups are sorted by source name (secondary key) 
        # and then by target name (tertiary key, for determinism)
        return (priority, src, target)

    # 3. Sort the edges using the custom key
    sorted_edges = sorted(edges, key=custom_sort_key)

    # 4. Print the result
    current_group: int = -1
    
    for edge in sorted_edges:
        src = edge['src']
        target = edge['target']
        buffer.write(f"{src} -> {target}\n")
    return buffer.getvalue()
        

        
        

# Input JSON data provided by the user
input_graph = {
    'Vertices': [
        {'name': 'Patient', 'type': 'user', 'description': 'Patients who schedule appointments.'}, 
        {'name': 'Administrator', 'type': 'user', 'description': 'Administrators who manage appointment details.'}, 
        {'name': 'AppointmentService', 'type': 'service', 'description': 'Service for managing appointment creation, listing, reading, and cancellation.'}, 
        {'name': 'PaymentService', 'type': 'service', 'description': 'Service to handle payments for appointments.'}, 
        {'name': 'NotificationService', 'type': 'service', 'description': 'Service to send notifications to users about doctor arrival.'}, 
        {'name': 'AppointmentDatabase', 'type': 'database', 'description': 'Database to store appointment details.'}, 
        {'name': 'PaymentDatabase', 'type': 'database', 'description': 'Database to store payment information'}, 
        {'name': 'DoctorArrivalEvent', 'type': 'eventsource', 'description': 'Event triggered when a doctor arrives.'}
    ], 
    'Edges': [
        {'src': 'Patient', 'target': 'AppointmentService', 'type': 'sync'}, 
        {'src': 'Administrator', 'target': 'AppointmentService', 'type': 'sync'}, 
        {'src': 'AppointmentService', 'target': 'AppointmentDatabase', 'type': 'sync'}, 
        {'src': 'AppointmentService', 'target': 'PaymentService', 'type': 'sync'}, 
        {'src': 'PaymentService', 'target': 'PaymentDatabase', 'type': 'sync'}, 
        {'src': 'DoctorArrivalEvent', 'target': 'NotificationService', 'type': 'async'}, 
        {'src': 'NotificationService', 'target': 'Patient', 'type': 'async'}
    ], 
    'thinking': [
        'Identified users: Patient, Administrator', 
        'Identified services: AppointmentService, PaymentService, NotificationService', 
        'Identified databases: AppointmentDatabase, PaymentDatabase', 
        'Identified eventsource: DoctorArrivalEvent', 
        'Represented the interactions as a SDG with appropriate edge types.'
    ]
}

# Run the function
#print(sort_and_print_edges(input_graph))
