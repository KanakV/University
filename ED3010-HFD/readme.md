# Emotion-Driven Recommendation System

### Final Project – ED3010: Human Factors Design
**Indian Institute of Technology Madras**

**Authors:**
- **Kanak Varma**
- **Manan Agarwal**
- **Gururaj Thorat**

---

## 📘 Project Overview

This system addresses decision fatigue on streaming platforms by recommending content based on the user’s emotional state. It consists of two main components:
1.  **Offline Data Pipeline**: Automates the scraping and emotional analysis of TV show plots (Text2Emotion).
2.  **Interactive Web Dashboard**: A FastAPI-based web application that performs real-time emotion classification on uploaded audio (Music2Emotion) and text.

## 📂 Project Structure

```text
.
├── app/
│   ├── app.py                # [WEB] Main FastAPI application
│   ├── ui/                   # [WEB] Frontend HTML/templates
│   ├── wiki scraper/         # [PIPELINE] Scraper & analysis scripts
│   └── uploads/              # [WEB] Temp storage for uploaded files
├── data/
│   ├── show_names.txt        # [INPUT] List of shows to scrape
│   ├── plots/                # [OUTPUT] Scraped JSON plots
│   └── audio/                # Audio samples
├── result/
│   ├── cv/                   # [OUTPUT] Final CSV reports
│   └── *.json                # [OUTPUT] Classified sentiment data
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```
---
⚙️ Installation & Setup
Before running the dashboard or analysis pipeline, ensure your environment is configured correctly.

Prerequisites

Python 3.8 or higher

pip (Python Package Manager)

ffmpeg (Required for audio processing in Music2Emotion)

Dependencies Install all required libraries using the provided requirements file:

Bash

pip install -r requirements.txt
🖥️ Interactive Dashboard (Web App)
The project includes a FastAPI web interface for real-time emotion analysis of audio files and text inputs.

How to Launch
Navigate to the project root directory.

Start the server using uvicorn:

Bash

uvicorn app.app:app --reload
Open your web browser and go to:

http://127.0.0.1:8000

Features
🎵 Music Analysis: Upload .wav or .mp3 files to detect emotions using the CLAP model.

📝 Text Analysis: Type or paste plot summaries to extract sentiment using RoBERTa.

🔄 Offline Data Pipeline
Automate the scraping and processing of TV show plots for the recommendation engine.

1. Configure Inputs
Edit data/show_names.txt to include the Wikipedia titles of the shows you wish to analyze (one per line).

Example: "The Office (American TV series)"

2. Run Automation Script
Execute the master script to scrape data, classify emotions, and generate reports:

Bash

# Make script executable (first time only)
chmod +x app/wiki_scraper/run_all.sh

# Run the pipeline
./app/wiki_scraper/run_all.sh
3. Manual Execution
If you prefer running modules individually:

Scraper: python3 app/wiki_scraper/wiki_scraper.py --names-file data/show_names.txt

Classification: python3 app/wiki_scraper/classifier_multi.py --plots-dir data/plots --out-dir result

Reporting: python3 app/wiki_scraper/post_processing.py --indir result --out result/cv/sentiment_counts.csv
---

## 📝 Summary of Methods

### **Text2Emotion**
- RoBERTa-based multi-label emotion classifier  
- Processes ~900 episode summaries from 4 TV shows  
- Outputs probability distribution across 6 Ekman emotions  

### **Music2Emotion**
- Uses LAION-CLAP embeddings  
- Classifies audio into 7 emotional categories  
- Extracts features like MFCCs, tempo, timbre  

### **Emotion Mapping**
- Converts multimodal outputs to *valence* & *arousal*  
- Enables emotional similarity–based recommendations  

### **UI Prototype**
- Emotion map visualization  
- Episode browsing by emotional category  

---

## 📊 Key Results

- Correctly classified **847 episodes** using Text2Emotion  
- Achieved **72% weighted F1** on Music2Emotion 7-class model  
- Clear emotional clustering by genre  
- Multimodal ensemble improved stability  

---

## ⚠️ Limitations

- Plot summaries lack scene-level detail  
- Royalty-free music differs from cinematic soundtracks  
- Sarcasm & irony reduce text-model accuracy  
- No real-time emotion capture implemented (only framework)  

---

## 🚀 Future Scope

- Scene-level segmentation  
- Transcript-level emotion extraction  
- Visual feature analysis  
- Behavioral telemetry from remotes/smartphones  
- Cross-cultural emotion model tuning  
- Hybrid CF + emotion recommendation system  

---

## 📄 Documentation

See the full academic report: **Final Report.pdf**

---

## 🙏 Acknowledgments
We thank **Prashanna Rangan R.** for mentorship, and open-source communities behind  
HuggingFace, PyTorch, librosa, scikit-learn, and CLAP models.

