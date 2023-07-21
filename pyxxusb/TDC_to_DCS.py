import os
import re
import statistics
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.patches as patches

RADIUS, OFFSET, NUM_POINTS  = 400, 600, 1000
DATA_FILE_PATH = "C:\\Users\\kobyh\\Desktop\\Data\\output_data.dat"
DIRECTORY = r'C:\Users\kobyh\Desktop\Data\Raw Data\Propane'
NAMING_CONVENTION = r'Propane_3um_(\d+)ang_TDC2228A'
PADDING_VALUE = 1

def generate_points_around_circle(radius, num_points, offset):
    angles = np.linspace(0, 360, num_points, endpoint=False)
    return {angle: (radius * np.cos(np.radians(angle)), offset + radius * np.sin(np.radians(angle))) for angle in angles}

def transform_points(points_dict):
    return {(angle, (np.degrees(np.arctan2(x, y)), y * (1 + (x / y) ** 2) ** 0.5)) for angle, (x, y) in points_dict.items() if y != 0 and np.isfinite(x / y)}

def read_data_file(file_path):
    return np.loadtxt(file_path).tolist()

def extract_columns_as_arrays(data):
    return {f"array_{int(column[0])}": column[1:] for column in np.array(data).T}

def get_nearest_y_element(x, y, all_values_array, arrays):
    return next((arrays[f"array_{x_value}"][int(y)] for x_value in range(int(x), -1, -1) if f"array_{x_value}" in arrays and 0 <= (index := int(y)) < len(arrays[f"array_{x_value}"])), 0)

def plot_circular_polar_plot(combined_array, star_values, num_rows, radius, offset):
    angles = np.deg2rad(star_values)
    angles_mesh, rows_mesh = np.meshgrid(angles, -np.arange(num_rows))

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    pcm = ax.pcolormesh(angles_mesh, rows_mesh, combined_array[1:], cmap='viridis', norm=mcolors.LogNorm(), shading='auto')

    # Adding the circle to the plot
    circle = patches.Circle((0, offset), radius=radius, transform=ax.transData._b, edgecolor='red', facecolor='none')
    ax.add_patch(circle)

    ax.set_yticks([])
    ax.set_xticks(angles)
    ax.set_xticklabels(star_values)

    ax.set_xlabel('HWP Angle')
    ax.set_title('VMI Image')

    plt.colorbar(pcm, ax=ax, label='Energy Counts')
    plt.show()

def t2E(time: np.ndarray, count: np.ndarray, L=0.53, t0=53e-9, E_max=400):
    MASS, CHARGE = 9.10938356e-31, 1.60217663e-19
    T = time - t0                  # Get actual time of flight (remove t0 delays)
    ind = T > 0                    # Remove negative and 0 time
    T = T[ind]
    I = count[ind].astype(float)
    V = L / T                      # Time to energy conversion
    E = MASS * V ** 2 / 2 / CHARGE
    Ie = I / E ** (3 / 2)          # Multiply by Jacobian for conversion (I(E) = I(t) * E^(-3/2))
    ind = np.argmax(E < E_max)     # Throw away high energy data just to reduce file size, also flip arrays to make low energy at index 0
    E = np.flip(E[ind:])
    Ie = np.flip(Ie[ind:])
    Ie /= Ie.max()

    return E, Ie

def read_first_2048_lines(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for _, line in zip(range(2048), file)]

def find_matching_files(directory, naming_convention):
    return [file for file in os.listdir(directory) if re.match(naming_convention, file)]

def create_data_array(file_path):
    return read_first_2048_lines(file_path)

def create_time_array():
    return np.arange(0, 2048) * 0.1518e-9

def calculate_spacing(matching_files, naming_convention):
    return [int(re.search(naming_convention, matching_files[i]).group(1)) - int(re.search(naming_convention, matching_files[i - 1]).group(1)) for i in range(1, len(matching_files))]

def create_additional_arrays(max_variable_num, most_common_spacing):
    additional_arrays = []
    for variable_num in range(max_variable_num + most_common_spacing, 91, most_common_spacing):
        data_array_name = f'data_{variable_num}'
        data_array = [PADDING_VALUE] * 2084
        globals()[data_array_name] = data_array
        additional_arrays.append(data_array_name)
    return additional_arrays

def create_identical_arrays(data_arrays):
    new_arrays = set()
    for data_array_name in data_arrays[:]:
        variable_num = int(data_array_name.split('_')[1])
        for num in [180 - variable_num, 180 + variable_num, 360 - variable_num]:
            data_array = globals()[data_array_name]
            globals()[f'data_{num}'] = data_array[:]
            new_arrays.add(f'data_{num}')
    return new_arrays

def main():
    matching_files = sorted(find_matching_files(DIRECTORY, NAMING_CONVENTION))
    file_vars, data_arrays = [], []

    for file_name in matching_files:
        variable_num = int(re.search(NAMING_CONVENTION, file_name).group(1))
        file_var_name, data_array_name = f'file_{variable_num}', f'data_{variable_num}'
        file_path = os.path.join(DIRECTORY, file_name)
        data_array = create_data_array(file_path)
        globals()[file_var_name], time_array = file_path, np.arange(0, 2048 * 0.151e-9, 0.151e-9)
        E, Ie = t2E(time_array, np.array(data_array))
        globals()[data_array_name], file_vars, data_arrays = list(Ie), file_vars + [file_var_name], data_arrays + [data_array_name]

    spacing_array = calculate_spacing(matching_files, NAMING_CONVENTION)
    most_common_spacing = statistics.mode(spacing_array) if spacing_array else None

    max_variable_num = int(re.search(NAMING_CONVENTION, matching_files[-1]).group(1))
    additional_arrays = create_additional_arrays(max_variable_num, most_common_spacing)
    data_arrays.extend(additional_arrays)

    new_arrays = create_identical_arrays(data_arrays)
    data_arrays.extend(sorted(new_arrays, key=lambda x: int(x.split('_')[1])))

    combined_array = np.array(list(zip(*(globals()[data_array_name] for data_array_name in data_arrays))), dtype=float)
    star_values = [int(data_array_name.split('_')[1]) for data_array_name in data_arrays]

    small_value = 1e-6
    combined_array = combined_array + small_value

    num_rows, num_columns = combined_array.shape
    plot_circular_polar_plot(combined_array, star_values, num_rows, RADIUS, OFFSET)

    star_values_row = np.array(star_values)
    combined_array_with_header = np.vstack((star_values_row, combined_array))
    combined_array_with_header = combined_array_with_header + small_value

    num_rows, num_columns = combined_array_with_header.shape
    np.savetxt(DATA_FILE_PATH, combined_array_with_header, fmt='%f', delimiter='\t')

    points_dict_circle = generate_points_around_circle(RADIUS, NUM_POINTS, OFFSET)
    points_dict_transformed = transform_points(points_dict_circle)

    data = read_data_file(DATA_FILE_PATH)
    arrays = extract_columns_as_arrays(data)
    all_values_array = sorted({int(key.split("_")[1]) for key in arrays if key.startswith("array_")})

    points_with_nearest_y = [(point_angle, get_nearest_y_element(abs(x), y, all_values_array, arrays)) for point_angle, (x, y) in points_dict_transformed]

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
