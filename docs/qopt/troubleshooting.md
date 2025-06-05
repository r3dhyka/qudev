# Quantum Optics Laboratory

Documentation of miscellaneous know-how and troubleshooting in Quantum Optics Lab.

## Troubleshooting
:material-tag-outline:{ title="Minimum version" } [1.2.0](../changelog/index.md) 

Symbol:<br>
⚠️ = Warning/Cautious!<br>
🔥 = Cautious for burning risk / hot surface

### Power Cable Extension

Do not use a long extension cable to power an equipment otherwise you will get spurious signals like the one shown in Fig. 1. The extension cable can act as an antenna and may pick up unwanted signals along the way.

<figure markdown="span">
    ![spurious signal](https://raw.githubusercontent.com/r3dhyka/qudev/refs/heads/main/docs/assets/spurious_signal.png){ width="400" }
    <figcaption>Figure 1. ~ 1 MHz spurious signal from a Si Photodetector</figcaption>
</figure>

### Power Line Frequency Noise

50 Hz noise from the power line is still creeping in as displayed in Fig. 2, and needs an iso-transformer to tame the noise. Luckily, no 100, 150 Hz harmonics were detected.

<figure markdown="span">
    ![line freq](https://raw.githubusercontent.com/r3dhyka/qudev/refs/heads/main/docs/assets/powerline_noise.png){ width="400" }
    <figcaption>Figure 2. Noise spectrum from open probe oscilloscope</figcaption>
</figure>

### Warm-up on Si Photodetector

The trans-impendance amplifier hook-up on the Si photodetector needs some time to warm-up. If you got a spurious signal on the oscilloscope, do not worry, give a minute or two and the signal will be gone.

<figure markdown="span">
    ![Before warm-up](https://raw.githubusercontent.com/r3dhyka/qudev/refs/heads/main/docs/assets/beforewarm_si_photodetector.png){ width="400" }
    <figcaption>Figure 3. Before warm-up</figcaption>
</figure>

<figure markdown="span">
    ![After warm-up](https://raw.githubusercontent.com/r3dhyka/qudev/refs/heads/main/docs/assets/afterwarm_si_photodetector.png){ width="400" }
    <figcaption>Figure 4. After warm-up</figcaption>
</figure>
