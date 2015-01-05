'''
Created on Jan 5, 2015

@author: Francois Belletti
'''

HIGHWAY_COLORS = {'primary'   : 'red',
                  'secondary' : 'blue',
                  'tertiary'  : 'green'}

def plot_network(node_dict, linked_nodes, ax):
    for node_id, neighbours in linked_nodes.iteritems():
        node_lat = float(node_dict[node_id].get('lat'))
        node_lon = float(node_dict[node_id].get('lon'))
        for neigh_id, features in neighbours.iteritems():
            neigh_lat = float(node_dict[neigh_id].get('lat'))
            neigh_lon = float(node_dict[neigh_id].get('lon'))
            mid_lat   = 0.5 * (node_lat + neigh_lat)
            mid_lon   = 0.5 * (node_lon + neigh_lon)
            ax.plot([node_lon, neigh_lon], [node_lat, neigh_lat],
                    c = HIGHWAY_COLORS[features['highway_type']])
            ax.scatter([node_lon, neigh_lon], [node_lat, neigh_lat],
                    c = HIGHWAY_COLORS[features['highway_type']])
            ax.text(mid_lon, mid_lat, features['max_speed'], fontsize = 8)