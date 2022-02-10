# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 11:00:09 2021

@author: lab
"""

try:
    from IPython import get_ipython
    get_ipython().magic('clear')
    get_ipython().magic('reset -f')
except:
    pass


import numpy as np
from matplotlib import pyplot as plt
import scipy.constants

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

def near_field_propagate(J_e, J_m, r_prime, r):
    x_prime = np.unique(r_prime[:,0])
    y_prime = np.unique(r_prime[:,1])
    
    E_A = np.empty(r.shape, dtype=np.complex128)
    E_F = np.empty(r.shape, dtype=np.complex128)
    for i in range(r.shape[0]):
        R = r[i,:][None,:] - r_prime
        R_norm = np.linalg.norm(R, axis=1, keepdims=True)
        R_hat = R/R_norm
        
        G1 = -(1 + 1j*k*R_norm - k**2 * R_norm**2)/(R_norm**3)
        G2 = (3 + 3*1j*k*R_norm - k**2 * R_norm**2)/(R_norm**5)
        
        E_A_integrand = np.reshape((-1j*eta/(4*np.pi*k))
                               * (G1 * J_e + 
                                  G2 * R * np.sum(R * J_e, axis=1, keepdims=True))
                               * np.exp(-1j*k*R_norm), (x_prime.size, y_prime.size, 3))
        E_F_integrand = np.reshape((1/(4*np.pi)) 
                     * np.cross(R_hat, J_m, axisa=1, axisb=1, axisc=1)
                     * (1 + 1j*k*R_norm)/R_norm**2
                     * np.exp(-1j*k*R_norm), (x_prime.size, y_prime.size, 3))
        E_A[i,:] = np.trapz(np.trapz(E_A_integrand, x_prime, axis=0), y_prime, axis=0)
        E_F[i,:] = np.trapz(np.trapz(E_F_integrand, x_prime, axis=0), y_prime, axis=0)
    
    E = E_A + E_F
    return E


mm = .001
GHz = 1E9
c = scipy.constants.c
EPS_0 = scipy.constants.epsilon_0
MU_0  = scipy.constants.mu_0
eta = np.sqrt(MU_0/EPS_0)
f = 10*GHz
lam = c/f
k = 2*np.pi*f/c
a = 22.86*mm
b = 10.16*mm
beta = k*np.sqrt(1-(np.pi/(k*a))**2)

f_max = 12*GHz
lam_min = c/f_max


### Specify plane coordinates
Lx = 200*mm
Ly = 200*mm
delta_x = lam_min/2
delta_y = lam_min/2

x_probe = np.arange(-Lx/2, Lx/2, delta_x)
y_probe = np.arange(-Ly/2, Ly/2, delta_y)
z_probe = 0
X_probe, Y_probe = np.meshgrid(x_probe, y_probe, indexing='ij')

x_probe_prime1 = np.arange(-a/2, a/2, lam/5)
y_probe_prime1 = np.arange(-b/2, b/2, lam/5)
X_probe_prime1, Y_probe_prime1 = np.meshgrid(x_probe_prime1, y_probe_prime1, indexing='ij')
r_probe_prime1 = np.stack(
    (X_probe_prime1.reshape(-1),
     Y_probe_prime1.reshape(-1),
     z_probe*np.ones(X_probe_prime1.size)), 
    axis=1)
J_e_probe1 = (-1/eta * np.cos(np.pi*X_probe_prime1/a)).reshape(-1)
J_m_probe1 = (np.cos(np.pi*X_probe_prime1/a)).reshape(-1)

x_probe_prime2 = np.arange(-b/2, b/2, lam/5)
y_probe_prime2 = np.arange(-a/2, a/2, lam/5)
X_probe_prime2, Y_probe_prime2 = np.meshgrid(x_probe_prime2, y_probe_prime2, indexing='ij')
r_probe_prime2 = np.stack(
    (X_probe_prime2.reshape(-1),
     Y_probe_prime2.reshape(-1),
     z_probe*np.ones(X_probe_prime2.size)), 
    axis=1)
J_e_probe2 = (-1/eta * np.cos(np.pi*Y_probe_prime2/a)).reshape(-1)
J_m_probe2 = (np.cos(np.pi*Y_probe_prime2/a)).reshape(-1)

X = X_probe
Y = Y_probe
x = np.unique(X_probe)
y = np.unique(Y_probe)
z = 80*mm
r_vec = np.stack((X.reshape(-1), Y.reshape(-1), z*np.ones(X.reshape(-1).shape)), axis=1)

E_vec1 = np.empty((x_probe.size, y_probe.size, x.size, y.size, 2), dtype=np.complex128)
J_e1 = np.stack((np.zeros(J_e_probe1.shape), J_e_probe1, np.zeros(J_e_probe1.shape)), axis=1)
J_m1 = np.stack((J_m_probe1, np.zeros(J_m_probe1.shape), np.zeros(J_m_probe1.shape)), axis=1)
for i in range(x_probe.size):
    for j in range(y_probe.size):
        r_prime = r_probe_prime1 - np.array([x_probe[i], y_probe[j], 0])[None,:]
        E_vec1[i,j,:,:,:] = near_field_propagate(J_e1, J_m1, r_prime, r_vec)[:,:2].reshape((x.size, y.size, 2))
        
E_vec2 = np.empty((x_probe.size, y_probe.size, x.size, y.size, 2), dtype=np.complex128)
J_e2 = np.stack((J_e_probe2, np.zeros(J_e_probe2.shape), np.zeros(J_e_probe2.shape)), axis=1)
J_m2 = np.stack((np.zeros(J_m_probe2.shape), -J_m_probe2, np.zeros(J_m_probe2.shape)), axis=1)
for i in range(x_probe.size):
    for j in range(y_probe.size):
        r_prime = r_probe_prime2 - np.array([x_probe[i], y_probe[j], 0])[None,:]
        E_vec2[i,j,:,:,:] = near_field_propagate(J_e2, J_m2, r_prime, r_vec)[:,:2].reshape((x.size, y.size, 2))
        
plt.imshow(np.abs(E_vec2[10,10,:,:,0]), extent=(x.min(), x.max(), y.min(), y.max()))

A_mat = np.concatenate((np.reshape(E_vec1, (x_probe.size*y_probe.size, x.size*y.size, 2)),
                        np.reshape(E_vec2, (x_probe.size*y_probe.size, x.size*y.size, 2))),
                        axis=0)
A_mat = np.concatenate((A_mat[:,:,0], A_mat[:,:,1]), axis=1)

#%%
N = x.size*y.size
fig = plt.figure(figsize=(5,5))
plt.imshow(np.real(np.reshape(A_mat[433,N:], (x.size, y.size))))



