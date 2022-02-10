import numpy as np
import scipy.constants

C = scipy.constants.c

def spherical_to_cartesian_vector(vec, theta_list, phi_list):
    # vec n X 3, theta_list n X 1, phi_list n X 1
    if np.isscalar(theta_list):
        n = 1
    else:
        n = phi_list.size
    T = np.reshape(np.column_stack((
        np.sin(theta_list)*np.cos(phi_list), 
        np.cos(theta_list)*np.cos(phi_list),
        -np.sin(phi_list),
        np.sin(theta_list)*np.sin(phi_list),
        np.cos(theta_list)*np.sin(phi_list),
        np.cos(phi_list),
        np.cos(theta_list),
        -np.sin(theta_list),
        np.zeros(n))),
              (n, 3, 3))
    return np.matmul(T, vec[:,:,None])[:,:,0]

def prop_from_magnetic_currents(K_m, r_vec, k, N_theta, N_phi):
    x = np.unique(r_vec[:,0])
    y = np.unique(r_vec[:,1])
    
    K_m_array = np.reshape(K_m, (x.size, y.size, 3))
    Theta_far, Phi_far = np.meshgrid(
        np.linspace(0, np.pi/2, N_theta),
        np.linspace(0, 2*np.pi, N_phi),
        indexing='ij')    
    theta_list = Theta_far.reshape(-1)
    phi_list = Phi_far.reshape(-1)
    
    r_hat = spherical_to_cartesian_vector(np.transpose(np.array([1, 0, 0])[:,None]),
                                         Theta_far.reshape(-1), 
                                         Phi_far.reshape(-1))
    k_far_vec = k * r_hat
    
    L_theta = np.empty((Theta_far.size), dtype=np.complex64)
    L_phi = np.empty((Theta_far.size), dtype=np.complex64)
    for i in range(Theta_far.size):
        integrand_theta = ((K_m_array[:,:,0]*np.cos(theta_list[i])*np.cos(phi_list[i]) + 
                           K_m_array[:,:,1]*np.cos(theta_list[i])*np.sin(phi_list[i]) -
                           K_m_array[:,:,2]*np.sin(theta_list[i])) *
                           np.reshape(np.exp(1j*np.sum(k_far_vec[i] * r_vec, 1)), (x.size, y.size)))
        integrand_phi = ((-K_m_array[:,:,0]*np.sin(phi_list[i]) + 
                           K_m_array[:,:,1]*np.cos(phi_list[i])) *
                           np.reshape(np.exp(1j*np.sum(k_far_vec[i] * r_vec, 1)), (x.size, y.size)))

        L_theta[i] = np.trapz(np.trapz(integrand_theta, x, axis=0), y, axis=0)
        L_phi[i] = np.trapz(np.trapz(integrand_phi, x, axis=0), y, axis=0)
        
    E = np.transpose(np.array([
        np.zeros(L_theta.shape), -L_phi, L_theta]))

    E = np.reshape(E, (N_theta, N_phi, 3))
        
    return Theta_far, Phi_far, E

def fft_prop_from_magnetic_currents(K_m, r_vec, k, N):
    x = np.unique(r_vec[:,0])
    y = np.unique(r_vec[:,1])
    
    K_m_reshape = np.transpose(np.reshape(K_m, (y.size, x.size, 3)), (1, 0, 2))
    K_m_pad = np.pad(K_m_reshape, ((N, N), (N, N), (0, 0)), 'constant')

    K_m_ft = np.fft.fftshift(np.fft.ifftn(np.fft.ifftshift(
            K_m_pad, axes=(0,1)), s=None, axes=(0,1)), axes=(0,1))
    delta_x = np.abs(x[1]-x[0])
    delta_y = np.abs(y[1]-y[0])
    kx = np.linspace(-np.pi/delta_x, np.pi/delta_x, K_m_ft.shape[0]).astype(np.complex64)
    ky = np.linspace(-np.pi/delta_y, np.pi/delta_y, K_m_ft.shape[1]).astype(np.complex64)
    kx_nonzeros = np.where(np.abs(kx)<k)
    ky_nonzeros = np.where(np.abs(ky)<k)
    Kx_nonzeros, Ky_nonzeros = np.meshgrid(kx_nonzeros, ky_nonzeros, indexing='ij')
    kx = kx[kx_nonzeros]
    ky = ky[ky_nonzeros]
    Kx, Ky = np.meshgrid(kx, ky, indexing='ij')
    Kz = np.sqrt(k**2 - Kx**2 - Ky**2)

    Theta_prop = np.arccos(np.real(Kz)/k)
    Phi_prop = np.arctan2(np.real(Ky), np.real(Kx))

    f_phi = ( np.cos(Theta_prop) * np.cos(Phi_prop) * K_m_ft[Kx_nonzeros,Ky_nonzeros,0] + 
             np.cos(Theta_prop) * np.sin(Phi_prop) * K_m_ft[Kx_nonzeros, Ky_nonzeros,1] )
    f_theta = ( -np.sin(Phi_prop) * K_m_ft[Kx_nonzeros, Ky_nonzeros,0] + 
               np.cos(Phi_prop) * K_m_ft[Kx_nonzeros, Ky_nonzeros,1] )

    E = np.transpose(np.array([
        np.reshape(np.zeros(f_theta.shape), -1), np.reshape(-f_phi, -1), np.reshape(f_theta, -1)]))

    return Theta_prop, Phi_prop, E

def propagate_from_scans(measurements, f, X, Y, N_theta, N_phi):
    # measurements is Nx x Ny x 2 array
    n_hat = np.transpose(np.array([0, 0, 1])[:,None])       # specify antenna orientation
    E = np.reshape(measurements, (measurements.shape[0]*measurements.shape[1], 2))     # stack NFS data into E-field vector
    X = X.reshape(-1)
    Y = Y.reshape(-1)

    r_vec = np.stack((X, Y, np.zeros(X.shape)), axis=1)
    E = np.stack((E[:,0], E[:,1], np.zeros((E.shape[0]), dtype=np.complex128)), axis=1)

    K_m = -np.cross(n_hat, E, axisa=1, axisb=1, axisc=1)     # define magnetic current from surface equivalence relationship
    Theta_far, Phi_far, E = prop_from_magnetic_currents(K_m, r_vec, 2*np.pi*f/C, N_theta, N_phi)   # propagate magnetic surface currents to far field

    return Theta_far, Phi_far, E