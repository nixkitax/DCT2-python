import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageOps, ImageTk
import os

from image_compression import process_image
from dct_comparison import compare_dct2_algorithms_thread

def setup_ui(root):
    root.title("Compressione di immagini tramite la DCT")
    root.geometry("800x600")

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    dct_frame = ttk.Frame(notebook)
    compare_frame = ttk.Frame(notebook)

    notebook.add(dct_frame, text="DCT")
    notebook.add(compare_frame, text="Comp")

    f_entry = ttk.Entry(dct_frame)
    f_entry.insert(0, "10")
    d_entry = ttk.Entry(dct_frame)
    d_entry.insert(0, "7")

    load_button = ttk.Button(dct_frame, text="Load .bmp image", command=lambda: load_image(f_entry, d_entry, file_label, img_label, compression_label, compressed_img_label))
    file_label = ttk.Label(dct_frame, text="Nessun file selezionato")
    compression_label = ttk.Label(dct_frame, text="")

    image_frame = tk.Frame(dct_frame)
    image_frame.pack()

    img_label = tk.Label(image_frame)
    compressed_img_label = tk.Label(image_frame)
    f_entry.pack()
    d_entry.pack()
    load_button.pack()
    file_label.pack()
    compression_label.pack()
    img_label.pack(side=tk.LEFT)
    compressed_img_label.pack(side=tk.LEFT)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(compare_frame, variable=progress_var, maximum=100)
    progress_bar.pack(pady=10)

    compare_button = tk.Button(compare_frame, text="Compare DCT2 Algorithms", command=lambda: compare_dct2_algorithms_thread(progress_var, progress_bar, root))
    compare_button.pack()

def load_image(f_entry, d_entry, file_label, img_label, compression_label, compressed_img_label):
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
