import os
import glob
import time
import signal
import re
import sys
import shutil

#This code takes files from the source_folder which match a certain naming convention
#and uses them to populate a destination folder at some set rate in order to simulate
#data coming in in real time

#This version initializes all the files by immediately creating a "blank" file for each
#file matching the naming convention in the source folder. Over time, these blank files
#get overwritten by real data. By blank, I mean the files initially contain 2048 
#rows of 0 before being replaced by actual data.

source_folder = r"C:\Users\kobyh\Desktop\Data\Raw Data\Methane"
destination_folder = r"C:\Users\kobyh\Desktop\Dummy_Data"  #WARNING: ALL CONTENTS OF DESTINATION_FOLDER WILL BE CLEARED UPON EXITING
input_rate = 3

pattern = os.path.join(source_folder, "CH4_3um_*ang_TDC2228A.dat")
file_list = sorted(glob.glob(pattern), key=lambda x: int(re.search(r"\d+", x).group()))

def exit_handler(signal, frame):
    print("\nExiting...")
    clear_dummy_data()
    sys.exit(0)

def clear_dummy_data():
    print("Clearing Destination Folder...")
    file_paths = glob.glob(os.path.join(destination_folder, "*"))
    for file_path in file_paths:
        os.remove(file_path)

signal.signal(signal.SIGINT, exit_handler)

os.makedirs(destination_folder, exist_ok=True)

# Create empty files at the beginning
for file_path in file_list:
    destination_path = os.path.join(destination_folder, os.path.basename(file_path))
    with open(destination_path, 'w') as f:
        for _ in range(2048):
            f.write("0\n")

try:
    for file_path in file_list:
        destination_path = os.path.join(destination_folder, os.path.basename(file_path))
        shutil.copy2(file_path, destination_path)
        print(f"Copied file: {destination_path}")
        time.sleep(input_rate)

    print("All files have been copied. Press Ctrl+C to exit.")
    while True:
        pass

except KeyboardInterrupt:
    clear_dummy_data()
    print("\nKeyboardInterrupt detected. Exiting...")
    sys.exit(0)
