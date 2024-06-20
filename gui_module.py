import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import numpy as np
from scipy.fftpack import dct
from image_processing_module import process_image, resize_image
import threading
import queue
import matplotlib.pyplot as plt
from dct_module import compare_dct2_algorithms, dct2_manual

def load_image():
    file_path = filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp")])
    if not file_path:
        return  

    file_label.configure(text=file_path)
    original_image = Image.open(file_path)

    resized_original_image = resize_image_aspect_ratio(original_image, 250, 250)
    original_photo = ctk.CTkImage(light_image=resized_original_image, size=(resized_original_image.width, resized_original_image.height))
    img_label.configure(image=original_photo, text="")
    img_label.image = original_photo

    resolution_label.configure(text=f"Risoluzione: {original_image.width}x{original_image.height}")

    try:
        F = int(f_entry.get() or 10)
        d = int(d_entry.get() or 7)

        if d > 2 * F - 2:
            messagebox.showerror("Error", f"Invalid value for d. It should be at most 2F-2 ({2*F-2}).")
            return
    except ValueError:
        messagebox.showerror("Error", "Invalid F or d value")
        return

    original_size = os.path.getsize(file_path)
    compressed_file_path = process_image(file_path, F, d)
    if compressed_file_path:
        compressed_size = os.path.getsize(compressed_file_path)
        compression_ratio = 100 * (original_size - compressed_size) / original_size
        compression_label.configure(text=f"Dimensione originale: {original_size} bytes = {round(original_size / (1024 * 1024), 4) } MB\n"
                                      f"Dimensione compressa: {compressed_size} bytes = {round(compressed_size / (1024 * 1024), 4) }MB\n"
                                      f"Compressione: {compression_ratio:.2f}%")

        compressed_image = Image.open(compressed_file_path)
        resized_compressed_image = resize_image_aspect_ratio(compressed_image, 250, 250)
        compressed_photo = ctk.CTkImage(light_image=resized_compressed_image, size=(resized_compressed_image.width, resized_compressed_image.height))
        compressed_img_label.configure(image=compressed_photo, text="")
        compressed_img_label.image = compressed_photo

def resize_image_aspect_ratio(image, max_width, max_height):
    """Resize an image while maintaining its aspect ratio."""
    ratio = min(max_width / image.width, max_height / image.height)
    new_size = (int(image.width * ratio), int(image.height * ratio))
    return image.resize(new_size, Image.LANCZOS)

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
        progress_var.set(progress / 100) 
        progress_bar.set(progress_var.get())
        progress_bar.update_idletasks()
    except queue.Empty:
        pass
    root.after(100, check_progress, progress_queue, progress_var, progress_bar)
    progress_var.set(0)

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

def test_dct2():
    test_matrix = np.array([
        [231, 32, 233, 161, 24, 71, 140, 245],
        [247, 40, 248, 245, 124, 204, 36, 107],
        [234, 202, 245, 167, 9, 217, 239, 173],
        [193, 190, 100, 167, 43, 180, 8, 70],
        [11, 24, 210, 177, 81, 243, 8, 112],
        [97, 195, 203, 47, 125, 114, 165, 181],
        [193, 70, 174, 167, 41, 30, 127, 245],
        [87, 149, 57, 192, 65, 129, 178, 228]
    ], dtype=np.float32)

    result_dct2 = dct2(test_matrix)
    result_manualdct2 = dct2_manual(test_matrix)

    print("Result of dct2:")
    print(result_dct2)
    print("Result of the implemented dct2 :")
    print(result_manualdct2)


def dct2(matrix):
    return dct(dct(matrix.T, norm='ortho').T, norm='ortho')

ctk.set_appearance_mode("dark")  # Modes: "system" (default), "light", "dark"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (default), "dark-blue", "green"

root = ctk.CTk()
root.title("Compressione di immagini tramite la DCT")
root.geometry("800x800")

tabview = ctk.CTkTabview(master=root)
tabview.pack(expand=True, fill='both', padx=20, pady=20)

tabview.add("DCT")  
tabview.add("Comp")  

dct_frame = tabview.tab("DCT")
comp_frame = tabview.tab("Comp")

resolution_label = ctk.CTkLabel(dct_frame, text="")
resolution_label.pack(pady=10)

f_label = ctk.CTkLabel(dct_frame, text="Valore di F:")
f_label.pack(pady=5)
f_entry = ctk.CTkEntry(dct_frame)
f_entry.insert(0, "10")
f_entry.pack(pady=5)

d_label = ctk.CTkLabel(dct_frame, text="Valore di d:")
d_label.pack(pady=5)
d_entry = ctk.CTkEntry(dct_frame)
d_entry.insert(0, "7")
d_entry.pack(pady=5)

load_button = ctk.CTkButton(dct_frame, text="Load .bmp image", command=load_image)
file_label = ctk.CTkLabel(dct_frame, text="Nessun file selezionato")
compression_label = ctk.CTkLabel(dct_frame, text="")

image_frame = ctk.CTkFrame(dct_frame)
image_frame.pack()

img_label = ctk.CTkLabel(image_frame, text="")
compressed_img_label = ctk.CTkLabel(image_frame, text="")
load_button.pack(pady=10)
file_label.pack(pady=10)
compression_label.pack(pady=10)
img_label.pack(side=ctk.LEFT, padx=10)
compressed_img_label.pack(side=ctk.LEFT, padx=10)


comp_label = ctk.CTkLabel(comp_frame, text="Click below to generate a comparison between the library DTC2 and the manually implemented version!")
comp_label.pack(pady=10)

compare_button = ctk.CTkButton(comp_frame, text="Compare DCT2 Algorithms", command=lambda: compare_dct2_algorithms_thread(progress_var, progress_bar))
compare_button.pack(pady=10)

progress_var = ctk.DoubleVar()
progress_var.set(0) 
progress_bar = ctk.CTkProgressBar(comp_frame, variable=progress_var)
progress_bar.pack()

test_dct_button = ctk.CTkButton(dct_frame, text="Test DCT2 (in terminal)", command=test_dct2)
test_dct_button.pack(pady=10)

root.mainloop()
