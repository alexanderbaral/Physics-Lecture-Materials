# -*- coding: utf-8 -*-
"""
@author: Alexander Baral
"""
# importing numpy
import numpy as np

vec1 = np.array([1, -2, 3])
vec2 = np.array([1, 2, 2])

def betrag(vec):
    abs_squared = np.sum([k**2 for k in vec])
    return np.sqrt(abs_squared)

def unitVec(vec):
    return vec / betrag(vec)

def zwischenWinkel(vec1, vec2):
    dummy = np.dot(vec1, vec2) / (betrag(vec1)*betrag(vec2))
    winkel_bogen = np.arccos( dummy )
    return np.rad2deg(winkel_bogen)

summeVec = vec1+vec2



print('AUSGABE:')
print('-----------')
print()
print('Kraft 1: ', vec1)
print('Betrag Kraft 1: ', betrag(vec1))
print()
print('Kraft 2: ', vec2)
print('Betrag Kraft 2: ', betrag(vec2))
print()
print('Gesamtkraft: ', summeVec)
print('Betrag Gesamtkraft: ', betrag(summeVec))
print()
print('Zwischenwinkel_Vec1_Vec2:', zwischenWinkel(vec1, vec2))
print('Zwischenwinkel_Gesamt_Vec1:', zwischenWinkel(summeVec, vec1))
print('Zwischenwinkel_Gesamt_Vec2:', zwischenWinkel(summeVec, vec2))
