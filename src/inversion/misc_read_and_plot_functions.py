import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
import glob
import re

from scipy import stats
import seaborn as sns

def plot_complex_arguments(data, data_2, f_1_kHz, f_2_kHz, angles_1, angles_2):
    depths = [10]
    lengths = [0.3]
    unwrap = True
    densely_dashdotted = (0, (3, 1, 1, 1))
    linestyles = ['-', '--', ':', '-.', densely_dashdotted]
    colors = ['k', 'b', 'm', 'g', 'c', 'y', 'gray', 'orange', 'brown']
    symbols = [None, '.', 'v', 's', '*']
    matplotlib.use('TkAgg')
    matplotlib.rcParams.update({'font.size': 22})
    fig, ax = plt.subplots()
    plot_arguments(angles_1, ax, colors, data, depths, f_1_kHz, f_2_kHz, lengths, linestyles, symbols, unwrap)

    colors_2 = ['r']
    plot_arguments(angles_2, ax, colors_2, data_2, depths, f_1_kHz, f_2_kHz, lengths, linestyles, symbols, unwrap)
    ax.set_ylabel('arg(f_bs) [deg]')
    ax.set_xlabel('Frequency [Hz]')
    # ax.set_xscale('log')
    ax.grid(True)
    ax.legend(prop={'size': 12})
    plt.show()


def plot_arguments(angles, ax, colors, data, depths, f_1_kHz, f_2_kHz, lengths, linestyles, symbols, unwrap=True):
    for length, style in zip(lengths, linestyles):
        data_for_length = data[data.length == length]
        for depth, color in zip(depths, colors):
            data_for_depth = data_for_length[data_for_length.depth == depth]
            for angle, symbol in zip(angles, symbols):
                data_for_angle = data_for_depth[data_for_depth.angle == angle]
                if data_for_angle.empty:
                    continue
                data = data_for_angle.sort_values(by=['f_kHz'])
                data = data[(data.f_kHz >= f_1_kHz) & (data.f_kHz < f_2_kHz)]
                ax.plot(data.f_kHz * 1000, (np.unwrap(data['arg_f_bs'], np.pi) if unwrap else data['arg_f_bs']) * 180 / np.pi,
                        color=color, linestyle=style, marker=symbol, markevery=3,
                        label='Length: {} cm, Depth: {} m, Angle: {} deg'.format(length * 100, depth, angle))
    ylim = ax.get_ylim()
    xlim = ax.get_xlim()
    for k in range(0, int(-ylim[0] / 180) + 1):
        if k % 2 == 1:
            ax.hlines(-k * 180, xlim[0], xlim[1], linestyle=':', color='k')
    for k in range(0, int(ylim[1] / 180) + 1):
        if k % 2 == 1:
            ax.hlines(k * 180, xlim[0], xlim[1], linestyle=':', color='k')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)


def plot_two_datasets(data_1, data_2, angles_1, angles_2):
    angles_1 = [82, 86, 90] # sorted(herring_df.angle.unique(), reverse=True)
    depths = [10] # sorted(herring_df.depth.unique())
    lengths = [0.3]  #sorted(herring_df.length.unique())
    densely_dashdotted = (0, (3, 1, 1, 1))
    linestyles = ['-', '--', ':', '-.', densely_dashdotted]
    colors = ['k', 'b', 'm', 'g', 'c', 'y', 'gray', 'orange', 'brown']
    symbols = [None, '.', 'v', 's', '*']
    matplotlib.use('TkAgg')
    matplotlib.rcParams.update({'font.size': 22})
    fig, ax = plt.subplots()
    plot_frequency_responses(ax, data_1, angles_1, depths, lengths, False, True, {},
                             linestyles, colors, symbols)


    angles_2 = [86]
    linestyles_2 = ['-']
    colors_2 = ['r']
    symbols_2 = [symbols[angles_1.index(i)] for i in angles_2]
    plot_frequency_responses(ax, data_2, angles_2, depths, lengths, False, True, {},
                             linestyles_2, colors_2, symbols_2)
    plt.show()


