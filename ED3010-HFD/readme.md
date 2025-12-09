
# Emotion-Driven Recommendation System  
### Final Project – ED3010: Human Factors Design  
**Indian Institute of Technology Madras**

**Authors:**  
- **Kanak Varma – ED23B027**  
- **Manan Agarwal – ED23B052**  
- **Gururaj Thorat – ED23B065**

---

## 📘 Project Overview

This repository contains all code, datasets, documentation, and prototypes developed for our **Emotion-Driven Recommendation System**, created as part of the **ED3010 – Human Factors Design** course.

Our project addresses **decision fatigue on streaming platforms** by building a multimodal system that recommends content based on the **user’s emotional state**.  
We integrate three complementary pipelines:

1. **Text2Emotion** — Transformer-based NLP on episode plot summaries  
2. **Music2Emotion** — Audio emotion classification using CLAP embeddings  
3. **Future Emotion Capture** — Behavioral signal–based emotion detection framework  

All outputs are mapped to **Plutchik’s Wheel of Emotions**, enabling valence–arousal–based recommendations.

---

## 📂 Repository Structure

```
ED3010-HFD/
│
├── app/                     # Code for Text2Emotion, Music2Emotion, dashboards
├── data/                    # Summaries, embeddings, metadata
├── docs/                    # Documentation files
├── requirements.txt         # Required python libraries
└── README.md
```

---

## 🔧 How to Run

### 1. Clone repository  
```bash
git clone https://github.com/KanakV/University.git
cd University/ED3010-HFD
```

### 2. Install dependencies  
```bash
pip install -r requirements.txt
```

### 3. Run Text2Emotion  
```bash
python src/text2emotion.py
```

### 4. Run Music2Emotion  
```bash
python src/music2emotion.py
```

### 5. Launch dashboard  
```bash
uvicorn app.main:app --reload
```

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

