import tkinter as tk
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import os
import subprocess

CONFIG_FILE_PATH = "C:/Users/kobyh/Desktop/data_directory.txt"  # <-- Should match CONFIG_FILE_PATH in parser_3.py
DEFAULT_DIRECTORY = r"C:\Users\kobyh\Desktop\Data\Raw Data\Ethane"
DEFAULT_NAMING_CONVENTION = "Ethan_3um_*ang_TDC2228A.dat"
PARSER_PATH = r"C:\Users\kobyh\Desktop\parser_4.py"
COMPARE_PATH = r"C:\Users\kobyh\Desktop\compare.py"  # <-- Change this path accordingly

# Global variables
parser_process = None
script_running = False

def read_data(file_path):
    with open(file_path, 'r') as file:
        data = [line.strip().split() for line in file]
    return data

def update_plot(i, ax, canvas):
    try:
        file_path = os.path.join(data_directory.get(), "data.txt")
        data = read_data(file_path)
        angles, cross_sections, errors, colors = [], [], [], []

        for angle, cross_section, error, color in data:
            if float(cross_section) != 0:
                angles.append(float(angle))
                cross_sections.append(float(cross_section))
                errors.append(float(error))
                colors.append('red' if int(color) == 1 else 'blue')

        ax.clear()
        ax.plot(angles, cross_sections, '.-', color='blue')
        ax.plot([angles[i] for i, c in enumerate(colors) if c == 'red'],
                [cross_sections[i] for i, c in enumerate(colors) if c == 'red'],
                '.-', color='red')

        ax.errorbar(angles, cross_sections, yerr=errors, fmt='none', color='black', capsize=3)

        ax.set_xlabel('Angle')
        ax.set_ylabel('Cross Section (Log Scale)')
        ax.set_title('Laser Electron Diffraction Experiment')
        ax.set_yscale('log')

        canvas.draw()

    except IOError as e:
        print(f"Failed to access data.txt: {e}. Skipping plot update.")


def update_data_directory(event=None):
    input_directory = data_directory_entry.get().strip()
    if input_directory.startswith('"') and input_directory.endswith('"'):
        input_directory = input_directory[1:-1]
    data_directory.set(input_directory)
    save_data_directory()


def browse_directory():
    selected_directory = filedialog.askdirectory()
    if selected_directory:
        data_directory_entry.delete(0, tk.END)
        data_directory_entry.insert(tk.END, selected_directory)
        update_data_directory()


def save_data_directory():
    directory = data_directory.get()
    naming_convention = naming_convention_entry.get()
    with open(CONFIG_FILE_PATH, 'w') as file:
        file.write(f"{directory}\t{naming_convention}")


def cleanup():
    if os.path.exists(CONFIG_FILE_PATH):
        os.remove(CONFIG_FILE_PATH)
    # Terminate the parser process if running
    if parser_process and parser_process.poll() is None:
        parser_process.terminate()


def create_initial_directory_file():
    if not os.path.isfile(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, 'w') as file:
                file.write(f"{DEFAULT_DIRECTORY}\t{DEFAULT_NAMING_CONVENTION}")
        except IOError as e:
            print(f"Failed to create data_directory.txt: {e}")


