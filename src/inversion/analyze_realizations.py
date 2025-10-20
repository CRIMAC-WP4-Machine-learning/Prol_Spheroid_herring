import numpy as np
import pandas as pd
import os
import glob
import re

import matplotlib
import matplotlib.pyplot as plt

from misc_read_and_plot_functions import read_data

def read_complex(s):
    return complex(s)

def extract_csv_files(dir, depth, length):
    csv_files = glob.glob(os.path.join(dir, '*.csv'))

    pattern = r"depth_(?P<depth>[0-9.]+)_size_(?P<size>[0-9.a-z]+)_realiz_(?P<realiz>[0-9]+)"

    sv_data = pd.DataFrame()

    for file in csv_files:
        match = re.search(pattern, file)
        if match:
            d = float(match.group('depth'))
            l = match.group('size')
            realiz = match.group('realiz')
            if d == depth and l == length:
                file_data = pd.read_csv(file, converters={'sv': read_complex})
                sv_data['sv_real_{}'.format(realiz)] = file_data.sv
    return sv_data


def do_svd(matrix):
    U, S, Vh = np.linalg.svd(matrix, full_matrices=False)
    print(S)
    return U

def do_average(matrix):
    return np.mean(matrix, axis=1)

def plot_realizations(sv_data, ax):
    for i, col in enumerate(sv_data.columns):
        ax.plot(20*np.log10(np.abs(sv_data[col])), linestyle='--', label=col)


def plot_vectors(vector, label, ax):
    ax.plot(20*np.log10(np.abs(vector)), linewidth=3, label=label)

def main():
    parent_dir = os.path.split(os.getcwd())[0]
    parent_dir = os.path.abspath(os.path.join(parent_dir, '..'))
    realizations_dir = os.path.join(parent_dir, 'model_results', 'school_results', 'realizations')
    depth = 100
    length = '0.1'
    sv_data = extract_csv_files(realizations_dir, depth, length)

    matplotlib.use('TkAgg')
    matplotlib.rcParams.update({'font.size': 22})
    fig, ax = plt.subplots()
    plot_realizations(sv_data, ax)
    sv_data_matrix = np.matrix(sv_data.values, dtype=complex)
    # U = do_average(sv_data_matrix)
    # plot_vectors(U, 'mean', ax)
    U = do_svd(sv_data_matrix)
    print('dot = {}'.format(np.dot(U[:, 0].T, U[:, 0])))
    #print(U @ U.H)
    plot_vectors(U[:, 0], 'U0', ax)
    plot_vectors(U[:, 1], 'U1', ax)
    plot_vectors(U[:, 2], 'U2', ax)
    plot_vectors(U[:, 3], 'U3', ax)

    single_fish_data_dir = os.path.join(parent_dir, 'model_results', 'model_low_freq_results')
    data = read_data(single_fish_data_dir)  # change this folder to point to model results
    data = data[data.depth == depth]
    data = data[data.angle == 90]
    if not length == 'mix':
        data = data[data.length == 100 * float(length)]
    sim_results = data.groupby('length')
    for name, groups in sim_results:
        plot_vectors(groups.f_bs, 'sim', ax)

    ax.legend()
    plt.show()

if __name__ == '__main__':
    main()