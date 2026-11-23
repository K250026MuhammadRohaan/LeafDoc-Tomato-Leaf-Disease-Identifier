# ======================================================================
# charts.py
# LeafDoc - draws and saves the three PNG charts (Lab 09).
# ======================================================================

import os
import matplotlib.pyplot as plt
import seaborn as sns


class ChartMaker:
    """Makes the 3 charts and saves them as PNG files in one folder."""

    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)   # create folder if it is missing

    # ------------------------------------------------------------------
    def class_counts_chart(self, table):
        """Bar chart: number of images in each class."""
        plt.figure(figsize=(7, 4))
        sns.countplot(data=table, x="label", hue="label", legend=False)
        plt.title("Number of images per class")
        plt.xlabel("Disease")
        plt.ylabel("Number of images")
        return self._save("class_counts.png")

    # ------------------------------------------------------------------
    def brown_boxplot(self, table):
        """Boxplot: % of brown pixels for each disease."""
        plt.figure(figsize=(7, 4))
        sns.boxplot(data=table, x="label", y="brown_pct", hue="label", legend=False)
        plt.title("Brown % in each disease")
        plt.xlabel("Disease")
        plt.ylabel("Brown pixels (%)")
        return self._save("brown_boxplot.png")

    # ------------------------------------------------------------------
    def confusion_matrix_chart(self, matrix, labels):
        """Heatmap of the confusion matrix (rows = real, columns = predicted)."""
        plt.figure(figsize=(6, 5))
        sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues",
                    xticklabels=labels, yticklabels=labels)
        plt.title("Confusion matrix (unseen test images)")
        plt.xlabel("Predicted disease")
        plt.ylabel("Real disease")
        return self._save("confusion_matrix.png")

    # ------------------------------------------------------------------
    def _save(self, file_name):
        """Saves the current chart and closes it."""
        path = os.path.join(self.output_dir, file_name)
        plt.tight_layout()
        plt.savefig(path, dpi=120)
        plt.close()          # close it so charts do not pile up in memory
        print("Chart saved:", path)
        return path
