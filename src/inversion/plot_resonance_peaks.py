import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
import os

from src.inversion.misc_read_and_plot_functions import read_data
from src.inversion.liquid_sphere import far_field_pattern_liquid_sphere, func_VanDerWaals_Air


def plot_df(data):
    matplotlib.use('TkAgg')
    matplotlib.rcParams.update({'font.size': 22})
    fig, ax = plt.subplots()
    linestyles = {
        30: '-',
        10: '--'
    }
    colors = {
        10: 'k',
        50: 'b',
        100: 'r'
    }
    line_thickness = {
        'spheroid': 1,
        'sphere': 2
    }
    for depth in data.depth.unique():
        data_depth = data[data.depth == depth]
        color = colors[depth] if depth in colors else 'g'
        for angle in [90]: #data_depth.angle.unique():
            data_depth_angle = data_depth[data_depth.angle == angle]
            for length in data_depth_angle.length.unique():
                linestyle = linestyles[length] if length in linestyles else '-'
                data_depth_angle_length = data_depth_angle[data_depth_angle.length == length]
                for t in data_depth_angle_length.type.unique():
                    l_thickness = line_thickness[t]
                    data_depth_angle_length_type = data_depth_angle_length[data_depth_angle_length.type == t]
                    if t == 'spheroid':
                        label = 'length = {}, depth = {}, angle = {}'.format(length, depth, angle)
                    else:
                        radius = data_depth_angle_length_type.radius.unique()[0]
                        label = '{} size = {:.4f}, depth = {}, angle = {}'.format(t, radius, depth, angle)
                    ax.plot(data_depth_angle_length_type.f_kHz, data_depth_angle_length_type.TS, linestyle=linestyle,
                            linewidth=l_thickness, color=color, marker='.', label=label)
    ax.set_xlabel('Frequency [kHz]')
    ax.set_ylabel('TS')
    ax.legend()
    ax.grid()
    plt.show()


def create_df_liquid_sphere(start_freq, end_freq, delta_freq, depths, lengths):
    rho_w = 1027

    c_w = 1500
    c_s = 0.23 * c_w
    theta_inc = np.pi / 2
    thetas = [theta_inc + np.pi]
    num_terms = 10
    results = pd.DataFrame(columns=['angle', 'depth', 'length', 'radius', 'f_kHz', 'TS', 'f_bs', 'mod_f_bs', 'arg_f_bs'])
    for d in depths:
        P_pa = 1e5 + rho_w*d*9.81
        rho_s = func_VanDerWaals_Air(P_pa, 15)
        for l in lengths:
            # find radii to give the same volume as the prolate spheroid
            axis = length_to_ps_axis(d, l, 'b0_varies')
            radius = (axis['b'] * axis['b'] * axis['a']) ** (1/3)
            for f in np.linspace(start=start_freq, stop=end_freq, num=int((end_freq - start_freq) / delta_freq +1)):
                k_0 = 2 * np.pi * f / c_w
                k_1 = 2 * np.pi * f / c_s
                form_function = far_field_pattern_liquid_sphere(rho_w, rho_s, k_0, k_1, radius, thetas, num_terms, theta_inc)
                TS = 20*np.log10(np.abs(form_function))
                df = pd.DataFrame({'angle': 90, 'depth': d, 'length': l, 'radius': radius, 'f_kHz': f / 1000, 'TS': TS, 'f_bs': form_function,
                                   'mod_f_bs': np.abs(form_function), 'arg_f_bs': np.angle(form_function)})
                results = pd.concat([results, df])
    return results

def length_to_ps_axis(depth, length, v='b0_const'):
    if depth == 10:
        if length == 30:
            return {'a': 0.039, 'b': 0.00354 if v=='b0_const' else 0.00707}
        elif length == 10:
            return {'a': 0.013, 'b': 0.00354}
    elif depth == 50:
        if length == 30:
            return {'a': 0.039, 'b': 0.00204 if v=='b0_const' else 0.00408}
        elif length == 10:
            return {'a': 0.013, 'b': 0.00204}
    elif depth == 100:
        if length == 30:
            return {'a': 0.039, 'b': 0.00151 if v=='b0_const' else 0.00302}
        elif length == 10:
            return {'a': 0.013, 'b': 0.00151}
    raise ValueError('Unknown depth and length')


def main():
    ParentDIR = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))
    data = read_data(os.path.join(ParentDIR, 'model_results', 'model_low_freq_b0_varies_results')) # r'F:\gitlab\Prol_Spheroid_herring\model_results\model_low_freq_b0_varies_results')  # change this folder to point to model results
    data = data[data.depth == 100]
    data['type'] = 'spheroid'
    # data_sphere = create_df_liquid_sphere(100, 10000, 50, [100], np.array([30, 10]))
    # data_sphere['type'] = 'sphere'
    # data = pd.concat([data, data_sphere])
    plot_df(data)


if __name__ == '__main__':
    main()