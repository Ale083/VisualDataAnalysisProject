# Visual Data Analysis Project

## Required software

You need:

- Python 3
- NumPy 1.24 or newer
- VTK 9.2 or newer
- Tkinter, which is normally included with Python on Windows

Install the Python packages from the project folder with:

```powershell
python -m pip install -r requirements.txt
```

## Running the project

After installing the requirements and adding the data files below, start the
GUI with:

```powershell
python main.py
```

## Data files

The VTK datasets are not included in the repository because the `.vtu` files
are too large to upload. Obtain the data files from the course Moodle/SeaFile
links and place them in the following folders:

```text
VIS_2026_WS_Data/
├── Car_BMW/
│   ├── car_BMW_pressure.vtu
│   └── car_BMW_density.vtu
└── Train_ICE/
    ├── train_ICE_pressure.vtu
    └── train_ICE_density.vtu
```

Keep the filenames and folder structure exactly as shown. The program expects
these paths when running the `car` or `train` dataset options.
