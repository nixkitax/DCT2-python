import numpy as np
import time
import matplotlib.pyplot as plt
import threading
import queue
from dct_functions import dct2, idct2

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

def compare_dct2_algorithms_thread(progress_var, progress_bar, root):
    progress_queue = queue.Queue()
    plot_queue = queue.Queue()
    threading.Thread(target=compare_dct2_algorithms, args=(progress_queue, plot_queue)).start()
    root.after(100, check_progress, progress_queue, progress_var, progress_bar, root)
    root.after(100, check_plot, plot_queue, root)

def check_progress(progress_queue, progress_var, progress_bar, root):
    try:
        progress = progress_queue.get_nowait()
        if progress == "done":
            return
        progress_var.set(progress)
        progress_bar.update_idletasks()
    except queue.Empty:
        pass
    root.after(100, check_progress, progress_queue, progress_var, progress_bar, root)

def check_plot(plot_queue, root):
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
        root.after(100, check_plot, plot_queue, root)
