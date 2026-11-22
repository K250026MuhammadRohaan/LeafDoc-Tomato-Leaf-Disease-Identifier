# ======================================================================
# api_client.py
# LeafDoc - gets a short disease description from the Wikipedia API.
# If there is no internet, it uses a saved copy (cache), then built-in text.
# ======================================================================

import json
import os
import requests

WIKI_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"

# Our disease name -> Wikipedia page title ("healthy" has no page)
WIKI_TITLES = {
    "early_blight": "Early blight",
    "late_blight": "Late blight",
    "leaf_mold": "Leaf mold",
}

# Wikipedia likes to know who is calling, so we send this header
HEADERS = {"User-Agent": "LeafDoc-StudentProject/1.0 (FAST NUCES lab project)"}

# Last fallback text: used when there is no internet AND no cache
BUILT_IN_TEXT = {
    "healthy": "The leaf looks healthy: mostly green with no big brown or yellow patches.",
    "early_blight": "Early blight is a fungal disease that causes dark brown spots "
                    "with ring patterns on older tomato leaves.",
    "late_blight": "Late blight is a very serious disease that spreads fast and makes "
                   "dark, wet-looking patches on leaves and fruit.",
    "leaf_mold": "Leaf mold is a fungal disease that causes pale yellow spots on top "
                 "of the leaf and olive-grey mold underneath.",
}


class DiseaseInfoClient:
    """Gets disease text from Wikipedia and keeps an offline cache."""

    def __init__(self, cache_path):
        self.cache_path = cache_path
        self._cache = {}          # private dict: disease -> text
        self._load_cache()

    # ------------------------------------------------------------------
    def _load_cache(self):
        """Read the cache file if it exists."""
        if os.path.isfile(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding="utf-8") as file:
                    self._cache = json.load(file)
            except (OSError, json.JSONDecodeError):
                print("Cache file could not be read, starting with an empty cache.")
                self._cache = {}

    def _save_cache(self):
        """Write the cache dict to the JSON file."""
        try:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as file:
                json.dump(self._cache, file, indent=2)
        except OSError:
            print("Could not save the cache file.")

    # ------------------------------------------------------------------
    def get_info(self, disease):
        """Return (text, source). source is 'wikipedia', 'cache' or 'built-in'."""
        title = WIKI_TITLES.get(disease)

        # "healthy" (or unknown names) has no Wikipedia page
        if title is None:
            return BUILT_IN_TEXT.get(disease, "No description available."), "built-in"

        # Step 1: try the Wikipedia API
        try:
            url = WIKI_URL + title.replace(" ", "_")
            response = requests.get(url, headers=HEADERS, timeout=5)

            if response.status_code == 200:                 # 200 = OK
                data = response.json()
                text = data.get("extract", "")
                # skip empty text and "may refer to" pages
                if text and data.get("type") != "disambiguation":
                    self._cache[disease] = text             # save for offline use
                    self._save_cache()
                    return text, "wikipedia"
            else:
                print("Wikipedia answered with status code", response.status_code)

        except requests.exceptions.RequestException:
            print("No internet or Wikipedia is not reachable.")
        except ValueError:
            print("Wikipedia sent a reply we could not read.")

        # Step 2: saved copy
        if disease in self._cache:
            return self._cache[disease], "cache"

        # Step 3: built-in text
        return BUILT_IN_TEXT.get(disease, "No description available."), "built-in"
