# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 11:38:00 2020

@author: avd13
"""

import numpy as np
from scipy import special as sp

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

def cartesian_to_spherical_vector(vec, theta_list, phi_list):
    # vec n X 3, theta_list n X 1, phi_list n X 1
    if np.isscalar(theta_list):
        n = 1
    else:
        n = phi_list.size
    T = np.reshape(np.column_stack((
        np.sin(theta_list)*np.cos(phi_list), 
        np.sin(theta_list)*np.sin(phi_list),
        np.cos(theta_list),
        np.cos(theta_list)*np.cos(phi_list),
        np.cos(theta_list)*np.sin(phi_list),
        -np.sin(theta_list),
        -np.sin(phi_list),
        np.cos(phi_list),
        np.zeros(n))),
              (n, 3, 3))
    return np.matmul(T, vec[:,:,None])[:,:,0]

def cylindrical_to_cartesian_vector(vec, phi_list):
    # vec n X 3, phi_list n X 1
    if np.isscalar(phi_list):
        n = 1
    else:
        n = phi_list.size
    T = np.reshape(np.column_stack((
        np.cos(phi_list),
        -np.sin(phi_list),
        np.zeros(n),
        np.sin(phi_list),
        np.cos(phi_list),
        np.zeros(n),
        np.zeros(n),
        np.zeros(n),
        np.ones(n))),
              (n, 3, 3))
    out_temp = np.matmul(T, vec[:,:,None])[:,:,0]
    return np.transpose(np.array([out_temp[:,0], out_temp[:,1], out_temp[:,2]]))

def cartesian_to_cylindrical_vector(vec, phi_list):
    # vec n X 3, phi_list n X 1
    if np.isscalar(phi_list):
        n = 1
    else:
        n = phi_list.size
    
    vec_reshape = np.transpose(np.array([vec[:,0], vec[:,1], vec[:,2]]))
    T = np.reshape(np.column_stack((
        np.cos(phi_list),
        np.sin(phi_list),
        np.zeros(n),
        -np.sin(phi_list),
        np.cos(phi_list),
        np.zeros(n),
        np.zeros(n),
        np.zeros(n),
        np.ones(n))),
              (n, 3, 3))
    return np.matmul(T, vec_reshape[:,:,None])[:,:,0]

def cartesian_to_circular_vector(vec):
    # vec n X 3
    vec_reshape = np.transpose(np.array([vec[:,0], vec[:,2]]))
    T_circular = np.array([[1/np.sqrt(2), -1j/np.sqrt(2)], [1/np.sqrt(2), 1j/np.sqrt(2)]])
    return np.matmul(T_circular[None,:,:], vec_reshape[:,:,None])[:,:,0]

def spherical_to_circular_vector(vec):
    # vec n X 3
    vec_reshape = np.transpose(np.array([vec[:,1], vec[:,2]]))
    T_circular = np.array([[1/np.sqrt(2), -1j/np.sqrt(2)], [1/np.sqrt(2), 1j/np.sqrt(2)]])
    return np.matmul(T_circular[None,:,:], vec_reshape[:,:,None])[:,:,0]
    
def euclidean_map(alpha, alpha_dict, f_indx):
    Alpha_true, Alpha_lorentz = np.meshgrid(alpha, alpha_dict[:,f_indx], indexing='ij')
    dist = np.sqrt((np.real(Alpha_true)-np.real(Alpha_lorentz))**2 + (np.imag(Alpha_true)-np.imag(Alpha_lorentz))**2)
    indx = np.argmin(dist, axis=1)
    return indx

def lorentzian_map(alpha):
    return (-1j + np.exp(-1j*np.angle(alpha)))/2

def compute_polarizabilities_beam(r_i, H_f, k_b_out, nu, mu, n, E_out, element_spacing, k, alpha_dict, f_indx):
    mu0 = 4*np.pi*10**-7
    eps0 = 8.85*10**-12
    Z0 = np.sqrt(mu0/eps0)
    
    exp_term = np.exp(-1j*np.sum(k_b_out * r_i, 1))
    
    H_dot_nu = np.sum(H_f * nu, 1)
    H_dot_mu = np.sum(H_f * mu, 1)
    
    n_cross_nu = np.cross(n, nu)
    n_cross_mu = np.cross(n, mu)
    
    E0_dot_n_cross_nu = np.sum(E_out * n_cross_nu, 1)
    E0_dot_n_cross_mu = np.sum(E_out * n_cross_mu, 1)
    
    alpha_1_true = np.nan_to_num(((1j*element_spacing**2)/(Z0*k)) * E0_dot_n_cross_nu * exp_term / H_dot_nu)
    alpha_2_true = np.nan_to_num(((1j*element_spacing**2)/(Z0*k)) * E0_dot_n_cross_mu * exp_term / H_dot_mu)
    
    alpha_dict_norm = alpha_dict * 1.0 * np.amax(np.abs(alpha_1_true))/np.amax(np.abs(alpha_dict))
    
    alpha_1_true = alpha_1_true.astype(np.complex64)
    alpha_2_true = alpha_2_true.astype(np.complex64)
    alpha_dict_norm = alpha_dict_norm.astype(np.complex64)

    indx_1 = euclidean_map(alpha_1_true, alpha_dict_norm, f_indx)
    indx_2 = euclidean_map(alpha_2_true, alpha_dict_norm, f_indx)
    
    return alpha_1_true, alpha_2_true, alpha_dict_norm, indx_1, indx_2

def compute_polarizabilities_beam_mean(r_i, H_f, k_b_out, nu, mu, n, E_out, element_spacing, k, alpha_dict, f_indx):
    mu0 = 4*np.pi*10**-7
    eps0 = 8.85*10**-12
    Z0 = np.sqrt(mu0/eps0)
    
    exp_term = np.exp(-1j*np.sum(k_b_out * r_i, 1))
    
    H_dot_nu = np.sum(H_f * nu, 1)
    H_dot_mu = np.sum(H_f * mu, 1)
    
    n_cross_nu = np.cross(n, nu)
    n_cross_mu = np.cross(n, mu)
    
    E0_dot_n_cross_nu = np.sum(E_out * n_cross_nu, 1)
    E0_dot_n_cross_mu = np.sum(E_out * n_cross_mu, 1)
    
    alpha_1_true = np.nan_to_num(((1j*element_spacing**2)/(Z0*k)) * E0_dot_n_cross_nu * exp_term / H_dot_nu)
    alpha_2_true = np.nan_to_num(((1j*element_spacing**2)/(Z0*k)) * E0_dot_n_cross_mu * exp_term / H_dot_mu)
    
    alpha_dict_norm = alpha_dict * np.mean(np.abs(alpha_1_true))/np.amax(np.abs(alpha_dict))
    
    alpha_1_true = alpha_1_true.astype(np.complex64)
    alpha_2_true = alpha_2_true.astype(np.complex64)
    alpha_dict_norm = alpha_dict_norm.astype(np.complex64)

    indx_1 = euclidean_map(alpha_1_true, alpha_dict_norm, f_indx)
    indx_2 = euclidean_map(alpha_2_true, alpha_dict_norm, f_indx)
    
    return alpha_1_true, alpha_2_true, alpha_dict_norm, indx_1, indx_2

def make_surface_currents(f, f_indx, nu, mu, alpha_type, alpha_1_true, alpha_2_true, alpha_dict,
                          indx_1, indx_2, element_spacing, H_f, theta_b, phi_b, r_i, E_0):
    # alpha_type 0 for true, 1 for euclidean estimate, 2 for lorentzian
    mu0 = 4*np.pi*10**-7
    
    nu_tensor = np.matmul(nu[:,:,None], np.transpose(nu[:,:,None], (0,2,1)))
    mu_tensor = np.matmul(mu[:,:,None], np.transpose(mu[:,:,None], (0,2,1)))
    
    if alpha_type==0:
        Chi_tensor = ( 
            (alpha_1_true/(element_spacing**2))[:,None,None]*nu_tensor + 
            (alpha_2_true/(element_spacing**2))[:,None,None]*mu_tensor
                            )
    elif alpha_type==1:
        Chi_tensor = ( 
            (alpha_dict[indx_1, f_indx]/(element_spacing**2))[:,None,None]*nu_tensor + 
            (alpha_dict[indx_2, f_indx]/(element_spacing**2))[:,None,None]*mu_tensor
                            )
    elif alpha_type==2:
        Chi_tensor = (
            (((-1j + np.exp(1j*np.angle(alpha_1_true)))/2)/(element_spacing**2))[:,None,None]*nu_tensor +
            (((-1j + np.exp(1j*np.angle(alpha_2_true)))/2)/(element_spacing**2))[:,None,None]*mu_tensor
            )
        
    elif alpha_type==3:
        phase_term1 = np.angle(alpha_1_true)/2
        phase_term2 = np.angle(alpha_2_true)/2
        Chi_tensor = (
            ((np.sin(phase_term1)*(np.exp(1j*phase_term1)))/(element_spacing**2))[:,None,None]*nu_tensor +
            ((np.sin(phase_term2)*(np.exp(1j*phase_term2)))/(element_spacing**2))[:,None,None]*mu_tensor
            )
        
    elif alpha_type==4:
        k = 2*np.pi*f/(3E8)
        k_b_spherical = np.transpose(np.array([k, 0, 0])[:,None])
        k_b = spherical_to_cartesian_vector(k_b_spherical, theta_b, phi_b)
        exp_term = np.exp(-1j*np.sum(k_b * r_i, 1))
        theta_k = np.transpose(np.array([0, 1, 0])[:,None])
        phi_k = np.transpose(np.array([0, 0, 1])[:,None])
        theta_k_cartesian = spherical_to_cartesian_vector(theta_k, theta_b, phi_b)
        phi_k_cartesian = spherical_to_cartesian_vector(phi_k, theta_b, phi_b)
        
        pol_mat = np.transpose(np.array([[
            np.sum(np.matmul(nu_tensor, H_f[:,:,None]) * theta_k_cartesian[:,:,None], axis=1), 
            np.sum(np.matmul(mu_tensor, H_f[:,:,None]) * theta_k_cartesian[:,:,None], axis=1)],
            [np.sum(np.matmul(nu_tensor, H_f[:,:,None]) * phi_k_cartesian[:,:,None], axis=1),
            np.sum(np.matmul(mu_tensor, H_f[:,:,None]) * phi_k_cartesian[:,:,None], axis=1)
                    ]]), (2, 0, 1, 3))[:,:,:,0]

        r_k = np.transpose(np.array([1, 0, 0])[:,None])
        pol_vec = np.cross(r_k, E_0)[:,1:]
        
        psi_vec = np.matmul(
            np.linalg.inv(pol_mat),
            (1j*2*element_spacing**2) * exp_term[:,None,None] * pol_vec[:,:,None]
                        )

        psi_1 = np.real(-np.log(1 - psi_vec[:,0,0])/2j)
        psi_2 = np.real(-np.log(1 - psi_vec[:,1,0])/2j)
        #psi_1 = (-np.angle(1 - psi_vec[:,0,0])/2).astype(np.complex64)
        #psi_2 = (-np.angle(1 - psi_vec[:,1,0])/2).astype(np.complex64)
        #psi_1 = np.angle(psi_vec[:,0,0])/2
        #psi_2 = np.angle(psi_vec[:,1,0])/2
        
        alpha_1 = np.sin(psi_1) * np.exp(1j*psi_1)
        alpha_2 = np.sin(psi_2) * np.exp(1j*psi_2)

        Chi_tensor = ( 
            (alpha_1/(element_spacing**2))[:,None,None]*nu_tensor + 
            (alpha_2/(element_spacing**2))[:,None,None]*mu_tensor
                            )
        
    K_m = -1j*2*np.pi*f*mu0 * np.matmul(Chi_tensor, H_f[:,:,None])[:,:,0]
    
    return K_m #, alpha_1, alpha_2

def near_field_propagate_magnetic_dipoles(r_in, r_out, k, K_m):
    
    mu0 = 4*np.pi*10**-7
    eps0 = 8.85*10**-12
    Z0 = np.sqrt(mu0/eps0)

    H = np.zeros((r_out.shape[0], 3), dtype=np.complex64)
    
    for i in range(r_in.shape[0]):
        R = r_out - np.transpose(r_in[i,:][:,None])
        R_mag = np.sqrt(np.sum(R**2, 1, keepdims=True))
        
        G1 = (-1 - 1j*k*R_mag + k**2*R_mag**2)/R_mag**3
        G2 = (3 + 1j*3*k*R_mag - k**2*R_mag**2)/R_mag**5
        
        temp_term = np.sum(R*np.transpose(K_m[i,:][:,None]), 1, keepdims=True) * G2 * np.exp(-1j*k*R_mag)
        
        H_temp = ( (-1j)/(4*np.pi*k*Z0) * (np.transpose(K_m[i,:][:,None])*G1*np.exp(-1j*k*R_mag)) +
                                               R*temp_term )
        H = H + H_temp
    
    return H

def compute_FF_from_magnetic_currents(r_i, K_m, k, N):
    
    Theta_far, Phi_far = np.meshgrid(
        np.arange(0, np.pi/2, np.pi/N),
        np.arange(0, 2*np.pi, np.pi/N),
        indexing='ij')
    
    R_far = np.ones(Theta_far.shape)
    r_far = np.transpose(np.array([np.reshape(R_far, -1), np.reshape(Theta_far, -1), np.reshape(Phi_far, -1)]))
    r_far_cartesian = np.transpose(np.array([
        r_far[:,0]*np.sin(r_far[:,1])*np.cos(r_far[:,2]),
        r_far[:,0]*np.sin(r_far[:,1])*np.sin(r_far[:,2]),
        r_far[:,0]*np.cos(r_far[:,1])
            ]))
    r_far_cartesian = r_far_cartesian/np.sqrt(np.sum(r_far_cartesian**2, axis=1, keepdims=True))
    
    L_theta = np.sum( ( K_m[:,0][:,None] * np.transpose((np.cos(r_far[:,1])*np.cos(r_far[:,2]))[:,None]) + 
                        K_m[:,1][:,None] * np.transpose((np.cos(r_far[:,1])*np.sin(r_far[:,2]))[:,None]) -
                        K_m[:,2][:,None] * np.transpose((np.sin(r_far[:,1]))[:,None]) ) *
           np.exp(+1j*k*np.sum(np.transpose(r_far_cartesian[:,:,None], (2,0,1))*np.transpose(r_i[:,:,None],(0,2,1)), 2)),
                0)
    L_phi = np.sum( ( -K_m[:,0][:,None] * np.transpose((np.sin(r_far[:,2]))[:,None]) + 
                       K_m[:,1][:,None] * np.transpose((np.cos(r_far[:,2]))[:,None]) ) *
                   np.exp(+1j*k*np.sum(np.transpose(r_far_cartesian[:,:,None], (2,0,1))*np.transpose(r_i[:,:,None],(0,2,1)), 2)),
                        0)
    return np.transpose(np.array([np.zeros(L_phi.shape), L_theta, L_phi]))

def fft_prop_from_magnetic_currents(K_m, x, y, k, N):
    K_m_reshape = np.reshape(K_m, (x.size, y.size, 3))
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

    H = np.transpose(np.array([
        np.reshape(np.zeros(f_theta.shape), -1), np.reshape(f_theta, -1), np.reshape(f_phi, -1)]))

    return Theta_prop, Phi_prop, H
    
    
    
    