def create_gui():
    root = tk.Tk()
    root.title("Real-Time Data Plot")

    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    data_directory_frame = tk.Frame(root)
    data_directory_frame.pack(side=tk.TOP, pady=10)
    data_directory_label = tk.Label(data_directory_frame, text="Data Directory:")
    data_directory_label.pack(side=tk.LEFT)
    data_directory_entry = tk.Entry(data_directory_frame, width=50)
    data_directory_entry.pack(side=tk.LEFT)
    data_directory_button = tk.Button(data_directory_frame, text="Browse", command=browse_directory)
    data_directory_button.pack(side=tk.LEFT)
    data_directory_button = tk.Button(data_directory_frame, text="Update", command=update_data_directory)
    data_directory_button.pack(side=tk.LEFT)

    naming_convention_frame = tk.Frame(root)
    naming_convention_frame.pack(side=tk.TOP, pady=10)
    naming_convention_label = tk.Label(naming_convention_frame, text="Naming Convention:")
    naming_convention_label.pack(side=tk.LEFT)
    naming_convention_entry = tk.Entry(naming_convention_frame, width=50)
    naming_convention_entry.pack(side=tk.LEFT)
    naming_convention_entry.insert(tk.END, DEFAULT_NAMING_CONVENTION)

    data_directory = tk.StringVar()
    data_directory_entry.insert(tk.END, DEFAULT_DIRECTORY)
    data_directory.set(data_directory_entry.get())

    disclaimer_label = tk.Label(root, fg="red")
    disclaimer_label.pack(side=tk.TOP, pady=5)
    disclaimer_label.config(text="")  # Add this line to initialize the label with an empty text

    ani = animation.FuncAnimation(fig, update_plot, fargs=(ax, canvas), interval=3000)

    def toggle_script():
        global parser_process, script_running
        if script_running:
            # Terminate the parser process
            if parser_process and parser_process.poll() is None:
                parser_process.terminate()
            run_button.config(state=tk.NORMAL)
            stop_button.config(state=tk.DISABLED)
            script_running = False
        else:
            if parser_process and parser_process.poll() is None:
                print("Parser script is already running.")
                return
            if not os.path.exists(PARSER_PATH):
                disclaimer_label.config(text="Parser path not found! Edit PARSER_PATH")
                return
            disclaimer_label.config(text="")
            parser_process = subprocess.Popen(["python", PARSER_PATH])
            run_button.config(state=tk.DISABLED)
            stop_button.config(state=tk.NORMAL)
            script_running = True

            if not os.path.exists(CONFIG_FILE_PATH):
                error_message = "Parser launched successfully, but CONFIG_FILE_PATH wasn't found.\n" \
                                "Edit CONFIG_FILE_PATH in plotter.py and parser.py so that they match\n" \
                                "and are compatible with your device"
                disclaimer_label.config(text=error_message)

    def compare_script():
        if not os.path.exists(COMPARE_PATH):
            disclaimer_label.config(text="Compare path not found! Edit COMPARE_PATH", fg="red")
            return
        disclaimer_label.config(text="", fg="black")
        subprocess.Popen(["python", COMPARE_PATH])

    def handle_enter(event):
        update_data_directory()

    button_frame = tk.Frame(root)
    button_frame.pack(side=tk.TOP, pady=10)

    run_button = tk.Button(button_frame, text="Run Parser", command=toggle_script)
    run_button.pack(side=tk.LEFT, padx=(10, 5))

    stop_button = tk.Button(button_frame, text="Kill Parser", command=toggle_script)
    stop_button.pack(side=tk.LEFT, padx=(5, 10))
    stop_button.config(state=tk.DISABLED)

    compare_button = tk.Button(button_frame, text="Compare", command=compare_script)
    compare_button.pack(side=tk.LEFT, padx=(10, 5))

    disclaimer_label = tk.Label(root, fg="red")
    disclaimer_label.pack(side=tk.TOP, pady=5)

    data_directory_entry.bind("<Return>", handle_enter)
    naming_convention_entry.bind("<Return>", handle_enter)

    return root, canvas, data_directory, data_directory_entry, naming_convention_entry, ax, ani


def start_gui_event_loop(root):
    try:
        root.mainloop()
    except KeyboardInterrupt:
        plt.close('all')  # Close all plot windows
        root.destroy()  # Destroy the tkinter window
    finally:
        cleanup()


if __name__ == "__main__":
    create_initial_directory_file()
    root, canvas, data_directory, data_directory_entry, naming_convention_entry, ax, ani = create_gui()
    start_gui_event_loop(root)
