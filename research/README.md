# Parcel Validation Tool 2.0 Research

## Compilers

---

## GUIs

### Tkinter

---

## Open Source Tools


### Set up environment

After cloning the repository you will need to set up your python environment. You need to first install [miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/individual).

Open Anaconda Prompt and change to the gdal directory within the cloned repository and create the environment from file:
```bash
cd "research/open source tools"
conda env create --file environment.yml
```

Activate the environment using:
```bash
conda activate pvt_os_env
```

When you are done, deactivate to exit environment and optionally remove environment:
```bash
conda deactivate
conda remove --name wlia2022_env --all
```

### Example Scripts

`example_geom.py`: An example to check if parcel geometry is within a given county.

`example_fields.py`: An example of field validation.