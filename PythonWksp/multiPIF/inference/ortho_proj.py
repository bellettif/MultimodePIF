'''
Created on Feb 3, 2015

@author: Francois Belletti
'''

import numpy as np

# Project C onto each A->B link
def orthogonal_proj(C, link_coords):
    n_links = len(link_coords)
    #
    C_x = np.ones(n_links, dtype = np.double) * C[0]
    C_y = np.ones(n_links, dtype = np.double) * C[1]
    A_x = np.asarray([l[0][1] for l in link_coords],
                     dtype = np.double)
    A_y = np.asarray([l[0][1] for l in link_coords],
                     dtype = np.double)
    B_x = np.asarray([l[1][0] for l in link_coords],
                     dtype = np.double)
    B_y = np.asarray([l[1][1] for l in link_coords],
                     dtype = np.double)
    # Compute directions vector
    u_x     =   B_x - A_x
    u_y     =   B_y - A_y
    u_norm  =   np.sqrt(u_x ** 2 + u_y ** 2)
    u_x     /=  u_norm
    u_y     /=  u_norm
    # Compute inner products
    A_C_x       =    C_x - A_x
    A_C_y       =    C_y - A_y
    A_C_inner_u =    A_C_x * u_x + A_C_y * u_y
    u_x         *=   A_C_inner_u
    u_y         *=   A_C_inner_u
    # Compute projection
    p_C_x   = A_x + u_x
    p_C_y   = A_y + u_y
    p_C_C_x = C_x - p_C_x
    p_C_C_y = C_y - p_C_y
    dists   = np.sqrt(p_C_C_x ** 2 + p_C_C_y ** 2)
    p_C_x = np.atleast_2d(p_C_x)
    p_C_y = np.atleast_2d(p_C_y)
    projs   = np.hstack((p_C_x.T, p_C_y.T))
    #
    return {'dists' : dists,
            'projs' : projs}









    
    