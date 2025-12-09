import argparse
import json
import os
import glob
import csv
from collections import Counter

# SINGLE LABEL
# DEFAULT_DIR = os.path.join(os.getcwd(), "singlelabel")
# DEFAULT_OUT = os.path.join(DEFAULT_DIR, "sentiment_counts_single.csv")

# MULTI LABEL
DEFAULT_DIR = os.path.join(os.getcwd(), "result", "plots") # Changed: Now reads input JSONs from 'result'
DEFAULT_OUT = os.path.join(os.getcwd(), "result", "csv", "sentiment_counts_multi.csv") # Changed: Now saves output CSV to 'result/cv'
...
def extract_labels_from_entry(entry, multilabel=False):
    s = entry.get("sentiment")
    if not s:
        return [] if multilabel else [None]

    # single-label formats
    if isinstance(s, dict):
        # older singlelabel: {"label": ..., "score": ...}
        if "label" in s and s["label"] is not None:
            return [s["label"]] if not multilabel else [s["label"]]
        # newer singlelabel/multilabel: {"top_label": ..., "labels_over_threshold": [...], "labels": {...}}
        if "top_label" in s and s["top_label"] is not None and not multilabel:
            return [s["top_label"]]
        if multilabel:
            if "labels_over_threshold" in s and isinstance(s["labels_over_threshold"], list) and s["labels_over_threshold"]:
                return s["labels_over_threshold"]
            # fallback to labels dict keys above  threshold
            if "labels" in s and isinstance(s["labels"], dict):
                return [k for k,v in s["labels"].items() if v >= 0.5]  # arbitrary fallback threshold
    return [] if multilabel else [None]

def process_dir(indir, out_csv, multilabel=False):
    pattern = os.path.join(indir, "*.json")
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"No JSON files found in {indir}")
        return

    counter = Counter()
    total_episodes = 0
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to read {fp}: {e}")
            continue
        if not isinstance(data, list):
            continue

        for entry in data:
            total_episodes += 1
            labels = extract_labels_from_entry(entry, multilabel=multilabel)
            if not labels:
                counter["<no_label>"] += 1
            else:
                for lbl in labels:
                    counter[lbl if lbl is not None else "<no_label>"] += 1

    # write CSV
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(["emotion", "count"])
        for label, cnt in counter.most_common():
            writer.writerow([label, cnt])

    print(f"Processed {total_episodes} episodes from {len(files)} files. Saved counts -> {out_csv}")

def main():
    p = argparse.ArgumentParser(description="Summarize sentiment labels from singlelabel JSON files into CSV")
    p.add_argument("--indir", "-i", help="Directory with singlelabel JSON files", default=DEFAULT_DIR)
    p.add_argument("--out", "-o", help="Output CSV path", default=DEFAULT_OUT)
    p.add_argument("--multilabel", "-m", action="store_true", help="If set, count all labels in labels_over_threshold (multi-label). Otherwise use top/label only.")
    args = p.parse_args()

    process_dir(args.indir, args.out, multilabel=args.multilabel)

if __name__ == "__main__":
    main()