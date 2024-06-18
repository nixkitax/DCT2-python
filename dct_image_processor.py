#TODO: Dividere in moduli, testare scaling algoritmo

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageOps, ImageTk
import numpy as np
import time
import matplotlib.pyplot as plt
import os
from scipy.fftpack import dct, idct
import threading
import queue

normalize_coefficients = False

def dct2_manual(matrix):
    N = matrix.shape[0]
    result = np.zeros_like(matrix, dtype=np.float32)
    for u in range(N):
        for v in range(N):
            sum_val = 0
            for x in range(N):
                for y in range(N):
                    sum_val += matrix[x, y] * np.cos(np.pi * u * (2 * x + 1) / (2 * N)) * np.cos(np.pi * v * (2 * y + 1) / (2 * N))
            alpha_u = np.sqrt(1/N) if u == 0 else np.sqrt(2/N)
            alpha_v = np.sqrt(1/N) if v == 0 else np.sqrt(2/N)
            result[u, v] = alpha_u * alpha_v * sum_val
    return result



def idct2_manual(matrix):
    N = matrix.shape[0]
    result = np.zeros_like(matrix, dtype=np.float32)
    for x in range(N):
        for y in range(N):
            sum_val = 0
            for u in range(N):
                for v in range(N):
                    alpha_u = np.sqrt(1/N) if u == 0 else np.sqrt(2/N)
                    alpha_v = np.sqrt(1/N) if v == 0 else np.sqrt(2/N)
                    sum_val += alpha_u * alpha_v * matrix[u, v] * np.cos(np.pi * u * (2 * x + 1) / (2 * N)) * np.cos(np.pi * v * (2 * y + 1) / (2 * N))
            result[x, y] = sum_val
    return result

def dct2(matrix):
    return dct(dct(matrix.T, norm='ortho').T, norm='ortho')

def idct2(matrix):
    return idct(idct(matrix.T, norm='ortho').T, norm='ortho')

def compare_dct2_algorithms(progress_queue, plot_queue):
    sizes = [8, 16, 32, 64]
    manual_times = []
    library_times = []

    total_steps = len(sizes) * 2
    step = 0
    
    for size in sizes:
        print("size: ", size)
        matrix = np.random.rand(size, size).astype(np.float32)
        
        start_time = time.time()
        dct2_manual(matrix)
        manual_times.append(time.time() - start_time)
        step += 1
        progress_queue.put((step / total_steps) * 100)
        
        start_time = time.time()
        dct2(matrix)
        library_times.append(time.time() - start_time)
        step += 1
        progress_queue.put((step / total_steps) * 100)
    
    progress_queue.put("done")
    plot_queue.put((sizes, manual_times, library_times))

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

def process_image(file_path, F, d):
    try:
        img = Image.open(file_path).convert('L')
    except Exception as e:
        print(f"Error in opening image: {e}")
        return ""

    gray_img = ImageOps.grayscale(img)
    matrix = image_to_matrix(gray_img)

    compressed_matrix = apply_dct_and_idct(matrix, F, d)

    compressed_img = matrix_to_image(compressed_matrix)
    compressed_file_path = "compressed_image.png"
    compressed_img.save(compressed_file_path)

    return compressed_file_path

def image_to_matrix(img):
    return np.array(img, dtype=np.float32)

def matrix_to_image(matrix):
    min_val, max_val = matrix.min(), matrix.max()
    normalized_matrix = 255 * (matrix - min_val) / (max_val - min_val)
    return Image.fromarray(np.uint8(normalized_matrix))

def apply_dct_and_idct(matrix, F, d):
    height, width = matrix.shape
    compressed_matrix = np.zeros_like(matrix)

    for y in range(0, height, F):
        for x in range(0, width, F):
            if y + F <= height and x + F <= width:
                block = matrix[y:y+F, x:x+F]
                dct_block = dct2(block)
                filtered_dct_block = filter_frequencies(dct_block, d)
                idct_block = idct2(filtered_dct_block) 
                compressed_matrix[y:y+F, x:x+F] = idct_block

    return compressed_matrix

def filter_frequencies(matrix, d):
    size = matrix.shape[0]
    for k in range(size):
        for l in range(size):
            if k + l >= d:
                matrix[k, l] = 0
    return matrix

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

def resize_image(image, max_width, max_height):
    width, height = image.size
    if width > max_width or height > max_height:
        ratio = min(max_width / width, max_height / height)
        new_size = (int(width * ratio), int(height * ratio))
        image = image.resize(new_size)
    return image

def toggle_normalize():
    global normalize_coefficients
    normalize_coefficients = not normalize_coefficients
    print("normalize_coefficients set to", normalize_coefficients)

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
