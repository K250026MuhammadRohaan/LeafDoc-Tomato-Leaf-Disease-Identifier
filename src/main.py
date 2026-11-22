# ======================================================================
# main.py
# LeafDoc - the console menu. It connects all the other files together.
# Run it with:   python src/main.py
# ======================================================================

import os
from datetime import datetime

import config                                   # we use config.X so values are easy to change
from exceptions import InvalidImageError
from image_processor import ImageProcessor
from data_loader import DatasetManager
from analysis import print_analysis
from charts import ChartMaker
from models import DiseaseClassifier
from api_client import DiseaseInfoClient
from storage import CsvResultsStore, JsonResultsStore


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def create_state():
    """Make all the objects once and keep them together in a dict."""
    return {
        "processor": ImageProcessor(image_size=config.IMAGE_SIZE),
        "manager": DatasetManager(config.DATA_DIR, config.MAX_PER_CLASS),
        "classifier": DiseaseClassifier(k=config.DEFAULT_K,
                                        test_size=config.TEST_SIZE,
                                        random_state=config.RANDOM_STATE),
        "info_client": DiseaseInfoClient(config.CACHE_PATH),
        "charts": ChartMaker(config.FIGURES_DIR),
        "store": CsvResultsStore(config.HISTORY_CSV),   # history format (CSV by default)
        "table_ready": False,
    }


def ask_menu_choice(low, high):
    """Keep asking until the user types a whole number between low and high."""
    while True:
        text = input("Enter your choice: ").strip()
        try:
            choice = int(text)                       # text -> number
        except ValueError:
            print("Please type a number, not text.")
            continue
        if low <= choice <= high:
            return choice
        print("Please choose a number from", low, "to", high)


def print_menu():
    print("\n========== LeafDoc: Tomato Leaf Disease Identifier ==========")
    print("1. Dataset summary")
    print("2. Train and test the model (compare K values)")
    print("3. Diagnose a leaf photo")
    print("4. Save the three charts")
    print("5. Show diagnosis history")
    print("6. Change history format (CSV / JSON)")
    print("0. Exit")


def load_table(state):
    """Build (or load) and clean the Pandas table. Returns True if it worked."""
    if state["table_ready"]:
        return True
    try:
        state["manager"].build_table(state["processor"], cache_path=config.FEATURES_CSV)
        state["manager"].clean()
    except FileNotFoundError as error:
        print("\nERROR:", error)
        return False
    if len(state["manager"].table) < 20:
        print("\nERROR: Not enough images found to train a model.")
        return False
    state["table_ready"] = True
    return True


def make_sure_model_is_ready(state):
    """Load the saved model, or train a new one. Returns True if the model is ready."""
    classifier = state["classifier"]
    if classifier.is_trained():
        return True
    if classifier.load_model(config.MODEL_PATH):
        print("Loaded saved model (K =", classifier.k, ")")
        return True
    print("No saved model found, training one now...")
    if not load_table(state):
        return False
    classifier.train(state["manager"].table)
    classifier.save_model(config.MODEL_PATH)
    return True


# ----------------------------------------------------------------------
# Menu options
# ----------------------------------------------------------------------
def option_dataset_summary(state):
    if not load_table(state):
        return
    state["manager"].summary()
    print()
    print_analysis(state["manager"].table)


def option_train_and_test(state):
    if not load_table(state):
        return
    classifier = state["classifier"]
    classifier.k = config.DEFAULT_K
    classifier.train(state["manager"].table)          # split + train

    print("\nComparing different K values on the same split...")
    results = classifier.compare_k_values(config.K_VALUES)

    # pick the K with the best accuracy and train again with it
    best_k = max(results, key=results.get)
    classifier.k = best_k
    classifier.train()
    classifier.save_model(config.MODEL_PATH)

    accuracy, matrix, report = classifier.evaluate()
    print("\nFinal model: K =", best_k)
    print("Accuracy on unseen test images:", round(accuracy * 100, 2), "%")
    print(report)
    state["last_matrix"] = matrix                      # saved for the chart option
    if accuracy < 0.70:
        print("Note: accuracy is below our 70% target. Colour alone may confuse some diseases.")


def option_diagnose(state):
    if not make_sure_model_is_ready(state):
        return

    path = input("Type the full path of the leaf photo (.jpg): ").strip()
    path = path.strip('"').strip("'")                  # remove quotes if the path was pasted with them

    try:
        features = state["processor"].get_features(path)
    except InvalidImageError as error:
        print("\nProblem with the image:", error)
        return

    label, confidence = state["classifier"].predict(features)
    text, source = state["info_client"].get_info(label)

    print("\n------------- RESULT -------------")
    print("Disease    :", label.replace("_", " ").title())
    print("Confidence :", round(confidence * 100, 1), "%")
    if confidence < 0.6:
        print("(The model is not very sure. Please ask an expert.)")
    print("\nAbout the disease (source:", source + "):")
    print(text)
    print("\nOther possibilities:")
    for name, probability in state["classifier"].rank_predictions(features):
        print("  ", name, "-", round(probability * 100, 1), "%")
    print("\nNote: LeafDoc is only a first check. It is not a replacement for an expert.")

    # save the result in the history file
    record = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "image_path": path,
        "disease": label,
        "confidence": round(confidence, 3),
    }
    state["store"].save_result(record)
    print("Result saved to", state["store"].get_path())


def option_save_charts(state):
    if not load_table(state):
        return
    charts = state["charts"]
    table = state["manager"].table
    charts.class_counts_chart(table)
    charts.brown_boxplot(table)

    # the confusion matrix needs a trained and tested model
    if "last_matrix" not in state:
        if not state["classifier"].is_trained() or state["classifier"].X_test is None:
            state["classifier"].train(table)
        _, state["last_matrix"], _ = state["classifier"].evaluate()
    labels = sorted(state["manager"].class_names)
    charts.confusion_matrix_chart(state["last_matrix"], labels)


def option_show_history(state):
    history = state["store"].load_history()
    if len(history) == 0:
        print("\nNo diagnoses saved yet.")
        return
    print("\nDiagnosis history (", len(history), "entries ):")
    for entry in history:
        print(entry["time"], "|", entry["disease"], "|", entry["confidence"], "|", entry["image_path"])


def option_change_format(state):
    print("\n1. CSV file")
    print("2. JSON file")
    choice = ask_menu_choice(1, 2)
    # Both classes have the same method names, so the rest of the program does not care which one
    if choice == 1:
        state["store"] = CsvResultsStore(config.HISTORY_CSV)
    else:
        state["store"] = JsonResultsStore(config.HISTORY_JSON)
    print("History will now be saved in", state["store"].get_path())


# ----------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------
def run_menu():
    state = create_state()
    while True:
        print_menu()
        choice = ask_menu_choice(0, 6)
        if choice == 0:
            print("Goodbye!")
            break
        elif choice == 1:
            option_dataset_summary(state)
        elif choice == 2:
            option_train_and_test(state)
        elif choice == 3:
            option_diagnose(state)
        elif choice == 4:
            option_save_charts(state)
        elif choice == 5:
            option_show_history(state)
        elif choice == 6:
            option_change_format(state)


if __name__ == "__main__":
    run_menu()
