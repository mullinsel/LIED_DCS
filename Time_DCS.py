import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as patches
from collections import namedtuple
import numpy as np
import fnmatch
import os

RADIUS, OFFSET, NUM_POINTS  = 600, 1200, 1000
DIRECTORY = r"C:\Users\kobyh\Desktop\Data\Raw Data\Methane"
NAMING_CONVENTION = "CH4_3um_*ang_TDC2228A.dat"
PADDING_VALUE = 1
SIGMA_T = 1
SIGMA_A = 1

def raw_data_to_table(DIRECTORY, NAMING_CONVENTION):
    DataTuple = namedtuple("DataTuple", ["num", "data"])
    file_list = [file for file in os.listdir(DIRECTORY) if fnmatch.fnmatch(file, NAMING_CONVENTION)]
    tuples = [
        DataTuple(num=float(file.split("_")[2].replace("ang", "")),
                  data=np.genfromtxt(os.path.join(DIRECTORY, file), max_rows=2048))
        for file in file_list
    ]

    difference_array = np.diff([t.num for t in tuples])
    spacing = np.round(np.median(difference_array))
    max_num = max(t.num for t in tuples)
    max_value = 90
    num_list = sorted([t.num for t in tuples] + [max_num + i * spacing for i in range(100) if max_num + i * spacing <= max_value])

    missing_nums = [num for num in num_list if num not in [t.num for t in tuples]]
    tuples += [DataTuple(num=i, data=np.ones(2048) * PADDING_VALUE) for i in missing_nums]
    tuples += [DataTuple(num=360 - t.num, data=t.data) for t in tuples if t.num in num_list]
    tuples += [DataTuple(num=180 - t.num, data=t.data) for t in tuples if t.num in num_list]
    tuples += [DataTuple(num=180 + t.num, data=t.data) for t in tuples if t.num in num_list and t.num != 0]

    tuples.sort(key=lambda t: t.num)
    table = (np.array([t.data for t in tuples])).T + 1e-6
    star_values = [t.num for t in tuples]
    arrays = {f"array_{int(t.num)}": t.data for t in tuples}

    return tuples, table, star_values, arrays

def plot_circular_polar_plot(combined_array, star_values, num_rows, radius, offset):
    angles = np.deg2rad(star_values)
    angles_mesh, rows_mesh = np.meshgrid(angles, -np.arange(num_rows))
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    pcm = ax.pcolormesh(angles_mesh, rows_mesh, combined_array, cmap='viridis', norm=mcolors.LogNorm(), shading='auto')
    circle = patches.Circle((0, offset), radius=radius, transform=ax.transData._b, edgecolor='red', facecolor='none')
    ax.add_patch(circle)
    ax.set_yticks([])
    ax.set_xticks(angles)
    ax.set_xticklabels(star_values)
    ax.set_xlabel('HWP Angle')
    ax.set_title('VMI Image')
    plt.colorbar(pcm, ax=ax, label='Energy Counts')
    plt.show()

def generate_and_transform_points(radius, num_points, offset):
    angles = np.linspace(0, 360, num_points, endpoint=False)
    points_dict = {angle: (radius * np.cos(np.radians(angle)), offset + radius * np.sin(np.radians(angle))) for angle in angles}
    transformed_points = [(angle, (np.degrees(np.arctan2(x, abs(y))), abs(y) * (1 + (x / abs(y)) ** 2) ** 0.5)) for angle, (x, y) in points_dict.items() if x != 0 and y != 0]
    return transformed_points

def gaussian_weight_2d(E, theta, E_i, A_j, SIGMA_T, SIGMA_A):
    return np.exp(
        -((E_i - E) ** 2 / (2 * SIGMA_T ** 2)) - ((A_j - theta) ** 2 / (2 * SIGMA_A ** 2))
    )

def get_DCS(x, y, all_values_array, arrays, points_dict_transformed, SIGMA_T, SIGMA_A):
    if SIGMA_T == 1 and SIGMA_A == 1:
        x_value, y_value = x, y
        return next((arrays[f"array_{x_value}"][int(y_value)] for x_value in range(int(x_value), -1, -1) if f"array_{x_value}" in arrays and 0 <= (index := int(y_value)) < len(arrays[f"array_{x_value}"])), 0)
    weighted_sum = 0
    total_weight = 0
    for point_angle, (x_value, y_value) in points_dict_transformed:
        angle_weight = gaussian_weight_2d(x, y, x_value, y_value, SIGMA_T, SIGMA_A)
        y_nearest = get_DCS(x_value, y_value, all_values_array, arrays, points_dict_transformed, 1, 1)
        weighted_sum += angle_weight * y_nearest
        total_weight += angle_weight
    if total_weight > 0:
        return weighted_sum / total_weight
    return 0

def main():
    tuples, table, star_values, arrays = raw_data_to_table(DIRECTORY, NAMING_CONVENTION)
    num_rows, num_columns = table.shape
    plot_circular_polar_plot(table, star_values, num_rows, RADIUS, OFFSET)

    transformed_points = generate_and_transform_points(RADIUS, NUM_POINTS, OFFSET)
    all_values_array = sorted({int(key.split("_")[1]) for key in arrays if key.startswith("array_")})
    points_with_nearest_y = [(point_angle, get_DCS(abs(x), y, all_values_array, arrays, transformed_points, SIGMA_T, SIGMA_A)) for point_angle, (x, y) in transformed_points]

    points_with_nearest_y.sort(key=lambda tup: tup[0])
    x_values, y_values = zip(*points_with_nearest_y)

    plt.plot(x_values, y_values)
    plt.xlabel('Scattering ')
    plt.ylabel('DCS')
    plt.title('DCS')
    plt.yscale('log')
    plt.show()

if __name__ == "__main__":
    main()