# -*- coding: utf-8 -*-
"""
@author: Alexander Baral
"""
# importing numpy
import numpy as np
import matplotlib.pyplot as plt

time_min = 0.0
time_max = 10.0

def distance(time):
    distance = 5 * time**2
    return distance

def velocity(time, eps = 1.0e-5):
    return (distance(time+eps)-distance(time-eps))/(2.0*eps)

def beschleunigung(time, eps = 1.0e-5):
    return (velocity(time+eps)-velocity(time-eps))/(2.0*eps)

# PLOTTING
time_Grid = np.linspace(start=time_min, stop=time_max, num=100, endpoint=True)

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(6, 6))


ax1.ticklabel_format(useOffset=False, axis='both')
ax2.ticklabel_format(useOffset=False, axis='both')
ax3.ticklabel_format(useOffset=False, axis='both')

color1 = 'black'
color2 = 'blue'
color3 = 'green'

# PLOT erstellen
ax1.plot(time_Grid, distance(time_Grid), label='Ort', color=color1, linewidth=2)
ax2.plot(time_Grid, velocity(time_Grid), label='Geschwindigkeit', color=color2, linewidth=2)
ax3.plot(time_Grid, beschleunigung(time_Grid), label='Beschleunigung', color=color3, linewidth=2)

# Achsenbeschriftung
ax1.set_xlabel(r'$t$ in s'); ax1.set_ylabel(r'$x$ in m')
ax2.set_xlabel(r'$t$ in s'); ax2.set_ylabel(r'$v$ in m/s')
ax3.set_xlabel(r'$t$ in s'); ax3.set_ylabel(r'$a$ in m/s²')

# Grid
ax1.grid()
ax2.grid()
ax3.grid()

ax1.legend(loc=1)
ax2.legend(loc=1)
ax3.legend(loc=1)

plt.tight_layout()
plt.show()
