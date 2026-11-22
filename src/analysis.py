# ======================================================================
# analysis.py
# LeafDoc - small Pandas analysis helpers (filter, group, summary).
# ======================================================================

from image_processor import FEATURE_NAMES


def filter_by_disease(table, disease):
    """Return only the rows of one disease (Pandas filtering)."""
    return table[table["label"] == disease]


def count_per_class(table):
    """Return a dict like {'healthy': 950, 'late_blight': 950, ...}."""
    counts = table["label"].value_counts()   # Pandas Series
    return {name: int(number) for name, number in counts.items()}   # normal dict with plain ints


def unique_labels(table):
    """Return the disease names as a set (a set has no duplicates)."""
    return set(table["label"])


def label_tuple(table):
    """Return the disease names as a sorted tuple (a tuple cannot be changed)."""
    return tuple(sorted(unique_labels(table)))


def pretty_names(labels):
    """Make nice names: 'early_blight' -> 'Early Blight' (uses map + lambda)."""
    return list(map(lambda name: name.replace("_", " ").title(), labels))


def high_brown_files(table, limit=30.0):
    """Return the file paths of leaves with more than `limit` % brown (uses filter)."""
    rows = table.to_dict("records")   # list of dicts, one per image
    brown_rows = filter(lambda row: row["brown_pct"] > limit, rows)
    return [row["file_path"] for row in brown_rows]


def group_summary(table):
    """Average of every feature for each disease (Pandas groupby)."""
    return table.groupby("label")[FEATURE_NAMES].mean().round(2)


def print_analysis(table):
    """Run all the small analyses and print the results."""
    print("Disease names (set):", unique_labels(table))
    print("Disease names (tuple):", label_tuple(table))
    print("Pretty names:", pretty_names(label_tuple(table)))
    print("Images per class (dict):", count_per_class(table))
    print("\nAverage features per disease:")
    print(group_summary(table))

    for disease in label_tuple(table):
        part = filter_by_disease(table, disease)
        print(disease, "-> average brown %:", round(part["brown_pct"].mean(), 2))

    print("\nLeaves with more than 30% brown:", len(high_brown_files(table)))
