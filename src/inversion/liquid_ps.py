import numpy as np
import pandas as pd
import os
from misc_read_and_plot_functions import extract_file_ts
from liquid_sphere import plot_series


def frequency_response(data, delta):
    hz = 1.0 / delta
    N = data.shape[0]
    ft = np.fft.rfft(data, N, axis=0) / N
    k = np.arange(N)
    frq = k * hz / N
    frq = frq[range(N // 2)]
    ft = np.real(ft * np.conj(ft))
    ft = ft[range(N // 2)]
    return frq, ft

def inverse_frequency_response(data, delta_hz):
    dt = 1 / delta_hz
    N = data.shape[0]
    ift = np.fft.irfft(data, N, axis=0) / N
    k = np.arange(N)
    time = k * dt / N
    time = time[range(N // 2)]
    ift = np.real(ift * np.conj(ift))
    ift = ift[range(N // 2)]
    return time, ift

def collection_scattering(scatterer_distances, data):
    average_distance = np.mean(scatterer_distances)

    collection = pd.DataFrame(columns=['freq', 'TS'])
    collection.freq = data.Freq_kHz * 1000

    k_0 = 2 * np.pi * collection.freq / 1500
    combined_scattering = np.zeros(len(data), dtype=np.complex128)
    form_function = data.f_bs
    for scatterer_dist in scatterer_distances:
        combined_scattering += (np.exp(1j*k_0*scatterer_dist) / scatterer_dist) * form_function.values

    collection.TS = 20 * np.log10(average_distance) + 20 * np.log10(np.abs(combined_scattering))

    return collection


def compute_collections():
    ParentDIR=os.path.split(os.getcwd())[0]
    sim_result_30 = 'ts_vs_freq_loop_herring_a_0.039_b_0.0015075567228888182_f1_1_f2_260_rhos_13.52_IncAngle_82_depth_100_length_0.3_iterRef_LU.csv'
    sim_result_10 = r'ts_vs_freq_loop_herring_a_0.013000000000000001_b_0.0015075567228888182_f1_1_f2_260_rhos_13.52_IncAngle_82_depth_100_length_0.1_iterRef_LU.csv'
    freq_resp_file = os.path.join(ParentDIR, r'..\model_results\model_backscatter_results', sim_result_10)
    ps_data = extract_file_ts([freq_resp_file])
    depth = 100

    delta_r = 0.1
    sigma_r = delta_r * 0.2
    n_collection = 5
    collection_ranges = np.linspace(depth, depth + (n_collection - 1) * delta_r, n_collection, endpoint=True)
    collection_ranges = [r + np.random.normal(0, sigma_r) for r in collection_ranges]
    collection_ts = collection_scattering(collection_ranges, ps_data)

    # iFFT of the frequency response
    collection_ts_array = np.asarray(collection_ts.TS)
    time, ifft, = inverse_frequency_response(collection_ts_array, 1000)
    plot_series(time[1:] * 1500, (ifft[1:], 'iFFT'))

    plot_series(ps_data.Freq_kHz * 1000, (ps_data.TS, 'single'), (collection_ts.TS, 'collection'))


if __name__ == '__main__':
    compute_collections()
