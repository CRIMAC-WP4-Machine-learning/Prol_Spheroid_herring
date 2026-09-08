from prol_spheroid_vectorized import ProlateSpheroid
from IterativeSolvers import IterativeRefinement
import os


class UserDefinedSettings:

    def __init__(self):
        self.prefix = 'SB'        # just a name to identify the output files
        # media properties
        self.ro_w = 1027            # the density of the surrounding media [kg/m^3]
        self.ro_s = 1027*1.0357  # *1.0257  *1.0357           # the density of the spheroid [kg/m^3]
        self.c_w = 1500            # the sound speed in the surrounding media [m/s]
        self.c_s = 1500*1.0279   # * 1.044  *1.0279           # the sound speed in the spheroid [m/s]

        # geometrical properties
        self.a = 0.01               # the length of the semi-major axis [m]
        self.b = 0.0025             # the length of the semi-minor axis [m]

        # frequencies
        self.delta_f = 2000         # the distance between frequencies [Hz]
        self.min_freq = 10000       # the start frequency [Hz]
        self.max_freq = 300100       # the end frequency [Hz]

        #incident angle
        self.theta_i_deg = 90       # the incidence angle [degrees]

        # precision
        self.precision_fbs = 1e-6

# Get the directory where this script is located
base_dir = os.path.dirname(os.path.abspath(__file__))

# Define Output directory inside it
output_dir = os.path.join(base_dir, "Output")

# Create the folder if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

if __name__ == '__main__':

    os.environ['PATH'] += os.pathsep + os.path.abspath(r'C:\bin\mingw64\bin')

    theta_i_deg_vec = [90,60,30]

    solver = IterativeRefinement('LU')

    for theta in theta_i_deg_vec:

        user_defined_settings = UserDefinedSettings()
        user_defined_settings.theta_i_deg = theta

        ts_file_name = (
            'ts_vs_freq_loop_{}_a_{}_b_{}_f1_{}_f2_{}_rhos_{:.2f}_cs{:.2f}_IncAngle_{}_{}.csv'
            .format(user_defined_settings.prefix,
                    user_defined_settings.a,
                    user_defined_settings.b,
                    int(user_defined_settings.min_freq / 1000),
                    int(user_defined_settings.max_freq / 1000),
                    user_defined_settings.ro_s,
                    user_defined_settings.c_s,
                    user_defined_settings.theta_i_deg,
                    solver.solver_name())
        )
        
        # Full path to the CSV file
        ts_file_path = os.path.join(output_dir, ts_file_name)

        spheroid = ProlateSpheroid(user_defined_settings, solver)
        # spheroid.run(ts_file_name)
        spheroid.run(ts_file_path)