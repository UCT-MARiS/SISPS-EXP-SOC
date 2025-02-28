# SISPS-EXP-SOC

Experimental Analysis of Asterion HR12-9 batteries using Electrochemical Impedance Spectroscopy (EIS).

This work contributes towards the paper entitled _Observations of Freezing Lead Acid Batteries using Electrochemical Impedance Spectroscopy_ (currently submitted to the Journal of Energy Storage).

> [!CAUTION]
> This repository has been cited in (pending) published works and may never not be renamed, moved, made private, or deleted.
>
> The repository ought to normally be Archived so that no changes can be made after the final publication of the paper. Only improvements to the documentation and instructions are to be exempted, with caution.
>
> Date Accepted: **--/--/----**  
> Date Published: **--/--/----**

## Contents

This repository contains all analytical code, methodology, documentation, manuals, and photographs used or generated in the course of the experiment.

Raw data of EIS spectra, charge cycling, varied discharge, test chamber temperature, and hand notes is included in the [submodule repository](./.gitmodules) [SISPS-EXP-SOC-DATA](https://github.com/UCT-MARIS/SISPS-EXP-SOC-DATA) (`Data/`).

### Data

Refer to the [submodule repository](https://github.com/UCT-MARIS/SISPS-EXP-SOC-DATA) for details.

<!-- - [`Data/EIS/`](./Data/EIS/) - Contains the raw CSV data files of EIS tests.
- [`Data/ETC/`](./Data/ETC/) - Contains the raw CSV data files of ETC history.
- [`Data/Cycling/`](./Data/Cycling/) - Time series data of Batch B battery cycling.
- [`Data/Varied Discharge/`](./Data/Varied%20Discharge/) - Time series data of battery varied discharge. -->

### Documentation

- [`Docs/`](./Docs/) - Documentation of the experiment and relevant instruments.
- [`Photos/`](./Photos/) - Photos of the experiment (git LFS).

### Analysis

- [`Notebook/`](./Notebook/) - Jupyter notebooks for data analysis.
- [`Plots/`](./Plots/) - Plots generated from analysis

> [!NOTE]
> Most plots are not displayed in the notebooks, but are saved in the [`Plots/`](./Plots/) directory.  
> Run the notebooks to generate plots.
> All plots are [.gitignored](./.gitignore), except for PGF outputs intended for LaTeX.  

## Usage

> [!TIP]
> This repository uses [GitHub Actions](https://github.com/UCT-MARiS/SISPS-EXP-SOC/actions) to run the notebooks and generate plots, and from which artefacts may be downloaded including all plots.
> Note however that the artefacts are deleted after some time from the time of the last run.

### Cloning

This repository contains a submodule. To clone the repository and its submodule, use the following command:

```zsh
git clone --recurse-submodules https://github.com/UCT-MARIS/SISPS-EXP-SOC
```

### Notebooks

Two Jupyter notebooks execute data importing, preprocessing, and graphical analysis data:

1. [main.ipynb](./Notebook/main.ipynb) - Main analysis of EIS data and other plots.
2. [concentrationPlots.ipynb](./Notebook/concentrationPlots.ipynb) - Analysis of concentration-related plots.

Specific instructions can be found in the notebook itself.

### Python Environment

The notebooks use Anaconda to manage the Python environment.
The environment file [`environment.yml`](./environment.yml) defines all dependencies.
Please follow the Conda documentation for installation and creating the environment.
A useful guide can be found [here](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file), however this may vary depending on your system and choice of any particular IDE.

> [!NOTE]
> Remember to create the environment within the [`./Notebook/`](./Notebook/) directory to avoid potential issues with relative paths.  
> The recommended python version is **3.11**.

## Issues

Please feel free to raise any issues or suggestions in the [Issues](https://github.com/UCT-MARiS/SISPS-EXP-SOC/issues) section.
The authors will strive to improve and clarify documentation and instructions as necessary.
Note however that no changes may alter the outputs of the analysis, but this can be done in a separate branch or fork of the repository.
