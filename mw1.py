"""MW.1.1 Basic Statistics and MW.1.2 Overview Visualization."""

from pathlib import Path

import numpy as np
import vtk


def read_vtu(filename):
    '''
    Creates the reader, sets what file it reads, processes the file and returns output
    '''
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(str(filename))
    reader.Update()
    return reader.GetOutput()


def get_values(grid, array_name):
    '''
    Takes a VTK and extracts on data field into a Numpy array.

    For example, grid named grid1 looks like:
    Point ID:       0       1       2       3
    Coordinates:  (0,0,0) (1,0,0) (0,1,0) (0,0,1)
    Pressure:      101.2   105.7   99.8    103.4 

    And the output for get_values(grid1, "Pressure") would be:
    array([101.2, 105.7,  99.8, 103.4]) 
    '''
    vtk_array = grid.GetPointData().GetArray(array_name)

    values = []
    for point_id in range(vtk_array.GetNumberOfTuples()):
        values.append(vtk_array.GetValue(point_id))
    return np.array(values)


def count_cell_types(grid):
    '''
    Count the three cell types requested in MW.1.1.
    '''
    tetrahedra = 0
    prisms = 0      
    pyramids = 0

    for cell_id in range(grid.GetNumberOfCells()):
        cell_type = grid.GetCellType(cell_id)
        if cell_type == vtk.VTK_TETRA:
            tetrahedra += 1
        elif cell_type == vtk.VTK_WEDGE: #in VTK a prism is called a wedge.
            prisms += 1
        elif cell_type == vtk.VTK_PYRAMID:
            pyramids += 1

    return tetrahedra, prisms, pyramids


def find_min_and_max(values, grid):
    '''
    Find min and max of a certain value and the point in the grid where each occurs.
    '''
    min_id = int(np.argmin(values))
    max_id = int(np.argmax(values))

    min_value = values[min_id]
    max_value = values[max_id]
    min_position = grid.GetPoint(min_id)
    max_position = grid.GetPoint(max_id)

    return min_value, min_position, max_value, max_position


def print_scalar_statistics(name, values, grid):
    '''
    Print the extremes, mean, and median for one scalar value.
    '''
    min_value, min_position, max_value, max_position = find_min_and_max(values, grid)

    print(f"\n{name}")
    print("-" * len(name))
    print(f"Minimum: {min_value:.6f} at {min_position}")
    print(f"Maximum: {max_value:.6f} at {max_position}")
    print(f"Mean:    {np.mean(values):.6f}")
    print(f"Median:  {np.median(values):.6f}")


    return min_position, max_position


def print_basic_statistics(pressure_grid, density_grid):
    '''
    Prints the measurements requested in MW.1.1
    Returns the positions used for MW.1.2, that way we don't have to calculate them twice
    '''
    print("MW.1.1 - Basic statistics")
    print("=" * 27)
    print(f"Number of vertices: {pressure_grid.GetNumberOfPoints()}")
    print(f"Overall number of cells: {pressure_grid.GetNumberOfCells()}")

    tetrahedra, prisms, pyramids = count_cell_types(pressure_grid)
    print(f"Number of tetrahedra: {tetrahedra}")
    print(f"Number of prisms: {prisms}")
    print(f"Number of pyramids: {pyramids}")

    #GetBounds returns xmin, xmax, ymin, ymax, zmin, zmax.
    bounds = pressure_grid.GetBounds()
    print("Bounding box:")
    #:.6f formats each number to six decimal places.
    print(f"  x: {bounds[0]:.6f} to {bounds[1]:.6f}")
    print(f"  y: {bounds[2]:.6f} to {bounds[3]:.6f}")
    print(f"  z: {bounds[4]:.6f} to {bounds[5]:.6f}")

    pressure_values = get_values(pressure_grid, "pressure")
    density_values = get_values(density_grid, "density")

    pressure_min, pressure_max = print_scalar_statistics(
        "Pressure", pressure_values, pressure_grid
    )
    density_min, density_max = print_scalar_statistics(
        "Density", density_values, density_grid
    )

    return pressure_min, pressure_max, density_min, density_max


