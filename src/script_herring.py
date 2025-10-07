from prol_spheroid_vectorized import ProlateSpheroid
from IterativeSolvers import BiCGSTABSolver, IterativeRefinement
import os

class HerringSettings:

    def __init__(self, prefix, ro_s, c_s, a, b, delta_f, min_freq, max_freq, theta_i_deg):
        self.prefix = prefix        # just a name to identify the output files
        # media properties
        self.ro_w = 1027            # the density of the surrounding media [kg/m^3]
        self.ro_s = ro_s            # the density of the spheroid [kg/m^3]
        self.c_w = 1500             # the sound speed in the surrounding media [m/s]
        self.c_s = c_s             # the sound speed in the spheroid [m/s]

        # geometrical properties
        self.a = a               # the length of the semi-major axis [m]
        self.b = b              # the length of the semi-minor axis [m]

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
    
    T=273+T_celsius 
    R=0.2870
    
    # Critical values for Oxygen:
    T_cr=132.5 # "Kelvin" Critical temperature
    P_cr=3.77E6 # "Pa" Critical pressure
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
    return Ro

def createSettings(fish_length, depth, incidence_angle):
    a = 0.01 # fish_length * 0.26 * 0.5
    b_0 = 0.01 * 0.5 # from Gorska & Ona - todo: maybe it also should be varied with length?
    b = 0.004 #b_0 * (1 + depth/10)**(-0.5)

    ro_w = 1027              # density of water
    # adjust ro_s to be approx 14 kg/m^3 at 100 m depth
    P_pa = 1e5 + ro_w*depth*9.81
    # ro_s_0 = 0.00129 * ro_w  # density at 0m
    # ro*_s_100 = 14            # density at 100m
    #ro_s = ro_s_0 * (1 + depth * (ro_s_100 - ro_s_0) / (ro_s_0 * 100))
    ro_s = func_VanDerWaals_Air(P_pa, 15) #(b_0**2)/(b**2)*ro_s_0
    c_w = 1500               # sound speed in water
    c_s = 343 #0.23 * c_w         # the sound speed is assumed not to depend on depth
    freq_Delta = 150
    freq_start = 500
    freq_end = 100001
    return HerringSettings('herring', ro_s, c_s, a, b, freq_Delta, freq_start, freq_end, incidence_angle)



if __name__ == '__main__':
    # if the path to the gfortran compiler is not already in the PATH environment variable, it can be added here
    os.environ['PATH'] += os.pathsep + os.path.abspath(r'C:\bin\mingw64\bin')

    fish_lengths = [0.00] # [0.10, 0.30]
    incidence_angles = [90, 89, 88, 87, 86, 84, 82, 80, 75, 70, 65, 60, 45]   # [90, 82, 75]
    depths = [50] #[10, 50, 100]

    for incidence_angle in incidence_angles:
        for fish_length in fish_lengths:
            for depth in depths:
                print('Running with length {}, incidence angle {}, and depth {}'.format(fish_length, incidence_angle, depth))
                herring_settings = createSettings(fish_length, depth, incidence_angle)
                #solver = BiCGSTABSolver('ILU')
                solver = IterativeRefinement('LU')
                ts_file_name = 'ts_vs_freq_loop_{}_a_{:.5f}_b_{:.5f}_f1_{}_f2_{}_rhos_{:.2f}_IncAngle_{}_depth_{}_length_{}_{}.csv'.format(herring_settings.prefix,
                                                                                                                                   herring_settings.a, herring_settings.b,
                                                                                                                                   int(herring_settings.min_freq / 1000),
                                                                                                                                   int(herring_settings.max_freq / 1000),
                                                                                                                                   herring_settings.ro_s, herring_settings.theta_i_deg,
                                                                                                                                   depth, fish_length,
                                                                                                                                   solver.solver_name())

                ParentDIR=os.path.split(os.getcwd())[0]
                freq_resp_file = os.path.join(ParentDIR, 'temp', ts_file_name)
                if os.path.isfile(freq_resp_file):
                    print('skipping {} since it already exists'.format(ts_file_name))
                    continue
                spheroid = ProlateSpheroid(herring_settings, solver)
                try:
                    spheroid.run(ts_file_name)
                except Exception as e:
                    # skip to the next case if a simulation fails for any reason
                    print(e)
                    pass
