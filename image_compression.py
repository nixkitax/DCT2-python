import numpy as np
from PIL import Image, ImageOps
from dct_functions import dct2, idct2

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
