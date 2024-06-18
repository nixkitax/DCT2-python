import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from image_processing_module import process_image, resize_image
import threading
import queue
import matplotlib.pyplot as plt
from dct_module import compare_dct2_algorithms

def load_image():
    file_path = filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp")])
    if not file_path:
        return

    file_label.config(text=file_path)
    original_image = Image.open(file_path)
    resized_original_image = resize_image(original_image, 400, 400)
    original_photo = ImageTk.PhotoImage(resized_original_image)
    img_label.config(image=original_photo)
    img_label.image = original_photo

    try:
        F = int(f_entry.get() or 10)
        d = int(d_entry.get() or 7)
    except ValueError:
        messagebox.showerror("Error", "Invalid F or d value")
        return

    original_size = os.path.getsize(file_path)
    compressed_file_path = process_image(file_path, F, d)
    if compressed_file_path:
        compressed_size = os.path.getsize(compressed_file_path)
        compression_ratio = 100 * (original_size - compressed_size) / original_size
        compression_label.config(text=f"Dimensione originale: {original_size} bytes\n"
                                      f"Dimensione compressa: {compressed_size} bytes\n"
                                      f"Compressione: {compression_ratio:.2f}%")

        compressed_image = Image.open(compressed_file_path)
        resized_compressed_image = resize_image(compressed_image, 400, 400)
        compressed_photo = ImageTk.PhotoImage(resized_compressed_image)
        compressed_img_label.config(image=compressed_photo)
        compressed_img_label.image = compressed_photo

def toggle_normalize():
    global normalize_coefficients
    normalize_coefficients = not normalize_coefficients
    print("normalize_coefficients set to", normalize_coefficients)

def compare_dct2_algorithms_thread(progress_var, progress_bar):
    progress_queue = queue.Queue()
    plot_queue = queue.Queue()
    threading.Thread(target=compare_dct2_algorithms, args=(progress_queue, plot_queue)).start()
    root.after(100, check_progress, progress_queue, progress_var, progress_bar)
    root.after(100, check_plot, plot_queue)

def check_progress(progress_queue, progress_var, progress_bar):
    try:
        progress = progress_queue.get_nowait()
        if progress == "done":
            return
        progress_var.set(progress)
        progress_bar.update_idletasks()
    except queue.Empty:
        pass
    root.after(100, check_progress, progress_queue, progress_var, progress_bar)

def check_plot(plot_queue):
    try:
        plot_data = plot_queue.get_nowait()
        sizes, manual_times, library_times = plot_data
        
        plt.figure()
        plt.plot(sizes, manual_times, label='Manual DCT2 ', marker='o')
        plt.plot(sizes, library_times, label='Library DCT2', marker='o')
        plt.xlabel('Matrix size (N)')
        plt.ylabel('Time (s)')
        plt.yscale('log')
        plt.legend()
        plt.title('Comparison of DCT2 Algorithms')
        plt.show()
    except queue.Empty:
        root.after(100, check_plot, plot_queue)

root = tk.Tk()
root.title("Compressione di immagini tramite la DCT")

root.geometry("800x600")

# Menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Create a Notebook
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# Create frames for each tab
dct_frame = ttk.Frame(notebook)
hello_frame = ttk.Frame(notebook)

notebook.add(dct_frame, text="DCT")
notebook.add(hello_frame, text=("Comp"))

f_entry = tk.Entry(dct_frame)
f_entry.insert(0, "10")
d_entry = tk.Entry(dct_frame)
d_entry.insert(0, "7")

normalize_button = tk.Checkbutton(dct_frame, text="“Normalizzare coefficenti DTC”", command=toggle_normalize)
load_button = tk.Button(dct_frame, text="“Load .bmp image”", command=load_image)
file_label = tk.Label(dct_frame, text="“Nessun file selezionato”")
compression_label = tk.Label(dct_frame, text="””")

image_frame = tk.Frame(dct_frame)
image_frame.pack()

img_label = tk.Label(image_frame)
compressed_img_label = tk.Label(image_frame)
f_entry.pack()
d_entry.pack()
normalize_button.pack()
load_button.pack()
file_label.pack()
compression_label.pack()
img_label.pack(side=tk.LEFT)
compressed_img_label.pack(side=tk.LEFT)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(hello_frame, variable=progress_var, maximum=100)
progress_bar.pack(pady=10)

compare_button = tk.Button(hello_frame, text="“Compare DCT2 Algorithms”", command=lambda: compare_dct2_algorithms_thread(progress_var, progress_bar))
compare_button.pack()

root.mainloop()
