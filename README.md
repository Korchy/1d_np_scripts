# 1d_np_scripts

Modified script NP_scripts.

NP_Scripts.py - the original module
np_scripts_1d.py - the modified module

Modifications:
- ZZ Move
    - Single anchor (named "1D_NP_Place") without deleting and recreating to improve work speed
    - Removed creation of the dummy to save 3d-cursor position
    - Right mouse button click does not interrupt moving process
    - Pressing space button on the navigation mode (scene scrolling/rotation). Another pressing space button returns to the moving mode
- ZX Copy
    - Changed each other the default copying mode (with and without alt button)
