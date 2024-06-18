
# Image Compression using DCT - Project README

## Project Overview

This project demonstrates image compression using the Discrete Cosine Transform (DCT). It provides a graphical user interface (GUI) to load, compress, and visualize BMP images. Additionally, it compares the performance of manual and library-based DCT implementations across various matrix sizes.

## Environment Setup

To ensure that you have all the necessary dependencies, a virtual environment should be created and activated before running the project. Follow these steps to set up your environment:

1.  **Create a virtual environment**:
    
    bash
    
    Copia codice
    
    `python -m venv env` 
    
2.  **Activate the virtual environment**:
    
    -   On Windows:
        
        bash
        
        Copia codice
        
        `.\env\Scripts\activate` 
        
    -   On macOS and Linux:
        
        bash
        
        Copia codice
        
        `source env/bin/activate` 
        
3.  **Install the required packages**:
    
    bash
    
    Copia codice
    
    `pip install -r requirements.txt` 
    

## Requirements

The following Python packages are required for this project:

-   `tkinter`
-   `Pillow`
-   `numpy`
-   `matplotlib`
-   `scipy`

Ensure that these packages are installed in your environment. A `requirements.txt` file is provided for convenience.

## Project Structure

The project is divided into several modules to organize the code effectively:

1.  **GUI and Main Application (`main.py`)**:
    
    -   This module initializes the main window using Tkinter, loads images, processes compression, and manages user interactions.
2.  **DCT Algorithms (`dct_algorithms.py`)**:
    
    -   Contains both manual and library-based implementations of 2D DCT and IDCT.
3.  **Image Processing (`image_processing.py`)**:
    
    -   Handles image conversion to/from matrices, DCT application, and filtering frequencies.
4.  **Performance Comparison (`compare_performance.py`)**:
    
    -   Measures and compares the performance of manual and library-based DCT algorithms.

## Usage

### Running the Application

1.  **Start the application**:
    
    bash
    
    Copia codice
    
    `python dct_image_processor.py` 
    
2.  **Load an Image**:
    
    -   Click on "Load .bmp image" to select a BMP file.
    -   Adjust the parameters `F` (block size) and `d` (frequency cut-off) if needed.
3.  **Compress the Image**:
    
    -   The application will display the original and compressed images side by side.
    -   Compression details, including original size, compressed size, and compression ratio, will be shown.
4.  **Compare DCT2 Algorithms**:
    
    -   Navigate to the "Comp" tab.
    -   Click on "Compare DCT2 Algorithms" to start the performance comparison.
    -   A progress bar will indicate the status, and a plot will display the results once completed.

### Parameters

-   **F (Block Size)**: Determines the size of the blocks for DCT transformation. Default is 10.
-   **d (Frequency Cut-off)**: Specifies the threshold for filtering frequencies during compression. Default is 7.

### Normalization

-   Check the "Normalize DCT Coefficients" option to enable normalization of DCT coefficients.

## Additional Information

-   **Progress and Visualization**:
    
    -   The progress of DCT algorithm comparison is shown using a progress bar.
    -   The comparison results are visualized using matplotlib.
-   **Error Handling**:
    
    -   Error messages will be displayed in case of invalid inputs or issues with file loading.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
