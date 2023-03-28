import numpy as np

#transformation functions
#take 1D arrays of size (3,) or 4D arrays with last two dimensions giving vector elements (* x * x 3 x 1)
#    cartesian: (x, y, z)
#    cylindrical: (rho, phi, z)
#    spherical: (r, theta, phi)
#
# MAY WANT TO MAKE SEPARATE CLASS FOR THESE

##coordinate transformations
def cartesian_to_cylindrical_coordinates(coordinate_array_cartesian):
    if coordinate_array_cartesian.ndim == 1:
        coordinate_array_cartesian = coordinate_array_cartesian[np.newaxis,np.newaxis,:,np.newaxis]
        
    rho = np.sqrt(coordinate_array_cartesian[:,:,0,np.newaxis,:]**2 + coordinate_array_cartesian[:,:,1,np.newaxis,:]**2)
    phi = np.arctan2(coordinate_array_cartesian[:,:,1,np.newaxis,:], coordinate_array_cartesian[:,:,0,np.newaxis,:])
    z = coordinate_array_cartesian[:,:,2,np.newaxis,:]
    return np.concatenate((rho, phi, z), axis=2)

def cylindrical_to_cartesian_coordinates(coordinate_array_cylindrical):
    if coordinate_array_cylindrical.ndim == 1:
        coordinate_array_cylindrical = coordinate_array_cylindrical[np.newaxis,np.newaxis,:,np.newaxis]
        
    x = coordinate_array_cylindrical[:,:,0,np.newaxis,:] * np.cos(coordinate_array_cylindrical[:,:,1,np.newaxis,:])
    y = coordinate_array_cylindrical[:,:,0,np.newaxis,:] * np.sin(coordinate_array_cylindrical[:,:,1,np.newaxis,:])
    z = coordinate_array_cylindrical[:,:,2,np.newaxis,:]
    return np.concatenate((x, y, z), axis=2)

def cartesian_to_spherical_coordinates(coordinate_array_cartesian):
    if coordinate_array_cartesian.ndim == 1:
        coordinate_array_cartesian = coordinate_array_cartesian[np.newaxis,np.newaxis,:,np.newaxis]
        
    r = np.sqrt(coordinate_array_cartesian[:,:,0,np.newaxis,:]**2 + coordinate_array_cartesian[:,:,1,np.newaxis,:]**2 + coordinate_array_cartesian[:,:,2,np.newaxis,:]**2)
    theta = np.arccos(coordinate_array_cartesian[:,:,2,np.newaxis,:]/r)
    phi = np.arctan2(coordinate_array_cartesian[:,:,1,np.newaxis,:], coordinate_array_cartesian[:,:,0,np.newaxis,:])
    return np.concatenate((r, theta, phi), axis=2)
    
def spherical_to_cartesian_coordinates(coordinate_array_spherical):
    if coordinate_array_spherical.ndim == 1:
        coordinate_array_spherical = coordinate_array_spherical[np.newaxis,np.newaxis,:,np.newaxis]
        
    x = coordinate_array_spherical[:,:,0,np.newaxis,:] * np.sin(coordinate_array_spherical[:,:,1,np.newaxis,:]) * np.cos(coordinate_array_spherical[:,:,2,np.newaxis,:])
    y = coordinate_array_spherical[:,:,0,np.newaxis,:] * np.sin(coordinate_array_spherical[:,:,1,np.newaxis,:]) * np.sin(coordinate_array_spherical[:,:,2,np.newaxis,:])
    z = coordinate_array_spherical[:,:,0,np.newaxis,:] * np.cos(coordinate_array_spherical[:,:,1,np.newaxis,:])
    return np.concatenate((x, y, z), axis=2)

def cylindrical_to_spherical_coordinates(coordinate_array_cylindrical):
    if coordinate_array_cylindrical.ndim == 1:
        coordinate_array_cylindrical = coordinate_array_cylindrical[np.newaxis,np.newaxis,:,np.newaxis]
        
    r = np.sqrt(coordinate_array_cylindrical[:,:,0,np.newaxis,:]**2 + coordinate_array_cylindrical[:,:,2,np.newaxis,:]**2)
    theta = np.arccos(coordinate_array_cylindrical[:,:,2,np.newaxis,:]/r)
    phi = coordinate_array_cylindrical[:,:,1,np.newaxis,:]
    return np.concatenate((r, theta, phi), axis=2)

def spherical_to_cylindrical_coordinates(coordinate_array_spherical):
    if coordinate_array_spherical.ndim == 1:
        coordinate_array_spherical = coordinate_array_spherical[np.newaxis,np.newaxis,:,np.newaxis]
        
    rho = coordinate_array_spherical[:,:,0,np.newaxis,:] * np.sin(coordinate_array_spherical[:,:,1,np.newaxis,:])
    phi = coordinate_array_spherical[:,:,2,np.newaxis,:]
    z = coordinate_array_spherical[:,:,0,np.newaxis,:] * np.cos(coordinate_array_spherical[:,:,1,np.newaxis,:])
    return np.concatenate((rho, phi, z), axis=2)

