# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 20:59:33 2021

@author: Aaron
"""

import numpy as np
import scipy.constants

mm = .001
GHz = 1E9
c = scipy.constants.c

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

def make_A_mat(f, a, b, x_probe, y_probe, z_offset):
    k = 2*np.pi*f/c
    beta = k*np.sqrt(1-(np.pi/(k*a))**2)
    
    X_probe, Y_probe = np.meshgrid(x_probe, y_probe, indexing='ij')
    
    X = X_probe
    Y = Y_probe
    x = np.unique(X_probe)
    y = np.unique(Y_probe)
    
    E_vertical = np.empty((x_probe.size, y_probe.size, x.size, y.size, 2), dtype=np.complex128)
    
    for i in range(x_probe.size):
        for j in range(y_probe.size):
            
            ## defining spherical coordinates over plane, for gain pattern calculation
            r = np.sqrt((X - X_probe[i,j])**2 + (Y - Y_probe[i,j])**2 + z_offset**2)
            theta = np.arccos(z_offset/np.sqrt((X - X_probe[i,j])**2 + (Y - Y_probe[i,j])**2 + (z_offset)**2))
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
    
            E_vec_spherical = np.stack(
                (np.zeros(E_theta.shape),
                 E_theta,
                 E_phi), axis=2).reshape((-1, 3))
            
            ## convert spherical vector components to cartesian
            E_vec_cartesian = spherical_to_cartesian_vector(E_vec_spherical,
                                                            theta.reshape(-1),
                                                            phi.reshape(-1))
            
            E_vertical[i,j,:,:,:] = E_vec_cartesian[:,:2].reshape((X.shape[0], Y.shape[1], 2))

    # e-field components for horizontal orientation obtained by swapping vertical orientation components
    E_horizontal = np.empty(E_vertical.shape, dtype=np.complex128)
    E_horizontal[:,:,:,:,0] = E_vertical[:,:,:,:,1]
    E_horizontal[:,:,:,:,1] = E_vertical[:,:,:,:,0]
    
    A_mat = np.concatenate((np.reshape(E_vertical, (x_probe.size*y_probe.size, x.size*y.size, 2)),
                        np.reshape(E_horizontal, (x_probe.size*y_probe.size, x.size*y.size, 2))),
                       axis=0)
    A_mat = np.concatenate((A_mat[:,:,0], A_mat[:,:,1]), axis=1)
    return A_mat

def probe_deconvolve(measurements, A_mat, x_probe, y_probe):
    ## measurements: Nx x Ny x 2 array
    ## size 2 dimension corresponds to vertical-horizontal probe orientation
    
    g = measurements.reshape((x_probe.size*y_probe.size*2, 1))
    E_solution = np.matmul(np.linalg.inv(A_mat), g)
    
    return E_solution.reshape((x_probe.size, y_probe.size, 2))
    
    
    
    
    
    
    
    