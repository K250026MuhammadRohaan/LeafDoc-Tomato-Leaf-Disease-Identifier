# ======================================================================
# models.py
# LeafDoc - KNN model: train, test, compare K values, predict (Lab 10-11).
# ======================================================================

import joblib
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

from image_processor import FEATURE_NAMES


class DiseaseClassifier:
    """KNN model that predicts the disease from the 6 colour features."""

    def __init__(self, k=5, test_size=0.2, random_state=42):
        self.k = k                          # number of neighbours
        self.test_size = test_size
        self.random_state = random_state
        self._model = None                  # private: the KNN model (made in train())
        self._scaler = StandardScaler()     # puts all features on a similar scale
        self._labels = []                   # disease names, sorted
        # the 80/20 split is stored here so every K is tested on the SAME split
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

    # ------------------------------------------------------------------
    def prepare_split(self, table):
        """Split the table into 80% training and 20% testing data."""
        X = table[FEATURE_NAMES].values      # the numbers
        y = table["label"].values            # the answers (disease names)
        self._labels = sorted(set(y))

        # stratify=y keeps the same share of each disease in both parts
        X_train, X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, stratify=y)

        # Fit the scaler on TRAINING data only, then apply it to both parts
        self.X_train = self._scaler.fit_transform(X_train)
        self.X_test = self._scaler.transform(X_test)
        print("Split done:", len(self.y_train), "train images,", len(self.y_test), "test images")

    # ------------------------------------------------------------------
    def train(self, table=None):
        """Train the KNN model with the current K."""
        if table is not None:
            self.prepare_split(table)
        if self.X_train is None:
            raise ValueError("No data yet. Give train() the table first.")

        self._model = KNeighborsClassifier(n_neighbors=self.k)
        self._model.fit(self.X_train, self.y_train)
        print("Model trained with K =", self.k)

    # ------------------------------------------------------------------
    def evaluate(self):
        """Test on the unseen 20%. Returns (accuracy, confusion matrix, report text)."""
        predictions = self._model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, predictions)
        matrix = confusion_matrix(self.y_test, predictions, labels=self._labels)
        report = classification_report(self.y_test, predictions, zero_division=0)
        return accuracy, matrix, report

    # ------------------------------------------------------------------
    def compare_k_values(self, k_values=(1, 3, 5, 11)):
        """Try several K values on the same split. Returns {K: accuracy}."""
        results = {}
        for k in k_values:
            model = KNeighborsClassifier(n_neighbors=k)
            model.fit(self.X_train, self.y_train)
            results[k] = accuracy_score(self.y_test, model.predict(self.X_test))

        # sorted + lambda: best accuracy first
        ranking = sorted(results.items(), key=lambda pair: pair[1], reverse=True)
        print("K values ranked (best first):")
        for k, accuracy in ranking:
            print("  K =", k, "-> accuracy", round(accuracy * 100, 2), "%")
        return results

    # ------------------------------------------------------------------
    def rank_predictions(self, features):
        """Return [(disease, probability), ...] sorted from most to least likely."""
        # features is a dict -> make a list in the right order
        numbers = [features[name] for name in FEATURE_NAMES]
        scaled = self._scaler.transform([numbers])
        probabilities = self._model.predict_proba(scaled)[0]   # one probability per class

        pairs = list(zip(self._model.classes_, probabilities))
        # sorted + lambda: highest probability first
        return sorted(pairs, key=lambda pair: pair[1], reverse=True)

    def predict(self, features):
        """Predict one leaf. Returns (label, confidence between 0 and 1)."""
        if self._model is None:
            raise ValueError("The model is not trained yet.")
        best_label, best_probability = self.rank_predictions(features)[0]
        return str(best_label), float(best_probability)

    # ------------------------------------------------------------------
    def save_model(self, path):
        """Save the trained model so we do not need to train again."""
        joblib.dump({"model": self._model, "scaler": self._scaler,
                     "labels": self._labels, "k": self.k}, path)

    def load_model(self, path):
        """Load a model saved earlier. Returns True if it worked."""
        try:
            data = joblib.load(path)
        except (OSError, EOFError, ValueError):
            return False
        self._model = data["model"]
        self._scaler = data["scaler"]
        self._labels = data["labels"]
        self.k = data["k"]
        return True

    def is_trained(self):
        return self._model is not None