def far_field_vs_vectorized(data, ts_drops):
    angles = [86, 90] # sorted(herring_df.angle.unique(), reverse=True)
    depths = [10] # sorted(herring_df.depth.unique())
    lengths = [0.3]  #sorted(herring_df.length.unique())

    plot_standard = True
    plot_drop = False

    densely_dashdotted = (0, (3, 1, 1, 1))
    linestyles = ['-', '--', ':', '-.', densely_dashdotted]
    colors = ['k', 'b', 'r', 'm', 'g', 'c', 'y', 'gray', 'orange', 'brown']
    symbols = [None, '.', 'v', 's', '*']

    matplotlib.use('TkAgg')
    matplotlib.rcParams.update({'font.size': 22})
    fig, ax = plt.subplots()
    plot_frequency_responses(ax, data, angles, depths, lengths, plot_drop, plot_standard, ts_drops,
                             linestyles, colors, symbols)
    plt.show()


def plot_frequency_responses(ax, data, angles, depths, lengths, plot_drop, plot_standard, ts_drops,
                             linestyles, colors, symbols):

    for length, style in zip(lengths, linestyles):
        data_for_length = data[data.length == length]
        for depth, color in zip(depths, colors):
            data_for_depth = data_for_length[data_for_length.depth == depth]
            for angle, symbol in zip(angles, symbols):
                data_for_angle = data_for_depth[data_for_depth.angle == angle]
                if data_for_angle.empty:
                    continue
                data = data_for_angle.sort_values(by=['f_kHz'])
                if plot_standard:
                    ax.plot(data.f_kHz * 1000, data.TS, color=color, linestyle=style, marker=symbol, markevery=3,
                            label='Length: {} cm, Depth: {} m, Angle: {} deg'.format(length * 100, depth, angle))
                if plot_drop and (angle, depth, length) in ts_drops:
                    drop = ts_drops[(angle, depth, length)]
                    triangle_x = [drop['fkHz_1'] * 1000, drop['fkHz_2'] * 1000, drop['fkHz_2'] * 1000,
                                  drop['fkHz_1'] * 1000]
                    triangle_y = [drop['TS_1'], drop['TS_1'], drop['TS_2'], drop['TS_1']]
                    ax.plot(triangle_x, triangle_y, color='r', linestyle=style, marker=symbol)
    ax.set_ylabel('TS [dB]')
    ax.set_xlabel('Frequency [Hz]')
    # ax.set_xscale('log')
    ax.grid(True)
    ax.legend(prop={'size': 12})


def transducer_responses(herring_df):
    transducers = [4, 18, 38, 70, 120, 200]
    depths = [50]

    responses = herring_df[(herring_df.f_kHz.isin(transducers)) & (herring_df.depth.isin(depths))]
    matplotlib.use('TkAgg')
    matplotlib.rcParams.update({'font.size': 22})
    matplotlib.rcParams.update({'lines.markersize': 10})
    fig, ax = plt.subplots()
    sns.scatterplot(x=responses.f_kHz, y=responses.TS, hue=responses.length, style=responses.angle, palette='rainbow')
    ax.set_ylabel('TS [dB]')
    ax.set_xlabel('Frequency [kHz]')
    #ax.set_xscale('log')
    ax.grid(True)
    ax.legend(prop={'size': 12})
    plt.show()


