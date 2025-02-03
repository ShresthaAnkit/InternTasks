# Function to infer a node's "name" based on its connected streets
def get_node_name(node_id, G):
    # Get all edges connected to this node
    edges = list(G.edges(node_id, data=True))
    
    # Collect street names from edges
    street_names = [data['name'] for  v, key, data in edges if 'name' in data]
    
    # If no street names are found, return a default
    if not street_names:
        return f"Node {node_id} (Unnamed streets)"
    
    # Return a concatenated string of street names (or just the first street name)
    return ', '.join(street_names[:2])  # Limiting to first 2 street names for simplicity

# Example: Get the "name" of the first node
node_id = list(G.nodes)[0]
node_name = get_node_name(node_id, G)
print(f"Node {node_id} is near: {node_name}")