#vector transformations
def cartesian_to_cylindrical_vector(vector_array, coordinate_array, **kwargs):
    if vector_array.ndim == 1:
        vector_array = vector_array[np.newaxis,np.newaxis,:,np.newaxis]
    if coordinate_array.ndim == 1:
        coordinate_array = coordinate_array[np.newaxis,np.newaxis,:,np.newaxis]
    
    coordinate_type = kwargs.get('coordinate_type', 'cartesian')
    
    if coordinate_type == 'cartesian':
        coordinate_array = cartesian_to_cylindrical_coordinates(coordinate_array)
        
    elif coordinate_type == 'spherical':
        coordinate_array = spherical_to_cylindrical_coordinates(coordinate_array)
    
    phi_list = coordinate_array[:,:,1,np.newaxis,:]
    
    T = np.concatenate((
                np.concatenate((
                        np.cos(phi_list),
                        np.sin(phi_list),
                        np.zeros(phi_list.shape)),
                    axis=3),
                np.concatenate((
                        -np.sin(phi_list),
                        np.cos(phi_list),
                        np.zeros(phi_list.shape)),
                    axis=3),
                np.concatenate((
                        np.zeros(phi_list.shape),
                        np.zeros(phi_list.shape),
                        np.ones(phi_list.shape)),
                    axis=3)),
            axis=2)
    return np.matmul(T, vector_array)

def cylindrical_to_cartesian_vector(vector_array, coordinate_array, **kwargs):
    if vector_array.ndim == 1:
        vector_array = vector_array[np.newaxis,np.newaxis,:,np.newaxis]
    if coordinate_array.ndim == 1:
        coordinate_array = coordinate_array[np.newaxis,np.newaxis,:,np.newaxis]
        
    coordinate_type = kwargs.get('coordinate_type', 'cartesian')
    
    if coordinate_type == 'cartesian':
        coordinate_array = cartesian_to_cylindrical_coordinates(coordinate_array)
        
    elif coordinate_type == 'spherical':
        coordinate_array = spherical_to_cylindrical_coordinates(coordinate_array)
    
    phi_list = coordinate_array[:,:,1,np.newaxis,:]
    
    T = np.concatenate((
                np.concatenate((
                        np.cos(phi_list),
                        -np.sin(phi_list),
                        np.zeros(phi_list.shape)),
                    axis=3),
                np.concatenate((
                        np.sin(phi_list),
                        np.cos(phi_list),
                        np.zeros(phi_list.shape)),
                    axis=3),
                np.concatenate((
                        np.zeros(phi_list.shape),
                        np.zeros(phi_list.shape),
                        np.ones(phi_list.shape)),
                    axis=3)),
            axis=2)
    return np.matmul(T, vector_array)

def cartesian_to_spherical_vector(vector_array, coordinate_array, **kwargs):
    if vector_array.ndim == 1:
        vector_array = vector_array[np.newaxis,np.newaxis,:,np.newaxis]
    if coordinate_array.ndim == 1:
        coordinate_array = coordinate_array[np.newaxis,np.newaxis,:,np.newaxis]
        
    coordinate_type = kwargs.get('coordinate_type', 'cartesian')
    
    if coordinate_type == 'cartesian':
        coordinate_array = cartesian_to_spherical_coordinates(coordinate_array)
        
    elif coordinate_type == 'cylindrical':
        coordinate_array = cylindrical_to_spherical_coordinates(coordinate_array)
    
    theta_list = coordinate_array[:,:,1,np.newaxis,:]
    phi_list = coordinate_array[:,:,2,np.newaxis,:]
    
    T = np.concatenate((
                np.concatenate((
                        np.sin(theta_list) * np.cos(phi_list),
                        np.sin(theta_list) * np.sin(phi_list),
                        np.cos(theta_list)),
                    axis=3),
                np.concatenate((
                        np.cos(theta_list) * np.cos(phi_list),
                        np.cos(theta_list) * np.sin(phi_list),
                        -np.sin(theta_list)),
                    axis=3),
                np.concatenate((
                        -np.sin(phi_list),
                        np.cos(phi_list),
                        np.zeros(phi_list.shape)),
                    axis=3)),
            axis=2)
    return np.matmul(T, vector_array)