def plot_ts_drop_vs_size(ts_drops, regression=None):
    matplotlib.use('TkAgg')
    matplotlib.rcParams.update({'font.size': 22})
    depths = [10, 50, 100]
    angles = [86, 84, 82, 80, 78]
    colors = ['k', 'b','r','m','g', 'c', 'y', 'gray', 'orange', 'brown']
    symbols = ['.', 'v', 's', '*', '^']
    fig, ax = plt.subplots()
    for (angle, depth, length), ts_drop in ts_drops.items():
        if not depth in depths or not angle in angles:
            continue
        delta_ts = ts_drop['TS_1'] - ts_drop['TS_2']
        depth_index = depths.index(depth)
        angle_index = angles.index(angle)
        #ax.plot('{}'.format(length), delta_ts, linestyle='None', color=colors[depth_index], marker=symbols[angle_index], label='Depth={}, Angle={}'.format(depth, angle))
        ax.plot(length, delta_ts, linestyle='None', color=colors[depth_index], marker=symbols[angle_index], label='Depth={}, Angle={}'.format(depth, angle))
    for depth in depths:
        if regression is not None and depth in regression:
            r = regression[depth]
            x_plot = np.linspace(0.1, 0.3, 100)
            depth_index = depths.index(depth)
            ax.plot(x_plot, x_plot * r.slope + r.intercept, color=colors[depth_index], label='Linear regression, depth={}, $R^2$={:.2}'.format(depth, r.rvalue**2))

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), prop={'size': 12})
    ax.set_xlabel('Fish length [m]')
    ax.set_ylabel('$\Delta$ TS [dB]')
    plt.show()


def plot_ts_drop_freq_vs_size(ts_drops, regression=None):
    matplotlib.use('TkAgg')
    matplotlib.rcParams.update({'font.size': 22})
    depths = [10, 50, 100]
    angles = [86, 84, 82, 80, 78]
    colors = ['k', 'b','r','m','g', 'c', 'y', 'gray', 'orange', 'brown']
    symbols = ['.', 'v', 's', '*', '^']
    fig, ax = plt.subplots()
    for (angle, depth, length), ts_drop in ts_drops.items():
        if not depth in depths or not angle in angles:
            continue
        mean_freq = 0.5* (ts_drop['fkHz_1'] + ts_drop['fkHz_2'])
        depth_index = depths.index(depth)
        angle_index = angles.index(angle)
        ax.plot(length, mean_freq, linestyle='None', color=colors[depth_index], marker=symbols[angle_index], label='Depth={}, Angle={}'.format(depth, angle))
    for depth in depths:
        if regression is not None and depth in regression:
            r = regression[depth]
            x_plot = np.linspace(0.1, 0.3, 100)
            depth_index = depths.index(depth)
            ax.plot(x_plot, x_plot * r.slope + r.intercept, color=colors[depth_index], label='Linear regression, depth={}, $R^2$={:.2}'.format(depth, r.rvalue**2))
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), prop={'size': 12})
    ax.set_xlabel('Fish length [m]')
    ax.set_ylabel('Mean frequency of TS-drop [kHz]')
    plt.show()

def lin_regress_ts_drop(ts_drops):
    depths = [10]
    angles = [86, 84, 82, 80, 78, 76]
    x_arrays, y_arrays = create_regression_vectors_ts_drops(angles, depths, ts_drops)
    regressions = {}
    for d in depths:
        depth_index = depths.index(d)
        x = x_arrays[depth_index]
        y = y_arrays[depth_index]
        regressions[d] = stats.linregress(x, y)
    return regressions


def create_regression_vectors_ts_drops(angles, depths, ts_drops):
    x_arrays = [[] for _ in depths]
    y_arrays = [[] for _ in depths]

    for (angle, depth, length), ts_drop in ts_drops.items():
        if not depth in depths or not angle in angles:
            continue
        delta_ts = ts_drop['TS_1'] - ts_drop['TS_2']
        depth_index = depths.index(depth)
        x = x_arrays[depth_index]
        y = y_arrays[depth_index]
        x.append(length)
        y.append(delta_ts)
    return np.asarray(x_arrays), np.asarray(y_arrays)


def lin_regress_ts_drop_normalized(ts_drops):
    depths = [10, 50, 100]
    angles = [86, 84, 82]
    x_arrays, y_arrays = create_regression_vectors_ts_drops(angles, depths, ts_drops)

    return create_normalized_regression(depths, x_arrays, y_arrays)


