# From-Flat-to-Mountain

## Overview
From-Flat-to-Mountain is a short analytical report that explores UCI World Tour stage points for different rider classes across flat, hilly, and mountain stages. The workflow combines a reproducible Python pipeline for visualizations (`generate_figures.py`) with a LaTeX manuscript (`cycling.tex`). Running the pipeline regenerates every figure used in the PDF so that the report always reflects the latest data and styling tweaks.

## Repository Layout
- `cycling.txt` – raw, whitespace-delimited stage-level data with rider class, stage profile, and points.
- `generate_figures.py` – scripts that reshape the dataset, fit diagnostic models, and export PNG figures into `figures/`.
- `cycling.tex` – LaTeX source that pulls in the generated graphics to produce `cycling.pdf`.
- `figures/` – cached outputs from the last figure build (safe to delete and regenerate).
- `cycling.ipynb` – scratchpad notebook that mirrors the Python workflow for exploratory work.
- Supporting LaTeX artifacts (`.aux`, `.toc`, etc.) are by-products of the PDF build and can be regenerated at any time.

## Requirements
- Python 3.10 or newer (earlier versions with `pathlib` support should also work).
- Packages: `matplotlib`, `numpy`, `pandas`, `seaborn`, `statsmodels`.
- A LaTeX distribution (TeX Live / MikTeX) if you plan to rebuild the PDF locally.

You can install the Python stack inside a virtual environment with:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install matplotlib numpy pandas seaborn statsmodels
```

## Reproducing the Figures
1. Ensure `cycling.txt` is present in the repository root. The loader expects space-separated values with the header row shown in the file.
2. Run the generator (from the repo root):

```powershell
python generate_figures.py
```

The script saves publication-ready PNGs under `figures/` and logs the exact filenames so you can confirm the refresh.

## Building the PDF Report
Once the figures are refreshed, compile the LaTeX source to rebuild `cycling.pdf`:

```powershell
pdflatex -interaction=nonstopmode cycling.tex
pdflatex -interaction=nonstopmode cycling.tex
```

Running pdflatex twice resolves figure references and the table of contents. Clean artifacts can be removed with `del cycling.aux cycling.log ...` as needed.

## Troubleshooting
- **Missing data file** – `generate_figures.py` raises `FileNotFoundError` if `cycling.txt` is absent; copy the latest export before running the script.
- **Package errors** – double-check that the virtual environment is active and `pip install` succeeded; `python -m pip list` can confirm versions.
- **LaTeX build issues** – make sure your LaTeX distribution knows where to find the `figures/` directory; keeping it in the repo root (as tracked) allows relative paths in `cycling.tex` to resolve automatically.