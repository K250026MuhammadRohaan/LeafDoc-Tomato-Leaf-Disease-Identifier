# LeafDoc: Tomato Leaf Disease Identifier

AL-2001 Programming for Artificial Intelligence (Lab), Fall 2026
FAST NUCES, Karachi Campus. Section BAI-3A. Track B (Images / CV)

**Group members**
- Muhammad Rohaan (25K-0026)
- Sarim Raza Ansari (25K-0064)
- Rana Muhammad Hussain (25K-0141)

## About the project

LeafDoc is a console program that checks tomato leaf photos. For a given photo it prints:

- the predicted class: healthy, early blight, late blight or leaf mold
- a confidence score
- a short description of the disease from Wikipedia (a saved copy is used when there is no internet)

Every result is saved to a history file (CSV or JSON). The program is meant as a quick first check only and does not replace an expert.

## How it works

1. A photo is loaded as a NumPy array, resized to 128x128, converted from RGB to HSV and scaled to 0-1.
2. Six colour features are measured: percentage of brown, yellow and green pixels, and the mean hue, saturation and brightness.
3. A KNN classifier (scikit-learn) predicts the disease from these six numbers.
4. The dataset is stored in a Pandas table (one row per image) for cleaning, grouping and charts.

## Project structure

```
LeafDoc/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/                 PlantVillage dataset goes here (not pushed to GitHub)
│   └── processed/           saved table, saved model, Wikipedia cache (created automatically)
├── outputs/
│   ├── figures/             the three PNG charts
│   └── history/             diagnosis history (CSV / JSON)
└── src/
    ├── config.py            all paths and settings
    ├── exceptions.py        InvalidImageError
    ├── image_processor.py   ImageProcessor
    ├── data_loader.py       DatasetManager
    ├── analysis.py          Pandas analysis helpers
    ├── charts.py            ChartMaker
    ├── models.py            DiseaseClassifier
    ├── api_client.py        DiseaseInfoClient
    ├── storage.py           ResultsStore, CsvResultsStore, JsonResultsStore
    └── main.py              console menu
```

## Requirements

- Windows with PowerShell (Mac / Linux commands are given in brackets)
- Python 3.12 from python.org (3.10 to 3.13 also work). Very new versions (3.14) and MSYS2 / MinGW builds of Python may fail to install the libraries.
- Internet connection for the library installation (and for Wikipedia text; the program also works offline)

## Setup (done once)

**Step 1: Install Python 3.12**

Download it from python.org and tick "Add python.exe to PATH" in the installer.
Alternatively, run `py install 3.12` in PowerShell.

**Step 2: Get the dataset**

Download PlantVillage from Kaggle: https://www.kaggle.com/datasets/emmarex/plantdisease

Extract it into `data/raw/`. These four folders must exist somewhere inside it (other plant folders are ignored):

```
Tomato_healthy
Tomato_Early_blight
Tomato_Late_blight
Tomato_Leaf_Mold
```

All images can stay in the folders. The program picks up to 950 images per class by itself (`MAX_PER_CLASS` in `src/config.py`).

If the dataset is stored somewhere else, change `DATA_DIR` in `src/config.py`, for example:

```python
DATA_DIR = r"D:\Datasets\PlantVillage"
```

**Step 3: Open PowerShell in the project folder**

```
cd "C:\path\to\LeafDoc"
```

**Step 4: Create the virtual environment**

```
py -3.12 -m venv .venv
```

Check with `dir .venv`: a folder named `Scripts` should be there.

**Step 5: Activate it**

```
.\.venv\Scripts\Activate.ps1
```

The `(.venv)` mark should appear at the start of the line. If PowerShell says that running scripts is disabled, run `Set-ExecutionPolicy -Scope Process Bypass` and activate again.
[Mac / Linux: `python3 -m venv .venv` and `source .venv/bin/activate`]

**Step 6: Install the libraries**

```
pip install --default-timeout=100 --retries 10 -r requirements.txt
```

If the download times out, run the same command again. Files that were already downloaded are reused.

## Running the program (every time)

```
cd "C:\path\to\LeafDoc"
.\.venv\Scripts\Activate.ps1
python src\main.py
```

[Mac / Linux: `source .venv/bin/activate` and `python3 src/main.py`]

## Menu options

| Option | Description |
|---|---|
| 1 | Dataset summary and Pandas analysis |
| 2 | Train the KNN model, compare K = 1, 3, 5, 11 on the same 80/20 split, show accuracy and report |
| 3 | Diagnose a leaf photo (enter the path of a .jpg file) |
| 4 | Save the three charts to `outputs/figures/` |
| 5 | Show the diagnosis history |
| 6 | Switch the history format between CSV and JSON |
| 0 | Exit |

Suggested order on the first run: **2**, then **4**, then **3**.

The first run measures around 3800 images and takes a few minutes. The measured table is then saved to `data/processed/features_table.csv`, so later runs start quickly. This file must be deleted if the dataset or the colour settings in `src/image_processor.py` are changed, so that it gets rebuilt.

## Output files

| File | Content |
|---|---|
| `outputs/figures/class_counts.png` | number of images per class |
| `outputs/figures/brown_boxplot.png` | brown percentage for each disease |
| `outputs/figures/confusion_matrix.png` | confusion matrix on the unseen test images |
| `outputs/history/history.csv` or `history.json` | saved diagnoses |
| `data/processed/disease_info_cache.json` | saved Wikipedia descriptions (offline use) |

## Troubleshooting

| Problem | Fix |
|---|---|
| `.venv\Scripts\activate` is not recognized | Use `.\.venv\Scripts\Activate.ps1` (the `.\` at the start is required in PowerShell) |
| Running scripts is disabled | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again |
| `No matching distribution found for numpy` | The Python version is unsupported. Install Python 3.12 and recreate `.venv` |
| `ReadTimeoutError` during install | Slow internet. Run the install command again |
| `Dataset folder not found` or `No tomato folders` | Check that the four Tomato folders are inside `data/raw/`, or fix `DATA_DIR` in `src/config.py` |
| Old results after changing the dataset or settings | Delete `data/processed/features_table.csv` and `data/processed/leafdoc_model.joblib` |

## Error handling

The program shows a message and continues (no crash) in these cases:

- the image path is wrong or the file does not exist
- the file is not a real image or is damaged
- the menu input is not a number or is out of range
- the dataset folder is missing
- the internet is down or Wikipedia does not answer with status 200 (the saved copy or a built-in text is used)

## Ethics and limitations

- LeafDoc is a first check only. A wrong prediction can happen, especially on photos taken in the field.
- It works best with one leaf on a plain, clear background, like the PlantVillage photos.
- Only four tomato classes are supported. Other crops and diseases are not covered.
- No treatment or chemical advice is given.
- Colour alone can confuse similar diseases. The real accuracy is reported honestly after training (option 2).

## Data sources

- PlantVillage dataset (Hughes and Salathe, 2015), Kaggle copy linked above.
- Wikipedia REST API (text under CC BY-SA 4.0): https://en.wikipedia.org/api/rest_v1/page/summary/

## Git workflow

```
git pull
git add .
git commit -m "short message about the change"
git push
```

Pull before starting work, and edit only the files of the own part to avoid merge conflicts.
