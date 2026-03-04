from prol_spheroid_vectorized import ProlateSpheroid
from IterativeSolvers import BiCGSTABSolver, IterativeRefinement
import os
import pandas as pd

class HerringSettings:

    def __init__(self, prefix, Res_mm, ro_s, c_s, a, b, delta_f, min_freq, max_freq, theta_i_deg):
        self.prefix = prefix        # just a name to identify the output files
        # media properties
        self.ro_w = 1027            # the density of the surrounding media [kg/m^3]
        self.ro_s = ro_s            # the density of the spheroid [kg/m^3]
        self.c_w = 1500             # the sound speed in the surrounding media [m/s]
        self.c_s = c_s             # the sound speed in the spheroid [m/s]

        # geometrical properties
        self.a = a               # the length of the semi-major axis [m]
        self.b = b              # the length of the semi-minor axis [m]
        self.Res = Res_mm
        # frequencies
        self.delta_f = delta_f         # the distance between frequencies [Hz]
        self.min_freq = min_freq       # the start frequency [Hz]
        self.max_freq = max_freq       # the end frequency [Hz]

        #incident angle
        self.theta_i_deg = theta_i_deg       # the incidence angle [degrees]

        # precision
        self.precision_fbs = 1e-6

def func_VanDerWaals_Air(P_pa,T_celsius):
    import numpy as np
    # Van Der Waals eqution from "Thermodynamics - An Engineering Approach, Cengel & Boles 2014" Eq 3-22
    # where "a" and "b" are estimated from 3-23

    T = 273 + T_celsius
    R = 0.2870

    # Critical values for Oxygen:
    T_cr = 132.5  # "Kelvin" Critical temperature
    P_cr = 3.77E6  # "Pa" Critical pressure
    #V_cr=0.0780 # m³/kmol  Critical per unit kmol

    a = 27 * R * R * T_cr * T_cr / (64 * P_cr)
    b = R * T_cr / (8 * P_cr)

    # Av³+Bv²+Cv+D=0
    A = P_pa
    B = -P_pa * b - R * T
    C = a
    D = -a * b

    v_vec = np.roots([A, B, C, D])

    Ro = 0.001 * 1 / np.real(v_vec[0])
    return Ro


def func_VanDerWaals_Oxygen(P_pa,T_celsius):
    import numpy as np
#    import matplotlib.pyplot as plt
    
    # Van Der Waals eqution from "Thermodynamics - An Engineering Approach, Cengel & Boles 2014" Eq 3-22
    # where "a" and "b" are estimated from 3-23
    
    #np.roots([1,1,-2])
    # For Oxygen:
    
#    z=1 # "m"  Depth
#    T1=273+6 # "K" temperature
#    T2=273+12 # "K" temperature
#    T3=273+20 # "K" temperature
    
#    z_vec=np.arange(0,1010,50)
#    
#    P=1E5+z*1000*9.81
    T=273+T_celsius 
    
    R=0.2598
    
    # Critical values for Oxygen:
    T_cr=154.8 # "Kelvin" Critical temperature
    P_cr=5.08E6 # "Pa" Critical pressure
    #V_cr=0.0780 # m³/kmol  Critical per unit kmol
    
    a=27*R*R*T_cr*T_cr/(64*P_cr)
    b=R*T_cr/(8*P_cr)
    
    # Av³+Bv²+Cv+D=0
    
    A=P_pa
    B=-P_pa*b-R*T
    C=a
    D=-a*b
    
    v_vec=np.roots([A,B,C,D])
    
    Ro=0.001*1/np.real(v_vec[0])
#    print(Ro)
    return Ro


def createSettings(_Target_i,_df, _incidence_angle):
    
    depth = _df.loc[df["Target"] == _Target_i, "Depth_m"].iloc[0]
    Elongation = _df.loc[df["Target"] == _Target_i, "Elongation"].iloc[0]
    Res_mm = _df.loc[df["Target"] == _Target_i, "Res_mm"].iloc[0]
    ro_s = _df.loc[df["Target"] == _Target_i, "rho_s"].iloc[0]

    print(depth , Elongation, Res_mm)

    b = (Res_mm / Elongation**(1/3) ) * 1E-3 
    a = b * Elongation

    ro_w = 1027              # density of water
    # adjust ro_s to be approx 14 kg/m^3 at 100 m depth
    P_pa = 1e5 + ro_w * depth * 9.81
    # ro_s_0 = 0.00129 * ro_w  # density at 0m
    # ro*_s_100 = 14            # density at 100m
    # ro_s = ro_s_0 * (1 + depth * (ro_s_100 - ro_s_0) / (ro_s_0 * 100))
    ro_s = func_VanDerWaals_Oxygen(P_pa, 10) #(b_0**2)/(b**2)*ro_s_0
    print('Van der Waals ro_s: ', ro_s)
    c_w = 1500               # sound speed in water
    c_s = 325 #0.23 * c_w         # the sound speed is assumed not to depend on depth
    freq_Delta = 1000
    freq_start = 30000
    freq_end = 380001
    return HerringSettings('Target_'+str(_Target_i), Res_mm, ro_s, c_s, a, b, freq_Delta, freq_start, freq_end, _incidence_angle)



if __name__ == '__main__':
    # if the path to the gfortran compiler is not already in the PATH environment variable, it can be added here
    os.environ['PATH'] += os.pathsep + os.path.abspath(r'C:\bin\mingw64\bin')

    data = {
    "Target": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "Depth_m": [412, 557, 520, 147, 166, 428, 426, 521, 516],
    "Elongation": [2.43, 1.16, 2.93, 3.68, 2.90, 2.57, 2.80, 2.06, 1.06],
    "Res_mm": [0.221, 0.424, 0.328, 0.264, 0.268, 0.321, 0.316, 0.408, 0.446],
    "rho_s": [59.7, 81.43, 75.83, 21.59, 24.25, 62.07, 61.77, 75.98, 75.22]
    }
    incidence_angle = 70 
    df = pd.DataFrame(data)
    print(df)

    for Target_i in df['Target']:
        print('Running with length {}, incidence angle {}, and depth {}'.format(Target_i, 1, 1))
        herring_settings = createSettings(Target_i, df, incidence_angle)
        solver = BiCGSTABSolver('ILU')
        solver = IterativeRefinement('LU')
        ts_file_name = 'TS_{}_Res_{}_a_{:.5f}_b_{:.5f}_f1_{}_f2_{}_rhos_{:.2f}_IncAngle_{}_{}.csv'.format(herring_settings.prefix, herring_settings.Res,
                                                                                                                            herring_settings.a, herring_settings.b,
                                                                                                                            int(herring_settings.min_freq / 1000),
                                                                                                                            int(herring_settings.max_freq / 1000),
                                                                                                                            herring_settings.ro_s, herring_settings.theta_i_deg,
                                                                                                                            solver.solver_name())

        ParentDIR=os.path.split(os.getcwd())[0]
        freq_resp_file = os.path.join(ParentDIR, 'temp', ts_file_name)
        if os.path.isfile(freq_resp_file):
            print('skipping {} since it already exists'.format(ts_file_name))
            continue
        spheroid = ProlateSpheroid(herring_settings, solver)
        try:
            spheroid.run(freq_resp_file)
        except Exception as e:
            # skip to the next case if a simulation fails for any reason
            print(e)
            pass
