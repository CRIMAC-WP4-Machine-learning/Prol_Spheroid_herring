'''
To run, be in Prol_Spheroid_herring directory. for example 
run cd /root/projects/Prol_Spheroid_herring/ 
Then use:
python -m src.distribution.DistributeFish
to run the script
'''
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import glob
import pandas as pd
import re
from scipy.signal import savgol_filter
import itertools

# 1. Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Change the current working directory to the script's directory
os.chdir(script_dir)
print(f"Current working directory changed to: {os.getcwd()}")

# 2. Calculate the parent directory (navigates two directories up.)
CurrentDIR = os.path.abspath(os.path.join(os.getcwd()))
print('Parent DIR: >>> ', CurrentDIR)

# Database Directory containing csv files with TS(f) and F_bs(f):
database_dir = os.path.join(CurrentDIR, 'temp/')
print('database_dir: ',database_dir)

csv_files = [f for f in os.listdir(database_dir) if f.endswith('.csv')]
print(csv_files)


# Define styles
colors = ['b','r', 'k', 'm', 'c', 'y', 'g']
linewidths = [1.5, 1.5, 1.5, 1.5]

# Define dash patterns: (dash_length, space_length, ...)
dash_patterns = [
    (None, None),     # solid line (no dash)
    (5, 3),           # long dash
    (2, 2),           # short dash
    (1, 1),           # dotted
    (5, 2, 1, 2),     # dash-dot
    (10, 4, 2, 4)     # long-short pattern
]

# Cycle through all of them
color_cycle = itertools.cycle(colors)
linewidth_cycle = itertools.cycle(linewidths)
dash_cycle = itertools.cycle(dash_patterns)

plt.figure(figsize=(12, 7))

for CSV_file_i in csv_files:
    file = os.path.join(CurrentDIR, 'temp', CSV_file_i)
    df_i = pd.read_csv(file)

    # Extract fishL
    fishL_match = re.search(r"fishL([\d.]+)", CSV_file_i)
    fishL = float(fishL_match.group(1)) if fishL_match else None

    # Extract N
    N_match = re.search(r"_N_(\d+)", CSV_file_i)
    N = int(N_match.group(1)) if N_match else None

    # Extract Phi values inside brackets and compute average
    phi_match = re.search(r"Phi\[(.*?)\]", CSV_file_i)
    if phi_match:
        phi_values = [float(x) for x in phi_match.group(1).split()]
        phi_avg = np.mean(phi_values)
    else:
        phi_avg = None

    if  (phi_avg < 80):
        DashSpace = 2
    else:
        DashSpace = 0
    
    DashStyle = [3, DashSpace]

    if (N<200) & (fishL < 0.15):
        linewidths = [1.5, 1.5]
    elif (N>200) & (fishL < 0.15):
        linewidths = [1.5, 1.5]
    else:
        linewidths = [1.5, 1.5, 1.5, 1.5]
    linewidth_cycle = itertools.cycle(linewidths)

    if (fishL < 0.15) & (N<200):
        line, = plt.plot(
            df_i['freq'],
            df_i['smoothed'],
            label="L="+str(fishL)+", N="+str(N)+", $\phi_{mean}$="+str(phi_avg),
            color=next(color_cycle),
            linewidth=next(linewidth_cycle)
        )
        SaveFileName = "Overlay"+str(fishL)+"_N_"+str(N)+"_Phi"+str(phi_avg)
        
        # Apply dash pattern
        line.set_dashes(DashStyle)

# for CSV_file_i in csv_files:
#     file = os.path.join(CurrentDIR, 'temp', CSV_file_i)
#     df_i = pd.read_csv(file)

#     # Extract fishL
#     fishL_match = re.search(r"fishL([\d.]+)", CSV_file_i)
#     fishL = float(fishL_match.group(1)) if fishL_match else None

#     # Extract N
#     N_match = re.search(r"_N_(\d+)", CSV_file_i)
#     N = int(N_match.group(1)) if N_match else None

#     # Extract Phi values inside brackets and compute average
#     phi_match = re.search(r"Phi\[(.*?)\]", CSV_file_i)
#     if phi_match:
#         phi_values = [float(x) for x in phi_match.group(1).split()]
#         phi_avg = np.mean(phi_values)
#     else:
#         phi_avg = None

#     print("fishL:", fishL)
#     print("N:", N)
#     print("Phi average:", phi_avg)    
    
#     line, = plt.plot(
#         df_i['freq'],
#         df_i['smoothed'],
#         label="L="+str(fishL)+"N="+str(N)+r", $phi$="+str(phi_avg),
#         color=next(color_cycle),
#         linewidth=next(linewidth_cycle)
#     )
    
#     # Apply dash pattern
#     line.set_dashes(next(dash_cycle))
plt.xlim([10,250])
plt.xlabel(' Frequency (kHz)', fontsize = 12)
plt.ylabel(' Sv ?', fontsize = 12)
plt.tick_params(axis='both', which='major', labelsize=12)  # change 12 to 14 or 16 for larger text
plt.legend(fontsize=14, ncol=2)
plt.savefig("temp/"+SaveFileName+".png", dpi=300, bbox_inches='tight')  # PNG

plt.show()    