def create_normalized_regression(depths, x_arrays, y_arrays):
    regressions = {}
    x_means = {}
    x_stds = {}
    y_means = {}
    y_stds = {}
    for d in depths:
        depth_index = depths.index(d)
        x = x_arrays[depth_index]
        y = y_arrays[depth_index]
        x_mean = np.mean(x)
        x_std = np.std(x)
        y_mean = np.mean(y)
        y_std = np.std(y)
        x = x - x_mean
        x = x / x_std
        y = y - y_mean
        y = y / y_std
        x_means[d] = x_mean
        x_stds[d] = x_std
        y_means[d] = y_mean
        y_stds[d] = y_std
        regressions[d] = stats.linregress(x, y)
    return regressions, x_means, x_stds, y_means, y_stds


def lin_regress_ts_drop_freq(ts_drops):
    depths = [10, 50, 100]
    angles = [86, 84, 82]
    regressions, x_arrays, y_arrays = create_regression_vectors_ts_drop_freq(angles, depths, ts_drops)
    for d in depths:
        depth_index = depths.index(d)
        x = x_arrays[depth_index]
        y = y_arrays[depth_index]
        regressions[d] = stats.linregress(x, y)
    return regressions


def create_regression_vectors_ts_drop_freq(angles, depths, ts_drops):
    x_arrays = [[] for _ in depths]
    y_arrays = [[] for _ in depths]
    regressions = {}
    for (angle, depth, length), ts_drop in ts_drops.items():
        if not depth in depths or not angle in angles:
            continue
        mean_freq = 0.5 * (ts_drop['fkHz_1'] + ts_drop['fkHz_2'])
        depth_index = depths.index(depth)
        x = x_arrays[depth_index]
        y = y_arrays[depth_index]
        x.append(length)
        y.append(mean_freq)
    return regressions, x_arrays, y_arrays


def lin_regress_ts_drop_freq_normalized(ts_drops):
    depths = [10, 50, 100]
    angles = [86, 84, 82]
    regressions, x_arrays, y_arrays = create_regression_vectors_ts_drop_freq(angles, depths, ts_drops)

    return create_normalized_regression(depths, x_arrays, y_arrays)

def normalize(array):
    mean = np.mean(array)
    array -= mean
    std = np.std(array)
    array /= std
    return array


def ts_drop_pca_regression(ts_drops):
    angles = [86, 84, 82]
    depths = [10, 50, 100]
    lengths = [0.1, 0.15, 0.25, 0.3]
    y = []
    x = []
    for (angle, depth, length), ts_drop in ts_drops.items():
        if not depth in depths or not angle in angles or not length in lengths:
            continue
        y.append(length)
        delta_ts = ts_drop['TS_1'] - ts_drop['TS_2']
        mean_freq = 0.5* (ts_drop['fkHz_1'] + ts_drop['fkHz_2'])
        x.append([delta_ts, mean_freq])
    y = np.asarray(y)
    x = np.vstack(x)
    x[:, 0] = normalize(x[:, 0].copy())
    x[:, 1] = normalize(x[:, 1].copy())
    print()


def read_data(folder):
    herring_files = glob.glob(r'{}\ts_vs_freq_loop_herring*'.format(folder))
    herring_df = pd.DataFrame(columns=['angle', 'depth', 'length', 'f_kHz', 'TS', 'f_bs'])
    for file in herring_files:
        r = re.search('\D*?_rhos_(.*)_IncAngle_(.*)_depth_(.*)_length_(.*)_(.*)_', file)
        rhos = float(r.group(1))
        angle = float(r.group(2))
        depth = float(r.group(3))
        length = float(r.group(4))
        # print('rhos = {}, depth = {}'.format(rhos, depth))
        data = extract_file_ts([file])
        df = pd.DataFrame({'angle': angle, 'depth': depth, 'length': length, 'f_kHz': data.Freq_kHz, 'TS': data.TS, 'f_bs': data.f_bs})
        #df['TS_smooth'] = df.rolling(window=5, center=True, min_periods=0)['TS'].mean()
        df['TS'] = 20 * np.log10(np.abs(df['f_bs']))
        df['mod_f_bs'] = np.abs(df['f_bs'])
        df['arg_f_bs'] = np.angle(df['f_bs'])
        herring_df = pd.concat([herring_df, df])
    return herring_df


