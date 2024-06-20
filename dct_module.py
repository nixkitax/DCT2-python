import numpy as np
from scipy.fftpack import dct, idct
import time

def dct2_manual(matrix):
    N = matrix.shape[0]
    result = np.zeros_like(matrix, dtype=np.float32)
    for u in range(N):
        for v in range(N):
            sum_val = 0
            for x in range(N):
                for y in range(N):
                    sum_val += matrix[x, y] * np.cos(np.pi * u * (2 * x + 1) / (2 * N)) * \
                    np.cos(np.pi * v * (2 * y + 1) / (2 * N))
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
                    sum_val += alpha_u * alpha_v * matrix[u, v] * np.cos(np.pi * u * \
                    (2 * x + 1) / (2 * N)) * np.cos(np.pi * v * (2 * y + 1) / (2 * N))
            result[x, y] = sum_val
    return result

def dct2(matrix):
    return dct(dct(matrix.T, norm='ortho').T, norm='ortho')

def idct2(matrix):
    return idct(idct(matrix.T, norm='ortho').T, norm='ortho')

def compare_dct2_algorithms(progress_queue, plot_queue):
    sizes = [8, 16, 32]
    manual_times = []
    library_times = []
    iterations = 10  

    total_steps = len(sizes) * 2
    step = 0
    
    for size in sizes:
        print("size: ", size)
        matrix = np.random.rand(size, size).astype(np.float32)
        
        start_time = time.perf_counter()
        for _ in range(iterations):
            dct2_manual(matrix)
        manual_time = (time.perf_counter() - start_time) / iterations
        manual_times.append(manual_time)
        print(f"Manual DCT2 (size={size}): {manual_time:.6f} seconds")
        step += 1
        progress_queue.put((step / total_steps) * 100)
        
        start_time = time.perf_counter()
        for _ in range(iterations):
            dct2(matrix)
        library_time = (time.perf_counter() - start_time) / iterations
        library_times.append(library_time)
        print(f"Library DCT2 (size={size}): {library_time:.6f} seconds")
        step += 1
        progress_queue.put((step / total_steps) * 100)
        
    print("Sizes: ", sizes)
    print("Manual times: ", manual_times)
    print("Library times: ", library_times)

    progress_queue.put("done")
    plot_queue.put((sizes, manual_times, library_times))

