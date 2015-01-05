'''
Created on Jan 4, 2015

    Plot tools for json documents in ZenMap format.
    This format is now deprecated.

@author: Francois Belletti
'''

HIGHWAY_COLOR_DICT = {'motorway' : 'orange',
                      'primary' : 'blue',
                      'secondary' : 'green',
                      'tertiary' : 'purple',
                      'bus_guideway' : 'light-blue'}

def plot_doc(ax, doc):
    geom = doc['geometry']
    geom_type = geom['type']
    highway_type = doc['properties']['highway']
    color = 'grey'
    dashes = False
    if highway_type in HIGHWAY_COLOR_DICT:
        color = HIGHWAY_COLOR_DICT[highway_type]
    if doc['properties']['railway'] == 'subway':
        color = 'red'
        dashes = True
    if doc['properties']['route'] == 'bus':
        color = 'yellow'
        dashes = True
    if doc['properties']['route'] == 'ferry':
        color = 'cyan'
        dashes = True 
    if doc['properties']['route'] == 'train':
        color = 'magenta'
        dashes = True    
    if geom_type == 'LineString':
        coord_list = geom['coordinates']
        lons = [x[0] for x in coord_list]
        lats = [x[1] for x in coord_list]
        if dashes:
            ax.plot(lons, lats, c = color, linestyle = '--')
        else:
            ax.plot(lons, lats, c = color)
    if geom_type == 'Point' and doc['properties']['railway'] in ['subway_entrance',
                                                                 'station',
                                                                 'tram_stop']:
        coords = geom['coordinates']
        ax.scatter(coords[0], coords[1], c = 'red')
    if geom_type == 'Point' and doc['properties']['highway'] == 'bus_stop':
        coords = geom['coordinates']
        print doc
        ax.scatter(coords[0], coords[1], c = 'yellow')
    