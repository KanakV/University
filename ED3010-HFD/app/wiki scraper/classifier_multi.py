import argparse
import glob
import json
import os
import sys
from transformers import pipeline

# model: multi-label CardiffNLP RoBERTa emotion model
try:
    pipe = pipeline(
        "text-classification",
        model="cardiffnlp/twitter-roberta-base-emotion-multilabel-latest",
        return_all_scores=True
    )
except Exception as e:
    print(f"Failed to load model: {e}", file=sys.stderr)
    pipe = None

PLOTS_DIR = os.path.join(os.getcwd(), "data", "plots") # Assumes you run the script from the root directory.
MULTILABEL_DIR = os.path.join(os.getcwd(), "result") # Output to the 'result' directory.
MULTILABEL_THRESHOLD = 0.50

def process_file(fp, out_dir=MULTILABEL_DIR):
    if pipe is None:
        print("Model pipeline not available.", file=sys.stderr)
        return False

    try:
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to read {fp}: {e}", file=sys.stderr)
        return False

    if not isinstance(data, list):
        print(f"Skipping {fp}: JSON root is not a list", file=sys.stderr)
        return False

    # skip files without any plots
    has_plot = any(isinstance(it, dict) and (it.get("plot") or "").strip() for it in data)
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
            entry["sentiment_multilabel"] = None
            results.append(entry)
            continue

        try:
            raw = pipe(plot, truncation=True, max_length=512)

            # normalize pipeline output to flat list
            scores_list = []
            if isinstance(raw, list) and raw:
                if isinstance(raw[0], list):
                    scores_list = raw[0]
                else:
                    scores_list = raw

            label_scores = {d.get("label"): float(d.get("score", 0.0)) for d in scores_list if d.get("label") is not None}

            if label_scores:
                top_label, top_score = max(label_scores.items(), key=lambda kv: kv[1])
                labels_over_threshold = [lbl for lbl, s in label_scores.items() if s >= MULTILABEL_THRESHOLD]
            else:
                top_label, top_score, labels_over_threshold = None, 0.0, []

            entry["sentiment_multilabel"] = {
                "top_label": top_label,
                "top_score": top_score,
                "labels": label_scores,
                "labels_over_threshold": labels_over_threshold
            }
        except Exception as e:
            entry["sentiment_multilabel"] = {"error": str(e)}

        results.append(entry)

    os.makedirs(out_dir, exist_ok=True)
    out_name = os.path.splitext(os.path.basename(fp))[0] + "_multilabel.json"
    out_path = os.path.join(out_dir, out_name)
    try:
        with open(out_path, "w", encoding="utf-8") as of:
            json.dump(results, of, indent=2, ensure_ascii=False)
            of.flush()
            try:
                os.fsync(of.fileno())
            except Exception:
                pass
        print(f"Saved -> {out_path}")
        return True
    except Exception as e:
        print(f"Failed to write {out_path}: {e}", file=sys.stderr)
        return False

def main():
    p = argparse.ArgumentParser(description="Run multilabel emotion classification on all plot JSONs in plots/ and save to multilabel/")
    p.add_argument("input", nargs="?", help="Optional single JSON file to process (otherwise all .json in plots/ are processed)")
    p.add_argument("--plots-dir", help="Directory with plot JSONs", default=PLOTS_DIR)
    p.add_argument("--out-dir", help="Directory to save multilabel outputs", default=MULTILABEL_DIR)
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