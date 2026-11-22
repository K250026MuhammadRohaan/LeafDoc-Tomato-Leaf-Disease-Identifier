# ======================================================================
# storage.py
# LeafDoc - saves the history of diagnoses as CSV or JSON.
# ResultsStore is an abstract class; the two child classes override its
# methods (inheritance + polymorphism) - Lab 05 and 06.
# ======================================================================

import csv
import json
import os
from abc import ABC, abstractmethod


class ResultsStore(ABC):
    """Parent class. It cannot be used directly, only its children."""

    def __init__(self, path):
        self._path = path                                  # private: file path
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)             # create folder if missing

    def get_path(self):
        return self._path

    @abstractmethod
    def save_result(self, record):
        """Save one diagnosis (a dict)."""
        pass

    @abstractmethod
    def load_history(self):
        """Return all saved diagnoses as a list of dicts."""
        pass


class CsvResultsStore(ResultsStore):
    """Saves the history in a CSV file."""

    FIELDS = ["time", "image_path", "disease", "confidence"]   # column names

    def save_result(self, record):
        is_new_file = not os.path.exists(self._path)
        try:
            with open(self._path, "a", newline="", encoding="utf-8") as file:   # "a" = add to end
                writer = csv.DictWriter(file, fieldnames=self.FIELDS)
                if is_new_file:
                    writer.writeheader()          # first line with column names
                writer.writerow(record)
        except OSError:
            print("Could not save the result to the CSV file.")

    def load_history(self):
        if not os.path.exists(self._path):
            return []                              # no history yet
        try:
            with open(self._path, "r", newline="", encoding="utf-8") as file:
                return list(csv.DictReader(file))
        except OSError:
            print("Could not read the CSV history file.")
            return []


class JsonResultsStore(ResultsStore):
    """Saves the history in a JSON file (same method names, different format)."""

    def save_result(self, record):
        history = self.load_history()      # read old results
        history.append(record)             # add the new one
        try:
            with open(self._path, "w", encoding="utf-8") as file:
                json.dump(history, file, indent=2)
        except OSError:
            print("Could not save the result to the JSON file.")

    def load_history(self):
        if not os.path.exists(self._path):
            return []
        try:
            with open(self._path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            print("The JSON history file could not be read, starting a new history.")
            return []
