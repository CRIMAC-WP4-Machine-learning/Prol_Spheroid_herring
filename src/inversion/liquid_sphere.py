import numpy as np
from scipy.special import spherical_jn, spherical_yn, legendre

import matplotlib.pyplot as plt
import matplotlib


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


def coeff_liquid_sphere(n, z):
    return z * spherical_jn(n ,z, True) / spherical_jn(n, z)


def far_field_pattern_liquid_sphere(rho_0, rho_1, k_0, k_1, r, thetas, num_terms, theta_inc):
    rho_10 = rho_1 / rho_0
    pattern = np.zeros((len(thetas)), dtype=np.complex128)
    g = 1 / rho_10
    x_0 = k_0 * r
    x_1 = k_1 * r
    for k, theta in enumerate(thetas):
        accumulator = 0
        for n in range(num_terms):
            coeff = coeff_liquid_sphere(n, x_1)
            c = (-(spherical_jn(n, x_0) * g * coeff - x_0 * spherical_jn(n, x_0, True))
                 / (spherical_yn(n, x_0) * g * coeff - x_0 * spherical_yn(n, x_0, True)))
            accumulator += ((-1)**n * (2 * n + 1) * ((c - 1j * c * c) / (1 + c * c))
                            * legendre(n)(np.cos( -theta + theta_inc + np.pi)))
        pattern[k] = -(1 / k_0) * accumulator

    return pattern

def plot_far_field(thetas, values, theta_inc):
    matplotlib.use('TkAgg')
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location('N')
    ax.plot(thetas, values)
    pattern_max = np.max(values)
    arrow_length = pattern_max * 0.3
    ax.arrow(x=theta_inc + np.pi, y=pattern_max * 0.9, dx=0, dy =-arrow_length, width=0.01,
             head_length=arrow_length * 0.1, length_includes_head=True, color='k')
    ax.set_xticks(np.pi/180. * np.linspace(0,  360, 12, endpoint=False))
    plt.show()

def plot_series(x_data, *values):
    matplotlib.use('TkAgg')
    fig, ax = plt.subplots()
    for v, name in values:
        ax.plot(x_data, v, label=name)
    ax.grid(True)
    ax.legend()
    plt.show()

def main():
    num_angles = 360
    rho_w = 1027
    rho_s = rho_w * 1.05
    c_w = 1500
    c_s = 1500 * 1.05
    f = 15200
    k_0 = 2 * np.pi * f / c_w
    k_1 = 2 * np.pi * f / c_s
    r = 0.1

    theta_inc = np.pi / 2
    thetas = np.linspace(0, 2 * np.pi, num_angles)
    #thetas = [theta_inc + np.pi]
    num_terms = 10
    form_function = far_field_pattern_liquid_sphere(rho_w, rho_s, k_0, k_1, r, thetas, num_terms, theta_inc)
    #print('ff = {}'.format(np.abs(form_function[0])))

    plot_far_field(thetas, np.abs(form_function), theta_inc)

def main_2():
    num_angles = 360
    rho_w = 1027
    rho_s = rho_w * 3.0
    #rho_s = rho_w
    k_0 = 5
    k_1 = 3
    #k_1 = k_0
    r = 1.0

    theta_inc = np.pi / 2
    #thetas = np.linspace(theta_inc + np.pi - 0.5 * np.pi, theta_inc + np.pi + 0.5 * np.pi, 100)
    thetas = np.linspace(0, 2 * np.pi, num_angles)
    num_terms = 10
    form_function = far_field_pattern_liquid_sphere(rho_w, rho_s, k_0, k_1, r, thetas, num_terms, theta_inc)

    plot_far_field(thetas, np.abs(form_function), theta_inc)


def collection_scattering(scatterer_distances, frequencies, rho_w, rho_s, c_w, c_s, r):
    average_distance = np.mean(scatterer_distances)
    collection_ts = []
    for f in frequencies:
        k_0 = 2 * np.pi * f / c_w
        k_1 = 2 * np.pi * f / c_s

        theta_inc = np.pi / 2
        thetas = [theta_inc + np.pi]
        num_terms = 10
        combined_scattering = 0
        for scatterer_dist in scatterer_distances:
            form_function = far_field_pattern_liquid_sphere(rho_w, rho_s, k_0, k_1, r, thetas, num_terms, theta_inc)[0]
            combined_scattering += (np.exp(1j*k_0*scatterer_dist) / scatterer_dist) * form_function

        collection_ts.append(20 * np.log10(average_distance) + 20 * np.log10(np.abs(combined_scattering)))

    return collection_ts

def compute_collections():
    rho_w = 1027
    #rho_s = rho_w * 1.05
    depth = 100
    P_pa = 1e5 + rho_w*depth*9.81
    rho_s = func_VanDerWaals_Air(P_pa, 15)

    c_w = 1500
    c_s = 0.23 * c_w
    #c_s = 1500 * 1.05
    r = 0.01 * 0.5
    frequencies = np.linspace(100, 360000, 3599, True)

    single_scatterer_ts = collection_scattering([depth], frequencies, rho_w, rho_s, c_w, c_s, r)
    delta_r = r * 2
    # collection_ts = collection_scattering([100, 100+delta_r, 100 + 2 * delta_r,
    #                                        100 + 3 * delta_r, 100 + 4 * delta_r, 100 + 5 * delta_r, 100 + 6 * delta_r], frequencies, rho_w, rho_s, c_w, c_s, r)
    n_collection = 2
    sigma_r = delta_r * 0.0
    collection_ranges = np.linspace(depth, depth + (n_collection - 1) * delta_r, n_collection, endpoint=True)
    collection_ranges = [r + np.random.normal(0, sigma_r) for r in collection_ranges]
    collection_ts = collection_scattering(collection_ranges, frequencies, rho_w, rho_s, c_w, c_s, r)

    plot_series(frequencies, (single_scatterer_ts, 'single'), (collection_ts, 'collection'))


if __name__ == '__main__':
    #main()
    #main_2()
    compute_collections()