def spherical_to_cartesian_vector(vector_array, coordinate_array, **kwargs):
    ''' coordinate transformations (from Antenna Theory Balanis 4ed, p. 1045)
    Args:
        vector_array
        coordinate_array
        **kwargs: Arbitrary keyword arguments
        Keywords
            coordinate_type (str): coordinate type (cartesian, cylindrical, spherical); [Default: None -> uses spherical coordinates])
    '''
    
    if vector_array.ndim == 1:
        vector_array = vector_array[np.newaxis,np.newaxis,:,np.newaxis]
    if coordinate_array.ndim == 1:
        coordinate_array = coordinate_array[np.newaxis,np.newaxis,:,np.newaxis]
        
    coordinate_type = kwargs.get('coordinate_type', None)
    
    if coordinate_type == 'cartesian':
        coordinate_array = cartesian_to_spherical_coordinates(coordinate_array)
        
    elif coordinate_type == 'cylindrical':
        coordinate_array = cylindrical_to_spherical_coordinates(coordinate_array)
    
    theta_list = coordinate_array[:,:,1,np.newaxis,:]
    phi_list = coordinate_array[:,:,2,np.newaxis,:]
    
    T = np.concatenate((
                np.concatenate((
                        np.sin(theta_list) * np.cos(phi_list),
                        np.cos(theta_list) * np.cos(phi_list),
                        -np.sin(phi_list)),
                    axis=3),
                np.concatenate((
                        np.sin(theta_list) * np.sin(phi_list),
                        np.cos(theta_list) * np.sin(phi_list),
                        np.cos(phi_list)),
                    axis=3),
                np.concatenate((
                        np.cos(theta_list),
                        -np.sin(theta_list),
                        np.zeros(phi_list.shape)),
                    axis=3)),
            axis=2)
    return np.matmul(T, vector_array)

def cylindrical_to_spherical_vector(vector_array, coordinate_array, **kwargs):
    if vector_array.ndim == 1:
        vector_array = vector_array[np.newaxis,np.newaxis,:,np.newaxis]
    if coordinate_array.ndim == 1:
        coordinate_array = coordinate_array[np.newaxis,np.newaxis,:,np.newaxis]
        
    coordinate_type = kwargs.get('coordinate_type', 'cartesian')
    
    if coordinate_type == 'cartesian':
        coordinate_array = cartesian_to_spherical_coordinates(coordinate_array)
        
    elif coordinate_type == 'cylindrical':
        coordinate_array = cylindrical_to_spherical_coordinates(coordinate_array)
    
    theta_list = coordinate_array[:,:,1,np.newaxis,:]
    
    T = np.concatenate((
                np.concatenate((
                        np.sin(theta_list),
                        np.zeros(theta_list.shape),
                        np.cos(theta_list)),
                    axis=3),
                np.concatenate((
                        np.cos(theta_list),
                        np.zeros(theta_list.shape),
                        -np.sin(theta_list)),
                    axis=3),
                np.concatenate((
                        np.zeros(theta_list.shape),
                        np.ones(theta_list.shape),
                        np.zeros(theta_list.shape)),
                    axis=3)),
            axis=2)
    return np.matmul(T, vector_array)

def spherical_to_cylindrical_vector(vector_array, coordinate_array, **kwargs):
    if vector_array.ndim == 1:
        vector_array = vector_array[np.newaxis,np.newaxis,:,np.newaxis]
    if coordinate_array.ndim == 1:
        coordinate_array = coordinate_array[np.newaxis,np.newaxis,:,np.newaxis]
        
    coordinate_type = kwargs.get('coordinate_type', 'cartesian')
    
    if coordinate_type == 'cartesian':
        coordinate_array = cartesian_to_spherical_coordinates(coordinate_array)
        
    elif coordinate_type == 'cylindrical':
        coordinate_array = cylindrical_to_spherical_coordinates(coordinate_array)
    
    theta_list = coordinate_array[:,:,1,np.newaxis,:]
    
    T = np.concatenate((
                np.concatenate((
                        np.sin(theta_list),
                        np.cos(theta_list),
                        np.zeros(theta_list.shape)),
                    axis=3),
                np.concatenate((
                        np.zeros(theta_list.shape),
                        np.zeros(theta_list.shape),
                        np.ones(theta_list.shape)),
                    axis=3),
                np.concatenate((
                        np.cos(theta_list),
                        -np.sin(theta_list),
                        np.zeros(theta_list.shape)),
                    axis=3)),
            axis=2)
    return np.matmul(T, vector_array)

def rotate_vector(vector_array, angle, rotation_axis):
    if vector_array.ndim == 1:
        vector_array = vector_array[np.newaxis,np.newaxis,:,np.newaxis]
        
    angle = np.radians(angle)
    
    axis_dictionary = {'x': np.array([1, 0, 0]), 'y': np.array([0, 1, 0]), 'z': np.array([0, 0, 1])}
    
    if isinstance(rotation_axis, str):
        if rotation_axis in ['x', 'y', 'z']:
            rotation_axis = axis_dictionary[rotation_axis][np.newaxis,np.newaxis,:,np.newaxis]
        
        else:
            raise Exception('Specify rotation axis as \'x\', \'y\', or \'z\', or supply arbitrary length (3,) vector.')
            
    else:
        if rotation_axis.ndim == 1:
            rotation_axis = rotation_axis[np.newaxis,np.newaxis,:,np.newaxis]
        
    out = (np.sum(rotation_axis * vector_array, axis=2, keepdims=True) * rotation_axis +
            np.cross(np.cross(rotation_axis, vector_array, axis=2), rotation_axis, axis=2) * np.cos(angle) +
            np.cross(rotation_axis, vector_array, axis=2) * np.sin(angle))
    return out