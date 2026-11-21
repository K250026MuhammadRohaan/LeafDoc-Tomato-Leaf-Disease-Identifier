# ======================================================================
# config.py
# LeafDoc - all the settings in ONE place (paths, sizes, K values).
# If you need to change a folder path, change it here only.
# ======================================================================

import os

# ---------- Project folders ----------
# Folder that contains the "src" folder (the main LeafDoc folder).
# os.path.abspath(__file__) = full path of this file, dirname = its folder.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# >>>>>>>>>> CHANGE THIS (1/1) <<<<<<<<<<
# Folder where you extracted the PlantVillage dataset from Kaggle.
# It must contain (somewhere inside it) these 4 folders:
#   Tomato_healthy, Tomato_Early_blight, Tomato_Late_blight, Tomato_Leaf_Mold
# Default = LeafDoc/data/raw   (just paste the dataset folders in there).
# Example for a different place on Windows:
#   DATA_DIR = r"D:\Datasets\PlantVillage"
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")

# ---------- Output folders (created automatically if missing) ----------
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "outputs", "figures")
HISTORY_DIR = os.path.join(PROJECT_ROOT, "outputs", "history")

# ---------- Files ----------
FEATURES_CSV = os.path.join(PROCESSED_DIR, "features_table.csv")     # saved Pandas table
CACHE_PATH = os.path.join(PROCESSED_DIR, "disease_info_cache.json")  # Wikipedia offline copy
MODEL_PATH = os.path.join(PROCESSED_DIR, "leafdoc_model.joblib")     # saved trained model
HISTORY_CSV = os.path.join(HISTORY_DIR, "history.csv")
HISTORY_JSON = os.path.join(HISTORY_DIR, "history.json")

# ---------- Settings ----------
IMAGE_SIZE = (128, 128)      # every photo is resized to 128 x 128
MAX_PER_CLASS = 950          # use at most 950 images from each disease folder
DEFAULT_K = 5                # default K for the KNN model
K_VALUES = [1, 3, 5, 11]     # K values we compare on the same split
TEST_SIZE = 0.2              # 80% train / 20% test
RANDOM_STATE = 42            # fixed number so results are the same every run

# Folder name in the PlantVillage dataset  ->  label we use in our program
FOLDER_TO_LABEL = {
    "Tomato_healthy": "healthy",
    "Tomato_Early_blight": "early_blight",
    "Tomato_Late_blight": "late_blight",
    "Tomato_Leaf_Mold": "leaf_mold",
}
