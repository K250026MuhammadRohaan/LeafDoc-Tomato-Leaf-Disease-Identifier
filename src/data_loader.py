# ======================================================================
# data_loader.py
# LeafDoc - finds the dataset images and builds the cleaned Pandas table.
# (Lab 03 set/list, Lab 04 map/lambda, Lab 08 Pandas)
# ======================================================================

import os
import random
import pandas as pd

from config import FOLDER_TO_LABEL, RANDOM_STATE
from exceptions import InvalidImageError
from image_processor import FEATURE_NAMES


class DatasetManager:
    """Scans the image folders and builds one table: one row per image."""

    def __init__(self, data_dir, max_per_class=950):
        self.data_dir = data_dir              # folder where the dataset is
        self.max_per_class = max_per_class    # maximum images per disease
        self.class_names = set()              # set of disease names found (no duplicates)
        self.table = pd.DataFrame()           # the Pandas table (empty at start)

    # ------------------------------------------------------------------
    def scan_folders(self):
        """Look for the 4 tomato folders and return a list of (path, label)."""
        if not os.path.isdir(self.data_dir):
            raise FileNotFoundError(
                "Dataset folder not found: " + str(self.data_dir)
                + "\nPlease set DATA_DIR in src/config.py")

        # Walk through all sub-folders and remember where each tomato folder is
        found_folders = {}   # dict: folder name -> full path
        for root, dirs, files in os.walk(self.data_dir):
            for folder_name in dirs:
                if folder_name in FOLDER_TO_LABEL and folder_name not in found_folders:
                    found_folders[folder_name] = os.path.join(root, folder_name)

        if len(found_folders) == 0:
            raise FileNotFoundError(
                "No tomato folders (Tomato_healthy, Tomato_Early_blight, ...) found in: "
                + str(self.data_dir))

        image_list = []   # will hold (path, label) pairs
        rng = random.Random(RANDOM_STATE)   # fixed seed -> same images each run

        for folder_name, folder_path in found_folders.items():
            label = FOLDER_TO_LABEL[folder_name]
            self.class_names.add(label)

            all_files = os.listdir(folder_path)
            # list comprehension: keep only the .jpg files (any capital letters)
            jpg_files = [name for name in all_files if name.lower().endswith(".jpg")]
            jpg_files.sort()          # sort first so shuffling is repeatable
            rng.shuffle(jpg_files)    # mix them up
            jpg_files = jpg_files[:self.max_per_class]   # keep only the first 950

            # map + lambda: make the full path of every file name
            full_paths = list(map(lambda name: os.path.join(folder_path, name), jpg_files))

            for path in full_paths:
                image_list.append((path, label))

            print("Found", len(full_paths), "images for", label)

        return image_list

    # ------------------------------------------------------------------
    def build_table(self, processor, cache_path=None, use_cache=True):
        """Measure every image and put the numbers in a Pandas table.

        If a saved table (cache_path) already exists we just load it,
        because measuring ~3800 images takes a few minutes.
        """
        # Use the saved table if we have one
        if use_cache and cache_path is not None and os.path.isfile(cache_path):
            print("Loading saved table from", cache_path)
            self.table = pd.read_csv(cache_path)
            self.class_names = set(self.table["label"])
            return self.table

        image_list = self.scan_folders()
        rows = []         # one dict per image
        skipped = 0       # how many broken images we skipped

        for number, (path, label) in enumerate(image_list):
            try:
                features = processor.get_features(path)
            except InvalidImageError:
                skipped += 1      # broken image: skip it, do not crash
                continue

            row = {"file_path": path, "label": label}
            row.update(features)   # add the 6 feature numbers to the row
            rows.append(row)

            if (number + 1) % 200 == 0:   # show progress every 200 images
                print("  processed", number + 1, "of", len(image_list))

        self.table = pd.DataFrame(rows)
        print("Table built:", len(self.table), "images, skipped", skipped)

        # Save the table so next time it loads fast
        if cache_path is not None and len(self.table) > 0:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            self.table.to_csv(cache_path, index=False)
            print("Table saved to", cache_path)

        return self.table

    # ------------------------------------------------------------------
    def clean(self):
        """Clean the table: drop missing values, duplicates and bad labels."""
        before = len(self.table)

        self.table = self.table.dropna()                          # drop rows with missing values
        self.table = self.table.drop_duplicates(subset="file_path")   # same file twice? keep one
        # keep only rows whose label is one of our 4 classes
        self.table = self.table[self.table["label"].isin(FOLDER_TO_LABEL.values())]
        # percentages must be between 0 and 100
        self.table = self.table[(self.table["brown_pct"] >= 0) & (self.table["brown_pct"] <= 100)]
        self.table = self.table.reset_index(drop=True)            # fix row numbers

        print("Cleaning done: removed", before - len(self.table), "rows,", len(self.table), "left")
        return self.table

    # ------------------------------------------------------------------
    def summary(self):
        """Print the size of the table and the average colours of each disease."""
        print("Table shape (rows, columns):", self.table.shape)
        print("\nImages per disease:")
        print(self.table["label"].value_counts())
        print("\nAverage features per disease:")
        grouped = self.table.groupby("label")[FEATURE_NAMES].mean().round(2)
        print(grouped)
        return grouped
