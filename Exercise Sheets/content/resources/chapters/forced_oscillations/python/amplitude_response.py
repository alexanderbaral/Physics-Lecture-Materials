import numpy as np
import matplotlib.pyplot as plt

# Parameter in SI-Einheiten
omega_0 = 2.0
delta = 0.2
force_amplitude = 1.0
mass = 1.0

omega = np.linspace(0.0, 5.0, 501)
drive = force_amplitude / mass
amplitude = drive / np.sqrt((omega_0**2 - omega**2)**2 + (2 * delta * omega)**2)
static_amplitude = drive / omega_0**2

fig, ax = plt.subplots()
ax.plot(omega, amplitude, color="tab:blue", label="Amplitudengang")
ax.axhline(static_amplitude, color="0.35", linestyle=":", label="statische Auslenkung")
if 0 < delta < omega_0 / np.sqrt(2):
    resonance = np.sqrt(omega_0**2 - 2 * delta**2)
    maximum = drive / (2 * delta * np.sqrt(omega_0**2 - delta**2))
    ax.axvline(resonance, color="0.45", linestyle="--", label="Resonanzkreisfrequenz")
    ax.axhline(maximum, color="0.35", linestyle=":", label="Resonanzamplitude")

ax.set(xlabel=r"Erregerkreisfrequenz $\Omega$ (1/s)", ylabel="Amplitude (m)", xlim=(0, 5))
ax.legend()
fig.tight_layout()
plt.show()
