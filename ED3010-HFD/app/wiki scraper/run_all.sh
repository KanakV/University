#!/bin/bash

# --- Configuration ---
WIKI_SCRAPER_DIR="wiki_scraper"
DATA_DIR="data"
RESULT_DIR="result"

# --- Setup: Create necessary directories if they don't exist ---
echo "--- 🛠️ Setting up directories ---"
mkdir -p $DATA_DIR/plots
mkdir -p $RESULT_DIR
mkdir -p $RESULT_DIR/cv
echo "Setup complete."

# --- Step 1: Scrape TV Show Plots ---
# Takes input from data/show_names.txt and outputs JSON plots to data/plots/
echo "--- 🌐 Step 1: Running Wiki Scraper ---"
python3 $WIKI_SCRAPER_DIR/wiki_scraper.py --names-file $DATA_DIR/show_names.txt
if [ $? -ne 0 ]; then
    echo "Wiki Scraper failed. Exiting."
    exit 1
fi
echo "Plots saved to $DATA_DIR/plots/."

# --- Step 2: Single-Label Classification ---
# Takes input from data/plots/ and outputs JSONs to result/
echo "--- 🏷️ Step 2: Running Single-Label Classifier ---"
python3 $WIKI_SCRAPER_DIR/classifier_single.py --plots-dir $DATA_DIR/plots --out-dir $RESULT_DIR
if [ $? -ne 0 ]; then
    echo "Single-Label Classifier failed. Continuing to Multi-Label..."
fi
echo "Single-label results saved to $RESULT_DIR/."

# --- Step 3: Multi-Label Classification ---
# Takes input from data/plots/ and outputs JSONs to result/
echo "--- 📊 Step 3: Running Multi-Label Classifier ---"
python3 $WIKI_SCRAPER_DIR/classifier_multi.py --plots-dir $DATA_DIR/plots --out-dir $RESULT_DIR
if [ $? -ne 0 ]; then
    echo "Multi-Label Classifier failed. Continuing to Post-Processing..."
fi
echo "Multi-label results saved to $RESULT_DIR/."

# --- Step 4: Post-Processing (Generate Counts CSV) ---
# Takes input from result/ and outputs CSV to result/cv/
echo "--- 📝 Step 4: Running Post-Processing ---"
# Note: Using the multi-label flag (-m) to process the multi-label output format,
# which is the default setting you modified in post_processing.py
python3 $WIKI_SCRAPER_DIR/post_processing.py -i $RESULT_DIR -o $RESULT_DIR/cv/sentiment_counts_multi.csv --multilabel
if [ $? -ne 0 ]; then
    echo "Post-Processing failed."
    exit 1
fi
echo "Final sentiment counts saved to $RESULT_DIR/cv/sentiment_counts_multi.csv."

echo "--- ✅ All steps complete! ---"