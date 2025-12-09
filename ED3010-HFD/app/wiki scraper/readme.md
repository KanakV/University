# TV Plot Sentiment Analysis Pipeline

This project automates the process of scraping TV show episode plots from Wikipedia, analyzing their emotional content using NLP models (Single-Label and Multi-Label), and generating statistical reports.

## 📂 Project Structure

The project is designed to be run from the root directory.

```text
.
├── data/
│   ├── show_names.txt         # [INPUT] List of TV shows to scrape (user created)
│   └── plots/                 # [OUTPUT] Scraped JSON plots are saved here
├── result/
│   ├── cv/                    # [OUTPUT] Final CSV reports
│   ├── *.json                 # [OUTPUT] Classified sentiment JSON files
├── wiki_scraper/
│   ├── wiki_scraper.py        # Scrapes Wikipedia for episode plots
│   ├── classifier_single.py   # HuggingFace Single-Label Sentiment Classifier
│   ├── classifier_multi.py    # HuggingFace Multi-Label Emotion Classifier
│   ├── post_processing.py     # Aggregates results into CSVs
│   └── run_all.sh             # Master script to run the full pipeline
└── requirements.txt           # Python dependencies