import osmnx as ox
import geopandas as gpd
import networkx as nx

# Define the place name or coordinates
place_name = "Kathmandu, Nepal"  

# Download the street network
G = ox.graph_from_place(place_name, network_type='drive')  # 'all' includes all types of roads
G = ox.project_graph(G, to_crs="EPSG:3857")  # Web Mercator
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Start timer
        result = func(*args, **kwargs)
        end_time = time.time()  # End timer
        print(f"{func.__name__} executed in {end_time - start_time:.6f} seconds")
        return result
    return wrapper
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

route = find_route(orig,dest)
ox.plot_graph_route(G,route=route)

# Define the origin and destination nodes (choose two random nodes in the graph)
orig = list(G.nodes())[0]
dest = list(G.nodes())[100]

# Apply Dijkstra's algorithm to find the shortest path
# The weight parameter 'length' ensures that we are finding the shortest path by distance
@timing_decorator
def find_route(orig,dest):
    route = nx.dijkstra_path(G, orig, dest, weight='length')
    return route

ox.plot.plot_graph_route(G, [31019057,2169068697],node_size=0,route_linewidth=1,orig_dest_size=10)