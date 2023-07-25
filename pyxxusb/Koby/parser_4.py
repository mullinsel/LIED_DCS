import glob
import time
import os
import statistics
import re
import numpy as np

# Default configuration
DEFAULT_DIRECTORY = r"C:\Users\kobyh\Desktop\Dummy_Data"
DEFAULT_NAMING_CONVENTION = "CH4_3um_*ang_TDC2228A.dat"
DEFAULT_DATA_FILE = "data.txt"
MASS = 9.1093837015 * 10**-31  # electon mass
CHARGE = 1.602176634 * 10**-19  # electron charge
TIME_BIN_SIZE = 0.151e-9

# Configuration file path
CONFIG_FILE_PATH = "C:/Users/kobyh/Desktop/data_directory.txt" #<-- SHOULD MATCH CONFIG_FILE_PATH IN plotter_3.py

# Analysis parameters
NUMBER_OF_TIME_BINS = 2048
DELAY_TIME = 3
ERROR_THRESHOLD = 1

def t2E(time, count, L=0.53, t0=1.92e-8, E_max=400):
    T = np.array(time) - t0  # Convert time to numpy array

    # remove negative and 0 time
    ind = T > 0
    T = T[ind]
    I = np.array(count)[ind]  # Convert count to numpy array, keep only positive times

    # time to energy conversion
    V = L / T  # velocity in m/s
    E = MASS * V**2 / 2  # energy bins in Joules
    E = E / CHARGE  # energy bins in eV

    # multiply by jacobian for conversion (I(E) = I(t)*E^(-3/2))
    # constants were thrown away since we only care about relative yields
    Ie = I / E**(3 / 2)

    # throw away high energy data just to reduce file size, also flip arrays to make low energy at index 0
    ind = np.argmax(E < E_max)
    E = np.flip(E[ind:])
    Ie = np.flip(Ie[ind:])
    Ie = Ie / Ie.max()
    return E, Ie

# Function to read the data directory and naming convention from the configuration file
def read_data_directory():
    if os.path.isfile(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'r') as file:
            contents = file.read().strip().split('\n')[0]
            if '\t' in contents:
                directory, naming_convention = contents.split('\t')
                return directory, naming_convention
            else:
                print("Incorrect file format. Expected format: directory\tnaming_convention")
    return DEFAULT_DIRECTORY, DEFAULT_NAMING_CONVENTION

# Function to extract the ang value from the file name using a given naming convention
def extract_ang_from_file_name(file_name, naming_convention):
    pattern = re.escape(naming_convention).replace(r'\*', r'(.*)')
    match = re.search(pattern, file_name)
    if match:
        ang = match.group(1)
        return ang
    else:
        return None

# Function to calculate the cross section, standard error, and threshold indicator
def calculate_statistics(data):
    time = np.arange(NUMBER_OF_TIME_BINS)*TIME_BIN_SIZE  # Time array generation
    E, Ie = t2E(time, data)  # Convert time to energy using t2E function

    cross_section = sum(Ie)
    standard_error = statistics.stdev(Ie) / (NUMBER_OF_TIME_BINS ** 0.5)
    if standard_error >= ERROR_THRESHOLD or standard_error == 0:
        threshold_indicator = 1
    elif 0 < standard_error < ERROR_THRESHOLD:
        threshold_indicator = 0
    return cross_section, standard_error, threshold_indicator


# Function to process the files in the given directory with the specified naming convention
def process_files(directory_path, file_pattern):
    cross_sections = {}
    file_paths = glob.glob(os.path.join(directory_path, file_pattern))
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        ang = extract_ang_from_file_name(file_name, file_pattern)
        if ang is not None:
            variable_name = f"data_{ang}"
            with open(file_path, "r") as file:
                lines = file.readlines()
                data = [float(line.strip()) for line in lines[:NUMBER_OF_TIME_BINS]]
            cross_section, standard_error, threshold_indicator = calculate_statistics(data)
            cross_sections[ang] = (cross_section, standard_error, threshold_indicator)
            locals()[variable_name] = data
    return cross_sections

# Function to write the cross section, standard error, and threshold indicator data to a file
def write_data_to_file(file_path, cross_sections):
    try:
        with open(file_path, "w") as data_file:
            sorted_angles = sorted(cross_sections.keys(), key=float)
            for angle in sorted_angles:
                cross_section, standard_error, threshold_indicator = cross_sections[angle]
                data_file.write(f"{angle} {cross_section} {standard_error} {threshold_indicator}\n")
    except FileNotFoundError as e:
        print(f"Failed to write data to {file_path}: {e}")

# Main execution loop
def main():
    directory_path, file_pattern = read_data_directory()
    running = True
    while running:
        try:
            cross_sections = process_files(directory_path, file_pattern)
            data_file_path = os.path.join(directory_path, DEFAULT_DATA_FILE)
            if os.path.isfile(data_file_path):
                os.remove(data_file_path)
            write_data_to_file(data_file_path, cross_sections)
            time.sleep(DELAY_TIME)
            new_directory_path, new_file_pattern = read_data_directory()
            if directory_path != new_directory_path or file_pattern != new_file_pattern:
                directory_path = new_directory_path
                file_pattern = new_file_pattern
                print(f"Updated directory path: {directory_path}")
                print(f"Updated file pattern: {file_pattern}")
        except KeyboardInterrupt:
            running = False

if __name__ == "__main__":
    main()
