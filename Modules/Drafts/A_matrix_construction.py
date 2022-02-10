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

mm = .001
GHz = 1E9
c = scipy.constants.c
f = 10*GHz
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

X = X_probe
Y = Y_probe
x = np.unique(X_probe)
y = np.unique(Y_probe)
z = 80*mm

E_vec1 = np.empty((x_probe.size, y_probe.size, x.size, y.size, 2), dtype=np.complex128)
for i in range(x_probe.size):
    for j in range(y_probe.size):
        
        ## defining spherical coordinates over plane, for gain pattern calculation
        r = np.sqrt((X - X_probe[i,j])**2 + (Y - Y_probe[i,j])**2 + (z - z_probe)**2)
        theta = np.arccos(z/np.sqrt((X - X_probe[i,j])**2 + (Y - Y_probe[i,j])**2 + (z - z_probe)**2))
        phi = np.arctan2(Y - Y_probe[i,j], X - X_probe[i,j])
        
        Ee = ( ((1+beta/k*np.cos(theta))/(1+beta/k)) *
              (np.sin(k*b/2 * np.sin(theta))/((k*b/2)*np.sin(theta))) )
        Eh = ( (np.pi/2)**2 * np.cos(theta) 
              * np.cos(k*a/2 * np.sin(theta))/((np.pi/2)**2 - (k*a/2*np.sin(theta))**2) )
        
        ## removing nan at probe position, replacing with max value 
        ## (sort gives nan as max value, taking next highest)
        Ee = np.nan_to_num(Ee, nan=np.sort(Ee.reshape(-1))[-2])
        Eh = np.nan_to_num(Eh, nan=np.sort(Eh.reshape(-1))[-2])
        
        E_theta = np.exp(1j*k*r)/(k*r) * Ee * np.sin(phi)
        E_phi = np.exp(1j*k*r)/(k*r) * Eh * np.cos(phi)
        # E_phi = np.exp(1j*k*r)/(k*r) * Ee * np.sin(phi)
        # E_theta = np.exp(1j*k*r)/(k*r) * Eh * np.cos(phi)

        E_vec_spherical = np.stack(
            (np.zeros(E_theta.shape),
             E_theta,
             E_phi), axis=2).reshape((-1, 3))
        
        ## convert spherical vector components to cartesian
        E_vec_cartesian = spherical_to_cartesian_vector(E_vec_spherical,
                                                        theta.reshape(-1),
                                                        phi.reshape(-1))
        
        E_vec1[i,j,:,:,:] = E_vec_cartesian[:,:2].reshape((X.shape[0], Y.shape[1], 2))

plt.imshow(np.real(E_vec1[7,7,:,:,0]))

E_vec2 = np.empty(E_vec1.shape, dtype=np.complex128)
E_vec2[:,:,:,:,0] = E_vec1[:,:,:,:,1]
E_vec2[:,:,:,:,1] = E_vec1[:,:,:,:,0]
#%%
fig, (ax1, ax2) = plt.subplots(1,2, figsize=(10,5))
im1 = ax1.imshow(np.real(E_vec1[int(np.floor(E_vec1.shape[0]/2)), int(np.floor(E_vec1.shape[1]/2)),:,:,0]),
                 extent=(np.min(X), np.max(X), np.min(Y), np.max(Y)))
fig.colorbar(im1, ax=ax1)
ax1.set_xlabel('x (m)')
ax1.set_ylabel('y (m)')
im2 = ax2.imshow(np.real(E_vec1[int(np.floor(E_vec1.shape[0]/2)), int(np.floor(E_vec1.shape[1]/2)),:,:,1]),
                 extent=(np.min(X), np.max(X), np.min(Y), np.max(Y)))
fig.colorbar(im2, ax=ax2)
ax2.set_xlabel('x (m)')
ax2.set_ylabel('y (m)')
plt.tight_layout()

x_indx = 5
y_indx = 15
fig, (ax1, ax2) = plt.subplots(1,2, figsize=(10,5))
im1 = ax1.imshow(np.real(E_vec1[x_indx, y_indx,:,:,1]),
                 extent=(np.min(X), np.max(X), np.min(Y), np.max(Y)))
fig.colorbar(im1, ax=ax1)
ax1.set_xlabel('x (m)')
ax1.set_ylabel('y (m)')
im2 = ax2.imshow(np.real(E_vec2[x_indx, y_indx,:,:,1]),
                 extent=(np.min(X), np.max(X), np.min(Y), np.max(Y)))
fig.colorbar(im2, ax=ax2)
ax2.set_xlabel('x (m)')
ax2.set_ylabel('y (m)')
plt.tight_layout()

test = np.reshape(E_vec1, (x_probe.size*y_probe.size, x.size*y.size, 2))
A_mat = np.concatenate((np.reshape(E_vec1, (x_probe.size*y_probe.size, x.size*y.size, 2)),
                        np.reshape(E_vec2, (x_probe.size*y_probe.size, x.size*y.size, 2))),
                       axis=0)
A_mat = np.concatenate((A_mat[:,:,0], A_mat[:,:,1]), axis=1)

N = x.size*y.size
fig = plt.figure(figsize=(5,5))
plt.imshow(np.real(np.reshape(A_mat[433,N:], (x.size, y.size))))



