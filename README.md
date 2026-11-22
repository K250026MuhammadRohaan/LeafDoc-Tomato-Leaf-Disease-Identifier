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
---- README.md
---- requirements.txt
---- .gitignore
---- data/
|   --- raw/                 PlantVillage leaf images
|   --- processed/           saved table, saved model, Wikipedia cache (created automatically)
---- outputs/
|   --- figures/             the three PNG charts
|   --- history/             diagnosis history (CSV / JSON)
---- src/
    --- config.py            all paths and settings
    --- exceptions.py        InvalidImageError
    --- image_processor.py   ImageProcessor
    --- data_loader.py       DatasetManager
    --- analysis.py          Pandas analysis helpers
    --- charts.py            ChartMaker
    --- models.py            DiseaseClassifier
    --- api_client.py        DiseaseInfoClient
    --- storage.py           ResultsStore, CsvResultsStore, JsonResultsStore
    --- main.py              console menu
```

## Requirements

- Windows with PowerShell
- Python 3.12 from python.org (3.10 to 3.13 also work). Very new versions (3.14) and MSYS2 / MinGW builds of Python may fail to install the libraries.
- Internet connection for the library installation (and for Wikipedia text; the program also works offline)

## Project Setup

**Step 0: Install git on PC**

Open Windows Powershell and type the following command, to install git:

```
winget install --id Git.Git -e --source winget
```

Then close down Powershell, and re-open it.


**Step 1: Clone from Github**

Then, in Windows Powershell, type the following commands:

```
git clone https://github.com/K250026MuhammadRohaan/LeafDoc-Tomato-Leaf-Disease-Identifier        

cd LeafDoc-Tomato-Leaf-Disease-Identifier 
```


**Step 2: Setup Virtual environment (Python 3.12)**

Next, open VS Code, and open the terminal, and type the follwing commands in:

```
py -3.12 -m venv .venv           

.\.venv\Scripts\Activate.ps1 
```
 

**Step 3: Install required libraries**

Next, type the following line, in the VS Code terminal:

```
pip install --default-timeout=100 --retries 10 -r requirements.txt    
```
 

**Step 4: Run the Program** 

Finally, type the following line in the VS Code terminal, to run the program:

```
python src\main.py         
```

## Running the program (every time after setup)

Open the downloaded github folder in VS Code, then open terminal there, and type the following code in there:

```
.\.venv\Scripts\Activate.ps1
python src\main.py
```

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

- PlantVillage tomato leaf images (Hughes & Salathé, 2015), 
Kaggle copy: https://www.kaggle.com/datasets/emmarex/plantdisease 
- Wikipedia REST API: https://en.wikipedia.org/api/rest_v1/page/summary/<page 
title> (e.g. Early blight, Late blight, Leaf mold). 