def average_over_incidence_angles(data, new_incidence_angle_means, incidence_angle_std):
    new_data = pd.DataFrame(columns=data.columns)
    for angle in new_incidence_angle_means:
        nd = stats.norm(angle, incidence_angle_std)
        for length in sorted(data.length.unique()):
            data_for_length = data[data.length == length]
            for depth in sorted(data_for_length.depth.unique()):
                data_for_depth = data_for_length[data_for_length.depth == depth]
                weight_intervals = find_weight_intervals(data_for_depth)
                weights = {}
                sum_weights = 0
                for data_angle in data_for_depth.angle.unique():
                    interval_1 = weight_intervals[data_angle]
                    interval_2 = weight_intervals[90 + 90 - data_angle]
                    w_1 = nd.cdf(interval_1[1]) - nd.cdf(interval_1[0])
                    w_2 = nd.cdf(interval_2[1]) - nd.cdf(interval_2[0])
                    weights[data_angle] = w_1 + w_2
                    sum_weights += w_1 + w_2
                # weights = {k: v for k, v in weights.items() if v > 0.001}
                # equal_weight = 1.0/len(weights)
                # for k in weights.keys():
                #     weights[k] = equal_weight

                new_data_for_depth = data_for_depth[data_for_depth.angle == data_for_depth.angle.unique().min()].drop(columns=['TS', 'f_bs']).copy(deep=True)
                new_data_for_depth['angle'] = angle
                new_data_for_depth['f_bs'] = np.sum([w * np.asarray(data_for_depth[data_for_depth.angle == a]['f_bs']) for (a, w) in weights.items()], axis=0)
                new_data_for_depth['TS'] = 20 * np.log10(np.abs(new_data_for_depth['f_bs']))
                new_data_for_depth['mod_f_bs'] = np.abs(new_data_for_depth['f_bs'])
                new_data_for_depth['arg_f_bs'] = np.angle(new_data_for_depth['f_bs'])
                new_data = pd.concat([new_data, new_data_for_depth], ignore_index=True)
    return new_data


def find_weight_intervals(data):
    available_angles = np.asarray(sorted(data.angle.unique()))
    available_mid_points = 0.5 * (available_angles[:-1] + available_angles[1:])
    available_mid_points = np.insert(available_mid_points, 0, -np.inf)
    available_mid_points = np.append(available_mid_points, 90)
    weight_intervals = {}
    for angle, interval_start, interval_end in zip(available_angles, available_mid_points, available_mid_points[1:]):
        weight_intervals[angle] = (interval_start, interval_end)
        weight_intervals[90 + (90 - angle)] = (90 + (90 - interval_end), 90 + (90 - interval_start))
    return weight_intervals


def find_largest_ts_drops(data_df, frequency_interval_length, start_freq):
    columns = ['TS_1', 'TS_2', 'fkHz_1', 'fkHz_2']
    group_df = data_df.groupby(['angle', 'depth', 'length'])
    ts_drops = {}
    for name, groups in group_df:
        delta_f = float(groups['f_kHz'].diff().max())  * 1000
        start_freq_index = int(start_freq / delta_f)
        f_period = int(frequency_interval_length / delta_f)
        smooth_ts = groups.rolling(window=10, center=True, min_periods=0)['TS'].median()
        ts_drop = smooth_ts[start_freq_index:].diff(periods=-f_period).max()
        ts_drop_index = smooth_ts[start_freq_index:].diff(periods=-f_period).argmax()
        ts_1 = smooth_ts[start_freq_index:].iloc[ts_drop_index]
        ts_2 = smooth_ts[start_freq_index:].iloc[ts_drop_index + f_period]
        f_1 = groups['f_kHz'][start_freq_index:].iloc[ts_drop_index]
        f_2 = groups['f_kHz'][start_freq_index:].iloc[ts_drop_index + f_period]
        data = [(ts_1, ts_2, f_1, f_2)]
        ts_drops[name] = [dict(zip(columns, x)) for x in data][0]
    return ts_drops


