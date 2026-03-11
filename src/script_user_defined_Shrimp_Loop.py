from prol_spheroid_vectorized import ProlateSpheroid
from IterativeSolvers import IterativeRefinement
import os


class UserDefinedSettings:

    def __init__(self):
        self.prefix = 'Shrimp7d'        # just a name to identify the output files
        # media properties
        self.ro_w = 1027            # the density of the surrounding media [kg/m^3]
        self.ro_s = 1027 * 1.0357            # the density of the spheroid [kg/m^3]
        self.c_w = 1500             # the sound speed in the surrounding media [m/s]
        self.c_s = 1500 * 1.0279            # the sound speed in the spheroid [m/s]

        # geometrical properties
        self.a = 0.038               # the length of the semi-major axis [m]
        self.b = 0.0069              # the length of the semi-minor axis [m]

        # frequencies
        self.delta_f = 1000         # the distance between frequencies [Hz]
        self.min_freq = 30000       # the start frequency [Hz]
        self.max_freq = 380100       # the end frequency [Hz]

        #incident angle
        self.theta_i_deg = 90       # the incidence angle [degrees]

        # precision
        self.precision_fbs = 1e-6


if __name__ == '__main__':

    os.environ['PATH'] += os.pathsep + os.path.abspath(r'C:\bin\mingw64\bin')

    theta_i_deg_vec = [90, 80, 75, 60, 45]

    solver = IterativeRefinement('LU')

    for theta in theta_i_deg_vec:

        user_defined_settings = UserDefinedSettings()
        user_defined_settings.theta_i_deg = theta

        ts_file_name = (
            'ts_vs_freq_loop_{}_a_{}_b_{}_f1_{}_f2_{}_rhos_{:.2f}_IncAngle_{}_{}.csv'
            .format(user_defined_settings.prefix,
                    user_defined_settings.a,
                    user_defined_settings.b,
                    int(user_defined_settings.min_freq / 1000),
                    int(user_defined_settings.max_freq / 1000),
                    user_defined_settings.ro_s,
                    user_defined_settings.theta_i_deg,
                    solver.solver_name())
        )

        spheroid = ProlateSpheroid(user_defined_settings, solver)
        spheroid.run(ts_file_name)