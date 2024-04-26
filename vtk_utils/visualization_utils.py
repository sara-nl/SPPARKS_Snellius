"""
last modified on Apr 14

Utilities for visualize VTK objects
"""

from typing import List, Tuple
import numpy as np
import pyvista as pv
import vtk

# VTK file constants
EXTENT_SIZE_3D = (101, 101, 51)  # Total dimensions including the zero index
EXTENT_SIZE_2D = (101, 101)  # Expected dimensions for 2D rendering

ORIGIN = (0, 0, 0)
SPACING = (1, 1, 1)
CELL_DATA = "Spin"  # Used specifically for the Scalars attribute in CellData


def check_array_dimensions(numpy_array: np.ndarray, extent_size: tuple):
    """
    Check if the dimensions of a NumPy array match the expected shape.

    This function verifies that the dimensions of a given NumPy array match the provided expected shape,
    which can be for either 2D or 3D data. This is a flexible function that can be used to ensure the array dimensions
    are correct before processing or visualization.

    Parameters:
    - numpy_array (np.ndarray): The array to check.
    - expected_shape (tuple): The expected dimensions of the array (can be 2D or 3D).

    Returns:
    - bool: True if dimensions match the expected shape, False otherwise.

    Raises:
    - ValueError: If the input array dimensions do not match the expected dimensions.
    """
    expected_shape = tuple(e - 1 for e in extent_size)
    if numpy_array.shape != expected_shape:
        raise ValueError(
            f"Array dimensions {numpy_array.shape} do not match the expected dimensions {expected_shape}."
        )

    return True


def render_vtk(vtk_data_object: vtk.vtkImageData, filename: str = "visualization.png"):
    """
    Visualize a vtkImageData object. Automatically handles both 2D and 3D data.

    Parameters:
    vtk_data_object (vtk.vtkImageData): The vtkImageData object to visualize.
    """
    dims = vtk_data_object.GetDimensions()

    pv.start_xvfb()  # Start an X virtual framebuffer
    pv_data = pv.wrap(vtk_data_object)
    plotter = pv.Plotter(off_screen=True)

    # Check if the data is 2D or 3D and visualize accordingly
    if 1 in dims:
        # Data is 2D
        plotter.add_mesh(pv_data, cmap="viridis")  # Use a suitable colormap
    else:
        # Data is 3D
        plotter.add_volume(pv_data)

    plotter.show(auto_close=False)
    plotter.screenshot(filename)
    plotter.close()


def render_2D_from_numpy(numpy_array: np.ndarray, filename: str = "visual_np.png"):
    """
    Render a 2D image from a 2D slice of a NumPy array and save it as an image file.

    This function takes a 2D slice from a 3D NumPy array and renders it as a 2D image using PyVista.
    The rendering is performed off-screen and the resulting image is saved
    to a specified file.

    Parameters:
    - numpy_array (np.ndarray): A 2D NumPy array or a 2D slice of a 3D array. The shape of the array
      should be in the form (height, width) or a 2D slice like (height, width, 1).
    - filename (str, optional): The name of the file where the image will be saved.
    """
    check_array_dimensions(numpy_array, extent_size=EXTENT_SIZE_2D)

    grid = pv.ImageData()  # pv.UniformGrid()
    grid.dimensions = (
        numpy_array.shape[0] + 1,
        numpy_array.shape[1] + 1,
        1,
    )  # Note the ordering of dimensions
    grid.spacing = SPACING
    grid.origin = ORIGIN
    grid.cell_data[CELL_DATA] = numpy_array.flatten(order="C")

    pv.start_xvfb()
    plotter = pv.Plotter(off_screen=True)
    plotter.add_mesh(grid, cmap="viridis", show_edges=False)

    plotter.show(auto_close=False)
    plotter.screenshot(filename)
    plotter.close()


def render_3D_from_numpy(numpy_array: np.ndarray, filename: str = "visual_np.png"):
    """
    Render a 3D volume from a NumPy array and save it as an image.

    Parameters:
    - numpy_array (np.ndarray): A 3D NumPy array that should match the specified 'EXTENT'.
    - filename (str, optional): The name of the file where the image will be saved.
    """
    check_array_dimensions(numpy_array, extent_size=EXTENT_SIZE_3D)

    image = pv.ImageData(EXTENT_SIZE_3D)
    image.spacing = SPACING
    image.origin = ORIGIN
    image.cell_data[CELL_DATA] = numpy_array.flatten(order="C")

    pv.start_xvfb()
    plotter = pv.Plotter(off_screen=True)

    plotter.add_volume(image, cmap="viridis", scalar_bar_args={"title": CELL_DATA})

    plotter.show(auto_close=False)
    plotter.screenshot(filename)
    plotter.close()
