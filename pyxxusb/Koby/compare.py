import tkinter as tk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import os

file_list = []

def add_plot():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        data = np.loadtxt(file_path)
        x = data[:, 0]
        y = np.log(data[:, 1])
        
        file_name = os.path.split(os.path.dirname(file_path))[-1]
        plt.plot(x, y, label=file_name)
        plt.legend()
        canvas.draw()
        
        file_list.append(file_name)
        listbox.insert(tk.END, file_name)

def remove_selected():
    selected_index = listbox.curselection()
    if selected_index:
        file_name = listbox.get(selected_index)
        listbox.delete(selected_index)
        file_list.remove(file_name)
        
        ax = plt.gca()
        lines = ax.lines
        for line in lines:
            if line.get_label() == file_name:
                line.remove()
        
        plt.legend()
        canvas.draw()

def update_plot():
    for file_name in file_list:
        file_path = os.path.join(os.getcwd(), file_name, "data.txt")
        if os.path.exists(file_path):
            data = np.loadtxt(file_path)
            x = data[:, 0]
            y = np.log(data[:, 1])
            
            ax = plt.gca()
            lines = ax.lines
            for line in lines:
                if line.get_label() == file_name:
                    line.set_data(x, y)
            
            # Update plot limits
            ax.relim()
            ax.autoscale_view(True, True, True)
            
            canvas.draw()

    root.after(3000, update_plot)  # Update plot every 3 seconds

root = tk.Tk()
root.title("Data Plotter")

figure = plt.figure(figsize=(6, 4), dpi=100)
canvas = FigureCanvasTkAgg(figure, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
canvas.draw()

button = tk.Button(root, text="data.txt File Path", command=add_plot)
button.pack()

listbox = tk.Listbox(root, height=5)
listbox.pack(side=tk.LEFT, padx=10, pady=10)

remove_button = tk.Button(root, text="Remove", command=remove_selected)
remove_button.pack(side=tk.LEFT, padx=10)

root.after(3000, update_plot)  # Start updating plot after 3 seconds

root.mainloop()
