# -*- coding: utf-8 -*-
"""
@author: Alexander Baral
"""
# importing numpy
import numpy as np

vec_r = np.array([2,3,-1])
vec_v = np.array([1,0,3])
masse = 10

vec_p = masse * vec_v


winkel_rp_bogen = np.arccos(np.clip(np.dot(vec_r, vec_p) / (np.linalg.norm(vec_r) * np.linalg.norm(vec_p)), -1.0, 1.0))
winkel_rp_grad = winkel_rp_bogen*360.0/(2.*np.pi)

print('Der Winkel zwischen r und v ist ', np.round(winkel_rp_grad,2), '°.')

vec_L =  np.cross(vec_r, vec_p)
betrag_L = np.linalg.norm(vec_L)

print('Der Drehimpulsvektor L ergibt sich zu: ', vec_L, 'Nms, mit einem Betrag von ', np.round(betrag_L,2),'Nms.')

check_skalarprod_Lr = np.dot(vec_L, vec_r)
check_skalarprod_Lp = np.dot(vec_L, vec_p)

if (check_skalarprod_Lp==0 and check_skalarprod_Lr==0):
    print('Der Drehimpulsvektor steht senkrecht auf Impuls p und Ortsvektor r.')