def make_sphere(position, radius, color):
    '''
    Create one colored sphere in a 3d position.
    '''
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(position)
    sphere.SetRadius(radius)

    #this just makes the sphere look better
    sphere.SetThetaResolution(20)
    sphere.SetPhiResolution(20)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphere.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    return actor


def show_overview(grid, pressure_min, pressure_max, density_min, density_max):
    '''
    Show visualization and extremes as requested in MW.1.2.
    '''
    # vtkOutlineFilter turns the data set's bounds into 12 visible lines.
    outline = vtk.vtkOutlineFilter()
    outline.SetInputData(grid)

    outline_mapper = vtk.vtkPolyDataMapper()
    outline_mapper.SetInputConnection(outline.GetOutputPort())

    outline_actor = vtk.vtkActor()
    outline_actor.SetMapper(outline_mapper)
    outline_actor.GetProperty().SetColor(0.9, 0.9, 0.9)
    outline_actor.GetProperty().SetLineWidth(2)

    #make the spheres large enough to see, based on the bound size
    bounds = grid.GetBounds()
    width = bounds[1] - bounds[0]
    height = bounds[3] - bounds[2]
    depth = bounds[5] - bounds[4]
    sphere_radius = 0.012 * np.sqrt(width**2 + height**2 + depth**2)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.1, 0.1, 0.1)

    # Show the actual outer surface of the train/car dataset.  Turning scalar
    # visibility off keeps the geometry neutral so the four colored spheres
    # remain easy to identify.
    surface_mapper = vtk.vtkDataSetMapper()
    surface_mapper.SetInputData(grid)
    surface_mapper.ScalarVisibilityOff()

    surface_actor = vtk.vtkActor()
    surface_actor.SetMapper(surface_mapper)
    surface_actor.GetProperty().SetColor(0.55, 0.65, 0.75)
    surface_actor.GetProperty().SetOpacity(0.35)
    surface_actor.GetProperty().SetEdgeVisibility(True)
    surface_actor.GetProperty().SetEdgeColor(0.75, 0.8, 0.85)

    renderer.AddActor(surface_actor)
    renderer.AddActor(outline_actor)

    #blue = low pressure; red = high pressure.
    #green = low density; orange = high density.
    renderer.AddActor(make_sphere(pressure_min, sphere_radius, (0.1, 0.3, 1.0)))
    renderer.AddActor(make_sphere(pressure_max, sphere_radius, (1.0, 0.1, 0.1)))
    renderer.AddActor(make_sphere(density_min, sphere_radius, (0.1, 0.9, 0.2)))
    renderer.AddActor(make_sphere(density_max, sphere_radius, (1.0, 0.6, 0.0)))

    window = vtk.vtkRenderWindow()
    window.SetWindowName("MW.1.2")
    window.SetSize(1100, 800)
    window.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)
    renderer.ResetCamera()
    window.Render()
    interactor.Start()


def get_file_paths(dataset):
    '''
    Return the correct pressure and density file for train or car.
    '''
    data_folder = Path(__file__).resolve().parent / "VIS_2026_WS_Data"

    if dataset == "train":
        folder = data_folder / "Train_ICE"
        pressure_file = "train_ICE_pressure.vtu"
        density_file = "train_ICE_density.vtu"

    elif dataset == "car":
        folder = data_folder / "Car_BMW"
        pressure_file = "car_BMW_pressure.vtu"
        density_file = "car_BMW_density.vtu"

    return folder / pressure_file, folder / density_file


def main(dataset):
    '''
    Run complete MW.1 workflow
    '''
    if dataset not in {"train", "car"}:
        raise ValueError("dataset must be 'train' or 'car'")

    pressure_file, density_file = get_file_paths(dataset)
    pressure_grid = read_vtu(pressure_file)
    density_grid = read_vtu(density_file)

    pressure_min, pressure_max, density_min, density_max = print_basic_statistics(
        pressure_grid, density_grid
    )

    show_overview(
        pressure_grid, pressure_min, pressure_max, density_min, density_max
    )
