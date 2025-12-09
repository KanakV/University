import argparse
import json
import os
import sys
import glob
from transformers import pipeline

# model for emotion/sentiment (will return scores for labels)
pipe = pipeline("text-classification", model="michellejieli/emotion_text_classifier")

PLOTS_DIR = os.path.join(os.getcwd(), "data", "plots") # Changed to use data/plots
SINGLELABEL_DIR = os.path.join(os.getcwd(), "result") # Changed to use result/

def process_file(fp, out_dir=SINGLELABEL_DIR):
    try:
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to read {fp}: {e}", file=sys.stderr)
        return False

    if not isinstance(data, list):
        print(f"Skipping {fp}: JSON root is not a list", file=sys.stderr)
        return False

    # check if file contains any plots
    has_plot = any(isinstance(item, dict) and (item.get("plot") or "").strip() for item in data)
    if not has_plot:
        print(f"Skipping {fp}: no plots found")
        return False

    results = []
    for entry in data:
        if not isinstance(entry, dict):
            results.append(entry)
            continue

        plot = (entry.get("plot") or "").strip()
        if not plot:
            entry["sentiment"] = None
            results.append(entry)
            continue

        try:
            raw = pipe(plot, truncation=True, max_length=512)
            # normalize output
            scores_list = raw[0] if isinstance(raw, list) and raw and isinstance(raw[0], list) else (raw if isinstance(raw, list) else [])
            # pick top label
            label_scores = {d.get("label"): float(d.get("score", 0.0)) for d in scores_list if d.get("label") is not None}
            if label_scores:
                top_label, top_score = max(label_scores.items(), key=lambda kv: kv[1])
            else:
                top_label, top_score = None, 0.0

            entry["sentiment"] = {"label": top_label, "score": top_score}
        except Exception as e:
            entry["sentiment"] = {"error": str(e)}

        results.append(entry)

    os.makedirs(out_dir, exist_ok=True)
    out_name = os.path.splitext(os.path.basename(fp))[0] + "_singlelabel.json"
    out_path = os.path.join(out_dir, out_name)
    try:
        with open(out_path, "w", encoding="utf-8") as of:
            json.dump(results, of, indent=2, ensure_ascii=False)
            of.flush()
            try:
                os.fsync(of.fileno())
            except Exception:
                pass
        print(f"Saved sentiment -> {out_path}")
        return True
    except Exception as e:
        print(f"Failed to write {out_path}: {e}", file=sys.stderr)
        return False

def main():
    p = argparse.ArgumentParser(description="Run single-label sentiment on plots JSON files in plots/ and save to singlelabel/")
    p.add_argument("input", nargs="?", help="Optional single JSON file to process (otherwise all .json in plots/ are processed)")
    p.add_argument("--plots-dir", help="Directory with plot JSONs", default=PLOTS_DIR)
    p.add_argument("--out-dir", help="Directory to save singlelabel outputs", default=SINGLELABEL_DIR)
    args = p.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    if args.input:
        process_file(args.input, out_dir=args.out_dir)
        return

    pattern = os.path.join(args.plots_dir, "*.json")
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"No JSON files found in {args.plots_dir}", file=sys.stderr)
        return

    for fp in files:
        print(f"Processing {fp} ...")
        process_file(fp, out_dir=args.out_dir)

if __name__ == "__main__":
    main()