def extract_file_ts(files):
    data = pd.DataFrame()
    for file in files:
        df = pd.read_csv(file)
        #df.loc[len(df), 'Freq'] = 0
        data = pd.concat([data, df])
    if 'Freq' in data:
        data['Freq_kHz'] = data['Freq'] / 1000
    if 'f_bs' in data:
        data['f_bs'] = np.complex128(data['f_bs'])
    return data


def test_inversion_multiple(ts_drop_slope, ts_drop_freq_slope,
                            x_mean, x_std, y_mean_drop, y_std_drop, y_mean_drop_freq, y_std_drop_freq):
    ts_drop = 8
    ts_drop_freq = 70

    ts_drop_normalized = (ts_drop - y_mean_drop) / y_std_drop
    ts_drop_freq_normalized = (ts_drop_freq - y_mean_drop_freq) / y_std_drop_freq
    y = np.asarray([ts_drop_normalized, ts_drop_freq_normalized])
    beta = np.asarray([ts_drop_slope.slope, ts_drop_freq_slope.slope])

    x = np.dot(y, 1./beta)

    resid = y - x * beta

    length = x * x_std + x_mean
    print('inverted length = {}'.format(length))


def test_inversion(ts_drop_regressions_normalized, x_means, x_stds, y_means, y_stds):
    # test inversion
    depth = 100
    regression_slope = ts_drop_regressions_normalized[depth]
    x_mean = x_means[depth]
    x_std = x_stds[depth]
    y_mean = y_means[depth]
    y_std = y_stds[depth]
    ts_drop = 8
    ts_drop_normalized = ts_drop - y_mean
    ts_drop_normalized = ts_drop_normalized / y_std
    x = ts_drop_normalized / regression_slope.slope
    length = x * x_std + x_mean
    print('inverted length = {}'.format(length))


if __name__ == '__main__':
    data = read_data(r'F:\gitlab\Prol_Spheroid_herring\model_results\model_backscatter_results')  # change this folder to point to model results
    data_averaged = average_over_incidence_angles(data, [86], 15)

    #ts_drops = find_largest_ts_drops(data, 50000, 15000)
    #ts_drop_pca_regression(ts_drops)
    #ts_drop_regressions = lin_regress_ts_drop(ts_drops)

    #ts_drop_freq_regressions = lin_regress_ts_drop_freq(ts_drops)
    #plot_ts_drop_vs_size(ts_drops, ts_drop_regressions)
    #plot_ts_drop_freq_vs_size(ts_drops, ts_drop_freq_regressions)
    #far_field_vs_vectorized(data, ts_drops)
    plot_two_datasets(data, data_averaged, [82, 86, 90], [86])
    #plot_complex_arguments(data, data_averaged, 15, 260, [82, 86, 90], [86])
    #transducer_responses(data)

    # ts_drop_regressions_normalized, x_means_ts_drop, x_stds_ts_drop, y_means_ts_drop, y_stds_ts_drop = lin_regress_ts_drop_normalized(ts_drops)
    # ts_drop_freq_regressions_normalized, x_means_ts_drop_freq, x_stds_ts_drop_freq, y_means_ts_drop_freq, y_stds_ts_drop_freq = lin_regress_ts_drop_freq_normalized(ts_drops)
    # #test_inversion(ts_drop_regressions_normalized, x_means_ts_drop, x_stds_ts_drop, y_means_ts_drop, y_stds_ts_drop)
    # depth = 100
    # test_inversion_multiple(ts_drop_regressions_normalized[depth], ts_drop_freq_regressions_normalized[depth],
    #                         x_means_ts_drop[depth], x_stds_ts_drop[depth],
    #                         y_means_ts_drop[depth], y_stds_ts_drop[depth],
    #                         y_means_ts_drop_freq[depth], y_stds_ts_drop_freq[depth])
