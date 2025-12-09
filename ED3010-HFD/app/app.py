"""
app.py
Clean, fixed FastAPI app for Music + Episode Emotion classification.

Key features:
- Proper CLAP preprocessing for audio.
- Robust WAV conversion using ffmpeg (with fallback).
- Local RoBERTa GoEmotions model support (falls back to keywords if missing).
- Endpoints: GET / (UI), POST /analyze/ (Audio), POST /analyze_text/ (Text).
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional

import numpy as np
import soundfile as sf
import torch
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    ClapModel,
    ClapProcessor,
)

# -----------------------
# Configuration / Paths
# -----------------------
# This resolves to the 'app' directory
BASE_DIR = Path(__file__).resolve().parent

# Define structure based on the project README
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = BASE_DIR / "uploads"
MODEL_DIR = BASE_DIR / "models" / "roberta_goemotions" 

# Ensure directories exist
for p in (TEMPLATES_DIR, STATIC_DIR, UPLOAD_DIR, MODEL_DIR.parent):
    p.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Music + Episode Emotion Classifier")

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Setup Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# -----------------------
# Helper: ffmpeg converter
# -----------------------
def convert_to_wav_48k(src_path: str) -> str:
    """
    Convert any audio file to 48kHz WAV (PCM 16-bit) using ffmpeg.
    Returns path to the converted wav file (temp file).
    Requires ffmpeg binary available in PATH.
    """
    dst_fd, dst_path = tempfile.mkstemp(suffix=".wav")
    os.close(dst_fd)
    dst_path = str(dst_path)
    cmd = [
        "ffmpeg",
        "-y",
        "-v", "error",
        "-i", str(src_path),
        "-ar", "48000",
        "-ac", "1",
        "-sample_fmt", "s16",
        dst_path,
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return dst_path
    except subprocess.CalledProcessError:
        # fallback: try with soundfile (may not resample correctly if libsndfile doesn't support it)
        try:
            data, sr = sf.read(src_path, always_2d=True)
            mono = data.mean(axis=1)
            sf.write(dst_path, mono, 48000, subtype="PCM_16")
            return dst_path
        except Exception as exc:
            if os.path.exists(dst_path):
                try:
                    os.remove(dst_path)
                except Exception:
                    pass
            raise RuntimeError(f"Failed to convert audio file to WAV: {exc}")

# -----------------------
# Load Models
# -----------------------
print("Loading CLAP audio model...")
# Downloads model from HuggingFace if not cached
clap_processor = ClapProcessor.from_pretrained("laion/clap-htsat-unfused")
clap_model = ClapModel.from_pretrained("laion/clap-htsat-unfused")
clap_model.eval()
print("CLAP ready.")

USE_LOCAL_TEXT_MODEL = False
text_tokenizer = None
text_model = None
TEXT_MODEL_LABELS = []

try:
    print(f"Attempting to load local RoBERTa GoEmotions model from {MODEL_DIR}...")
    text_tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    text_model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
    text_model.eval()
    
    # Explicit label order for SamLowe/roberta-base-go_emotions
    TEXT_MODEL_LABELS = [
        "admiration", "amusement", "anger", "annoyance", "approval", "caring", 
        "confusion", "curiosity", "desire", "disappointment", "disapproval", 
        "disgust", "embarrassment", "excitement", "fear", "gratitude", "grief", 
        "joy", "love", "nervousness", "optimism", "pride", "realization", 
        "relief", "remorse", "sadness", "surprise", "neutral",
    ]
    USE_LOCAL_TEXT_MODEL = True
    print("Local RoBERTa GoEmotions loaded.")
except Exception as exc:
    print("Local RoBERTa GoEmotions not available; falling back to simple keyword heuristic.")
    # print("Reason:", exc)
    text_tokenizer = None
    text_model = None
    USE_LOCAL_TEXT_MODEL = False

# Audio emotion labels for zero-shot classification
AUDIO_EMOTIONS = ["happy", "sad", "angry", "calm", "fear", "surprise", "love", "neutral"]

# In-memory history
results_history = []
text_results_history = []

# -----------------------
# Utilities
# -----------------------
def read_wav_file(path: str) -> Tuple[np.ndarray, int]:
    """Read wav with soundfile and return mono 1-D numpy array (float32) and sample rate."""
    data, sr = sf.read(path, dtype="float32", always_2d=False)
    # If stereo, average to mono
    if isinstance(data, np.ndarray) and data.ndim > 1:
        data = np.mean(data, axis=1)
    data = np.asarray(data, dtype=np.float32)
    return data, sr

def compute_clap_audio_embedding(audio_np: np.ndarray, sampling_rate: int) -> torch.Tensor:
    """Compute CLAP audio embedding."""
    # ClapProcessor expects 'audios' for audio input
    inputs = clap_processor(audios=audio_np, sampling_rate=sampling_rate, return_tensors="pt")
    with torch.no_grad():
        audio_emb = clap_model.get_audio_features(**inputs)
    return audio_emb

def compute_clap_text_embeddings(texts: list[str]) -> torch.Tensor:
    """Compute CLAP text embeddings."""
    inputs = clap_processor(text=texts, return_tensors="pt", padding=True)
    with torch.no_grad():
        text_emb = clap_model.get_text_features(**inputs)
    return text_emb

def classify_text_emotions(text: str) -> Tuple[str, dict]:
    """Classify text using local model or keyword heuristic."""
    if USE_LOCAL_TEXT_MODEL and text_model is not None and text_tokenizer is not None:
        inputs = text_tokenizer(text, truncation=True, padding=True, return_tensors="pt")
        with torch.no_grad():
            outputs = text_model(**inputs)
        logits = outputs.logits.squeeze(0).cpu().numpy()
        
        # Softmax for probabilities
        probs = np.exp(logits - np.max(logits))
        probs = probs / probs.sum()
        
        top_idx = int(np.argmax(probs))
        top_emotion = TEXT_MODEL_LABELS[top_idx] if top_idx < len(TEXT_MODEL_LABELS) else "neutral"
        scores = {TEXT_MODEL_LABELS[i]: float(probs[i]) for i in range(len(TEXT_MODEL_LABELS))}
        return top_emotion, scores
    else:
        # Fallback Heuristic
        t = text.lower()
        keywords = {
            "happy": ["happy", "joy", "delight", "smile", "cheerful", "elated"],
            "sad": ["sad", "sorrow", "tears", "depressed", "mourn"],
            "angry": ["angry", "rage", "furious", "hate"],
            "fear": ["fear", "scared", "terrified", "afraid"],
            "surprise": ["surprise", "shocked", "astonish"],
            "love": ["love", "romance", "affection"],
            "calm": ["calm", "peaceful", "relaxed"],
        }
        scores = {emo: 0.0 for emo in AUDIO_EMOTIONS}
        for emo, kw_list in keywords.items():
            matches = sum(t.count(kw) for kw in kw_list)
            if emo in scores:
                scores[emo] = float(matches)
        
        total = sum(scores.values()) or 1.0
        normalized = {k: v / total for k, v in scores.items()}
        top = max(normalized.items(), key=lambda kv: kv[1])[0]
        return top, normalized

# -----------------------
# Routes
# -----------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the dashboard UI."""
    tpl_path = TEMPLATES_DIR / "index.html"
    if tpl_path.exists():
        return templates.TemplateResponse("index.html", {
            "request": request,
            "history_music": results_history,
            "history_text": text_results_history,
            "recommendations": []
        })
    else:
        # Fallback simple UI if template is missing
        return HTMLResponse("""
        <html>
            <body style="font-family: sans-serif; padding: 2rem;">
                <h1>Emotion Classifier Dashboard</h1>
                <p><i>Template not found in app/templates/index.html</i></p>
                <hr>
                <h3>API Endpoints</h3>
                <ul>
                    <li><b>POST /analyze/</b>: Upload audio file for classification</li>
                    <li><b>POST /analyze_text/</b>: Upload text file for classification</li>
                </ul>
            </body>
        </html>
        """)

@app.post("/analyze/")
async def analyze_audio(file: UploadFile = File(...)):
    """Audio Emotion Classification Endpoint"""
    file_path: Optional[str] = None
    wav_path: Optional[str] = None
    try:
        # 1. Save uploaded file
        fd, tmp_path = tempfile.mkstemp(suffix=Path(file.filename).suffix)
        os.close(fd)
        file_path = tmp_path
        with open(file_path, "wb") as dst:
            dst.write(await file.read())

        # 2. Convert to consistent WAV format
        wav_path = convert_to_wav_48k(file_path)

        # 3. Read and Preprocess
        audio_np, sr = read_wav_file(wav_path)
        if audio_np is None or audio_np.size == 0:
            raise RuntimeError("Failed to read audio data.")

        # 4. Get Embeddings (Audio & Text Labels)
        audio_emb = compute_clap_audio_embedding(audio_np, sr)
        text_emb = compute_clap_text_embeddings(AUDIO_EMOTIONS)

        # 5. Compute Similarity
        audio_norm = torch.nn.functional.normalize(audio_emb, p=2, dim=-1)
        text_norm = torch.nn.functional.normalize(text_emb, p=2, dim=-1)
        sims = torch.matmul(audio_norm, text_norm.T).squeeze(0).cpu().numpy()

        idx = int(np.argmax(sims))
        top_emotion = AUDIO_EMOTIONS[idx]
        scores = {AUDIO_EMOTIONS[i]: float(sims[i]) for i in range(len(AUDIO_EMOTIONS))}

        # 6. Response
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            "filename": file.filename,
            "emotion": top_emotion,
            "scores": scores,
            "timestamp": timestamp,
        }
        results_history.insert(0, record)
        return JSONResponse(record)

    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)
    finally:
        # Cleanup temp files
        for p in (file_path, wav_path):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

@app.post("/analyze_text/")
async def analyze_text(file: UploadFile = File(...)):
    """Text Emotion Classification Endpoint"""
    try:
        raw = (await file.read()).decode("utf-8", errors="replace")
        top_emotion, scores = classify_text_emotions(raw)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            "filename": file.filename,
            "emotion": top_emotion,
            "scores": scores,
            "timestamp": timestamp,
        }
        text_results_history.insert(0, record)
        return JSONResponse(record)
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


###################################################################################
# In case previous does not work out uncomment and run the following code instead #
# Till the END marker                                                             # 
###################################################################################


# """
# app.py
# Clean, fixed FastAPI app for Music + Episode Emotion classification.

# Key fixes:
# - Proper CLAP preprocessing: use `audios=` with ClapProcessor and pass **inputs to ClapModel.get_audio_features(...)
# - Robust WAV conversion and resampling to 48000 Hz
# - Mono conversion, dtype normalization (float32)
# - Safe torch.no_grad() use
# - Text classifier fallback kept (local RoBERTa GoEmotions if available)
# - Same endpoints as original: GET / (serves index.html), POST /analyze/ (audio), POST /analyze_text/ (text)
# """

# from __future__ import annotations

# import os
# import subprocess
# import tempfile
# from datetime import datetime
# from pathlib import Path
# from typing import Tuple, Optional

# import numpy as np
# import soundfile as sf
# import torch
# from fastapi import FastAPI, File, UploadFile, Request
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from transformers import (
#     AutoTokenizer,
#     AutoModelForSequenceClassification,
#     ClapModel,
#     ClapProcessor,
# )

# # -----------------------
# # Configuration / Paths
# # -----------------------
# BASE_DIR = Path(__file__).resolve().parent
# TEMPLATES_DIR = BASE_DIR / "templates"
# STATIC_DIR = BASE_DIR / "static"
# UPLOAD_DIR = BASE_DIR / "uploads"
# MODEL_DIR = BASE_DIR / "models" / "roberta_goemotions"  # local text model path (if available)

# for p in (TEMPLATES_DIR, STATIC_DIR, UPLOAD_DIR, MODEL_DIR.parent):
#     p.mkdir(parents=True, exist_ok=True)

# app = FastAPI(title="Music + Episode Emotion Classifier")
# app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
# templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# # -----------------------
# # Helper: ffmpeg converter
# # -----------------------
# def convert_to_wav_48k(src_path: str) -> str:
#     """
#     Convert any audio file to 48kHz WAV (PCM 16-bit) using ffmpeg.
#     Returns path to the converted wav file (temp file).
#     Requires ffmpeg binary available in PATH.
#     """
#     dst_fd, dst_path = tempfile.mkstemp(suffix=".wav")
#     os.close(dst_fd)
#     dst_path = str(dst_path)
#     cmd = [
#         "ffmpeg",
#         "-y",
#         "-v", "error",
#         "-i", str(src_path),
#         "-ar", "48000",
#         "-ac", "1",
#         "-sample_fmt", "s16",
#         dst_path,
#     ]
#     try:
#         subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#         return dst_path
#     except subprocess.CalledProcessError:
#         # fallback: try with soundfile (may not resample)
#         try:
#             data, sr = sf.read(src_path, always_2d=True)
#             mono = data.mean(axis=1)
#             sf.write(dst_path, mono, 48000, subtype="PCM_16")
#             return dst_path
#         except Exception as exc:
#             if os.path.exists(dst_path):
#                 try:
#                     os.remove(dst_path)
#                 except Exception:
#                     pass
#             raise RuntimeError(f"Failed to convert audio file to WAV: {exc}")

# # -----------------------
# # Load models
# # -----------------------
# print("Loading CLAP audio model...")
# clap_processor = ClapProcessor.from_pretrained("laion/clap-htsat-unfused")
# clap_model = ClapModel.from_pretrained("laion/clap-htsat-unfused")
# clap_model.eval()
# print("CLAP ready.")

# USE_LOCAL_TEXT_MODEL = False
# text_tokenizer = None
# text_model = None
# TEXT_MODEL_LABELS = []

# try:
#     print("Attempting to load local RoBERTa GoEmotions model...")
#     text_tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
#     text_model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
#     text_model.eval()
#     # explicit label order (SamLowe/roberta-base-go_emotions)
#     TEXT_MODEL_LABELS = [
#         "admiration",
#         "amusement",
#         "anger",
#         "annoyance",
#         "approval",
#         "caring",
#         "confusion",
#         "curiosity",
#         "desire",
#         "disappointment",
#         "disapproval",
#         "disgust",
#         "embarrassment",
#         "excitement",
#         "fear",
#         "gratitude",
#         "grief",
#         "joy",
#         "love",
#         "nervousness",
#         "optimism",
#         "pride",
#         "realization",
#         "relief",
#         "remorse",
#         "sadness",
#         "surprise",
#         "neutral",
#     ]
#     USE_LOCAL_TEXT_MODEL = True
#     print("Local RoBERTa GoEmotions loaded.")
# except Exception as exc:
#     print("Local RoBERTa GoEmotions not available; falling back to simple keyword heuristic for text.")
#     print("Reason:", exc)
#     text_tokenizer = None
#     text_model = None
#     USE_LOCAL_TEXT_MODEL = False

# # A short set of audio "emotion" labels used to compare against
# # Keep it compact so we can compute text embeddings via CLAP as well.
# AUDIO_EMOTIONS = ["happy", "sad", "angry", "calm", "fear", "surprise", "love", "neutral"]

# # In-memory history buffers (simple)
# results_history = []
# text_results_history = []

# # -----------------------
# # Utilities
# # -----------------------
# def read_wav_file(path: str) -> Tuple[np.ndarray, int]:
#     """Read wav with soundfile and return mono 1-D numpy array (float32) and sample rate."""
#     data, sr = sf.read(path, dtype="float32", always_2d=False)
#     # if stereo (2D) reduce to mono by averaging channels
#     if isinstance(data, np.ndarray) and data.ndim > 1:
#         data = np.mean(data, axis=1)
#     # ensure float32 numpy array
#     data = np.asarray(data, dtype=np.float32)
#     return data, sr

# def compute_clap_audio_embedding(audio_np: np.ndarray, sampling_rate: int) -> torch.Tensor:
#     """
#     Given a 1-D numpy array (float32) and sampling rate, return CLAP audio embedding tensor.
#     IMPORTANT: ClapProcessor expects the kwarg name `audios=` (plural) for audio inputs.
#     """
#     # ClapProcessor accepts either list/ndarray. We pass a single example (1-D array).
#     inputs = clap_processor(audios=audio_np, sampling_rate=sampling_rate, return_tensors="pt")
#     with torch.no_grad():
#         # Correct usage: pass preprocessed inputs as keyword args to get_audio_features(...)
#         audio_emb = clap_model.get_audio_features(**inputs)
#     # audio_emb shape: (batch_size, emb_dim) -> we return the tensor
#     return audio_emb

# def compute_clap_text_embeddings(texts: list[str]) -> torch.Tensor:
#     """
#     Given a list of text strings, return CLAP text embeddings (tensor).
#     We'll use ClapProcessor(text=..., return_tensors="pt") and ClapModel.get_text_features(**inputs).
#     """
#     inputs = clap_processor(texts, return_tensors="pt", padding=True)
#     with torch.no_grad():
#         text_emb = clap_model.get_text_features(**inputs)
#     return text_emb

# def classify_text_emotions(text: str) -> Tuple[str, dict]:
#     """
#     Classify text using local RoBERTa GoEmotions if available, otherwise a naive keyword heuristic.
#     Returns (top_emotion, scores_dict).
#     """
#     if USE_LOCAL_TEXT_MODEL and text_model is not None and text_tokenizer is not None:
#         inputs = text_tokenizer(text, truncation=True, padding=True, return_tensors="pt")
#         with torch.no_grad():
#             outputs = text_model(**inputs)
#         logits = outputs.logits.squeeze(0).cpu().numpy()
#         # If model is multi-label, we could apply sigmoid, but SamLowe's model returns logits for 28 classes.
#         # We'll softmax for single-label top emotion (simple)
#         probs = np.exp(logits - np.max(logits))
#         probs = probs / probs.sum()
#         top_idx = int(np.argmax(probs))
#         top_emotion = TEXT_MODEL_LABELS[top_idx] if top_idx < len(TEXT_MODEL_LABELS) else "neutral"
#         scores = {TEXT_MODEL_LABELS[i]: float(probs[i]) for i in range(len(TEXT_MODEL_LABELS))}
#         return top_emotion, scores
#     else:
#         # naive heuristic
#         t = text.lower()
#         keywords = {
#             "happy": ["happy", "joy", "delight", "smile", "cheerful", "elated"],
#             "sad": ["sad", "sorrow", "tears", "depressed", "mourn"],
#             "angry": ["angry", "rage", "furious", "hate"],
#             "fear": ["fear", "scared", "terrified", "afraid"],
#             "surprise": ["surprise", "shocked", "astonish"],
#             "love": ["love", "romance", "affection"],
#             "calm": ["calm", "peaceful", "relaxed"],
#         }
#         scores = {}
#         for emo in AUDIO_EMOTIONS:
#             scores[emo] = 0.0
#         for emo, kw_list in keywords.items():
#             matches = sum(t.count(kw) for kw in kw_list)
#             if emo in scores:
#                 scores[emo] = float(matches)
#         # Tie-breaking and normalization
#         total = sum(scores.values()) or 1.0
#         normalized = {k: v / total for k, v in scores.items()}
#         top = max(normalized.items(), key=lambda kv: kv[1])[0]
#         return top, normalized

# # -----------------------
# # Routes
# # -----------------------
# @app.get("/", response_class=HTMLResponse)
# async def index(request: Request):
#     # Serve index.html from templates if available, otherwise a minimal page
#     tpl_path = TEMPLATES_DIR / "index.html"
#     if tpl_path.exists():
#         return templates.TemplateResponse("index.html", {"request": request,
#                                                          "history_music": results_history,
#                                                          "history_text": text_results_history,
#                                                          "recommendations": []})
#     else:
#         html = "<html><body><h1>Emotion Classifier</h1><p>Upload via /analyze/ or /analyze_text/</p></body></html>"
#         return HTMLResponse(html)

# @app.post("/analyze/")
# async def analyze_audio(file: UploadFile = File(...)):
#     """
#     Accepts form file upload (audio). Saves file, converts to 48k WAV mono, then:
#       - reads WAV
#       - computes CLAP audio embedding
#       - computes CLAP text embeddings for AUDIO_EMOTIONS
#       - computes cosine similarities and returns top emotion + scores
#     """
#     # save uploaded file to disk
#     file_path: Optional[str] = None
#     wav_path: Optional[str] = None
#     try:
#         # Write incoming file to a temp file
#         fd, tmp_path = tempfile.mkstemp(suffix=Path(file.filename).suffix)
#         os.close(fd)
#         file_path = tmp_path
#         with open(file_path, "wb") as dst:
#             content = await file.read()
#             dst.write(content)

#         # Convert to WAV 48k mono
#         wav_path = convert_to_wav_48k(file_path)

#         # Read wav into numpy array (float32)
#         audio_np, sr = read_wav_file(wav_path)  # 1-D float32 array, sr should be 48000
#         if audio_np is None or audio_np.size == 0:
#             raise RuntimeError("Failed to read audio from converted WAV file.")

#         # Compute CLAP audio embedding
#         audio_emb = compute_clap_audio_embedding(audio_np, sr)  # tensor (1, dim)

#         # Compute CLAP text embeddings for predefined AUDIO_EMOTIONS
#         text_emb = compute_clap_text_embeddings(AUDIO_EMOTIONS)  # tensor (len, dim)

#         # Normalize and compute cosine similarities
#         audio_norm = torch.nn.functional.normalize(audio_emb, p=2, dim=-1)  # (1, dim)
#         text_norm = torch.nn.functional.normalize(text_emb, p=2, dim=-1)    # (N, dim)
#         sims = torch.matmul(audio_norm, text_norm.T).squeeze(0).cpu().numpy()  # (N,)

#         idx = int(np.argmax(sims))
#         top_emotion = AUDIO_EMOTIONS[idx]
#         scores = {AUDIO_EMOTIONS[i]: float(sims[i]) for i in range(len(AUDIO_EMOTIONS))}

#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         record = {
#             "filename": file.filename,
#             "emotion": top_emotion,
#             "scores": scores,
#             "timestamp": timestamp,
#         }
#         # push to history (most recent first)
#         results_history.insert(0, record)
#         # return result
#         return JSONResponse(record)

#     except Exception as exc:
#         # return the error message for debugging in UI
#         return JSONResponse({"error": str(exc)})
#     finally:
#         # cleanup
#         for p in (file_path, wav_path):
#             if p and os.path.exists(p):
#                 try:
#                     os.remove(p)
#                 except Exception:
#                     pass

# @app.post("/analyze_text/")
# async def analyze_text(file: UploadFile = File(...)):
#     """
#     Accepts a text file (.txt), reads content, classifies via local text model if present,
#     otherwise uses a heuristic.
#     Returns top emotion and a scores dict.
#     """
#     try:
#         raw = (await file.read()).decode("utf-8", errors="replace")
#         top_emotion, scores = classify_text_emotions(raw)

#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         record = {
#             "filename": file.filename,
#             "emotion": top_emotion,
#             "scores": scores,
#             "timestamp": timestamp,
#         }
#         text_results_history.insert(0, record)
#         return JSONResponse(record)
#     except Exception as exc:
#         return JSONResponse({"error": str(exc)})

# # -----------------------
# # Run server
# # -----------------------
# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)






###################################################################################
##################################### END #########################################
###################################################################################





# """
# Main FastAPI application providing Netflix-inspired UI for music and text emotion
# analysis. Music emotions use CLAP, text emotions prefer the local GoEmotions
# (28-label) transformer model stored in ./models/goemotions, and fall back to a
# keyword heuristic if the model is unavailable.
# """

# from __future__ import annotations

# import math
# import os
# import subprocess
# import tempfile
# from datetime import datetime
# from pathlib import Path

# import numpy as np
# import soundfile as sf
# import torch
# from fastapi import FastAPI, File, Request, UploadFile
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from transformers import (
#     AutoTokenizer,
#     AutoModelForSequenceClassification,
#     ClapModel,
#     ClapProcessor,
# )

# # ──────────────────────────────
# # Paths and FastAPI setup
# # ──────────────────────────────

# BASE_DIR = Path(__file__).resolve().parent
# TEMPLATES_DIR = BASE_DIR / "templates"
# STATIC_DIR = BASE_DIR / "static"
# UPLOAD_DIR = BASE_DIR / "uploads"
# MODEL_DIR = BASE_DIR / "models" / "goemotions"   # << LOCAL MODEL PATH

# for folder in (TEMPLATES_DIR, STATIC_DIR, UPLOAD_DIR, MODEL_DIR.parent):
#     folder.mkdir(parents=True, exist_ok=True)

# app = FastAPI(title="Music + Episode Emotion Classifier (Local GoEmotions)")
# app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
# templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
# try:
#     templates.env.auto_reload = True
#     templates.env.cache = {}
# except Exception:
#     pass

# # ──────────────────────────────
# # Load models (local preferred)
# # ──────────────────────────────

# print("Loading CLAP audio model...")
# clap_processor = ClapProcessor.from_pretrained("laion/clap-htsat-unfused")
# clap_model = ClapModel.from_pretrained("laion/clap-htsat-unfused")
# clap_model.eval()
# print("CLAP ready.")

# USE_LOCAL_TEXT_MODEL = False
# TEXT_MODEL_LABELS: list[str] = []

# try:
#     print("Loading local GoEmotions text model (27 labels)...")

#     # This path must contain the downloaded joeddav/distilbert-base-uncased-go-emotions files
#     text_tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
#     text_model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
#     text_model.eval()

#     TEXT_MODEL_LABELS = [
#         "admiration","amusement","anger","annoyance","approval","caring","confusion",
#         "curiosity","desire","disappointment","disapproval","disgust","embarrassment",
#         "excitement","fear","gratitude","grief","joy","love","nervousness","optimism",
#         "pride","realization","relief","remorse","sadness","surprise"
#     ]

#     USE_LOCAL_TEXT_MODEL = True
#     print("GoEmotions model ready (LOCAL).")

# except Exception as exc:
#     print("Local model not found. Using keyword fallback.")
#     print(exc)
#     text_tokenizer = None
#     text_model = None


# TEXT_EMOTION_KEYWORDS = {
#     "happy": ["happy", "joy", "delight", "smile", "cheer", "laugh"],
#     "sad": ["sad", "cry", "tear", "lonely", "blue", "downcast"],
#     "angry": ["angry", "rage", "furious", "mad", "annoyed", "irritated"],
#     "calm": ["calm", "peace", "serene", "relaxed", "quiet", "still"],
#     "fear": ["scared", "afraid", "fear", "terrified", "nervous", "anxious"],
#     "surprise": ["surprised", "stunned", "shocked", "amazed", "astonished"],
#     "love": ["love", "romance", "affection", "cherish", "adore", "heart"],
# }
# DEFAULT_TEXT_EMOTION = "calm"

# AUDIO_EMOTIONS = ["happy", "sad", "energetic", "calm", "romantic", "angry", "relaxed"]

# # ──────────────────────────────
# # In-memory histories
# # ──────────────────────────────

# results_history: list[dict] = []
# text_results_history: list[dict] = []

# # ──────────────────────────────
# # Helpers
# # ──────────────────────────────

# def convert_to_wav_48k(input_path: str) -> str:
#     output_path = tempfile.mktemp(suffix=".wav")
#     completed = subprocess.run(
#         ["ffmpeg", "-y", "-i", input_path, "-ar", "48000", "-ac", "1", output_path],
#         stdout=subprocess.DEVNULL,
#         stderr=subprocess.DEVNULL,
#         check=False,
#     )
#     if completed.returncode != 0 or not os.path.exists(output_path):
#         raise RuntimeError("FFmpeg conversion failed")
#     return output_path


# def emotion_similarity(scores1: dict, scores2: dict) -> float:
#     keys = set(scores1.keys()) | set(scores2.keys())
#     v1 = [scores1.get(k, 0.0) for k in keys]
#     v2 = [scores2.get(k, 0.0) for k in keys]
#     dot = sum(a * b for a, b in zip(v1, v2))
#     n1 = math.sqrt(sum(a * a for a in v1))
#     n2 = math.sqrt(sum(b * b for b in v2))
#     if n1 == 0 or n2 == 0:
#         return 0.0
#     return dot / (n1 * n2)


# def classify_text_emotions(text: str) -> tuple[str, dict[str, float]]:
#     """Try local GoEmotions model; fallback to keyword heuristic when unavailable."""
#     if USE_LOCAL_TEXT_MODEL and text_tokenizer and text_model:
#         inputs = text_tokenizer(text, return_tensors="pt", truncation=True)
#         with torch.no_grad():
#             logits = text_model(**inputs).logits[0]
#         probs = torch.softmax(logits, dim=0).tolist()
#         scores = {
#             TEXT_MODEL_LABELS[i]: round(float(probs[i]), 4)
#             for i in range(len(TEXT_MODEL_LABELS))
#         }
#         top_emotion = max(scores, key=scores.get)
#         return top_emotion, scores

#     lowered = text.lower()
#     raw_scores = {}
#     for emotion, keywords in TEXT_EMOTION_KEYWORDS.items():
#         score = sum(lowered.count(keyword) for keyword in keywords)
#         raw_scores[emotion] = float(score)
#     total = sum(raw_scores.values())
#     if total == 0:
#         return DEFAULT_TEXT_EMOTION, {DEFAULT_TEXT_EMOTION: 1.0}
#     normalized = {
#         emotion: round(score / total, 4)
#         for emotion, score in raw_scores.items()
#         if score > 0
#     }
#     top = max(normalized, key=normalized.get)
#     return top, normalized


# # ──────────────────────────────
# # Routes
# # ──────────────────────────────

# @app.get("/", response_class=HTMLResponse)
# @app.get("/analyze/", response_class=HTMLResponse)
# async def home(request: Request):
#     recommendations = []
#     if len(text_results_history) >= 2:
#         anchor = text_results_history[0]
#         sims = [
#             (emotion_similarity(anchor["scores"], item["scores"]), item)
#             for item in text_results_history[1:]
#         ]
#         sims.sort(reverse=True, key=lambda pair: pair[0])
#         recommendations = [item for _, item in sims[:4]]

#     return templates.TemplateResponse(
#         "index.html",
#         {
#             "request": request,
#             "history_music": results_history,
#             "history_text": text_results_history,
#             "recommendations": recommendations,
#         },
#     )


# @app.post("/analyze/")
# async def analyze_audio(file: UploadFile = File(...)):
#     file_path = UPLOAD_DIR / file.filename
#     wav_path = None
#     try:
#         with open(file_path, "wb") as destination:
#             destination.write(await file.read())

#         wav_path = convert_to_wav_48k(str(file_path))
#         audio_data, sr = sf.read(wav_path)
#         if audio_data.ndim > 1:
#             audio_data = np.mean(audio_data, axis=1)

#         inputs = clap_processor(audio=[audio_data], sampling_rate=sr, return_tensors="pt")
#         with torch.no_grad():
#             audio_emb = clap_model.get_audio_features(**inputs)
#             text_inputs = clap_processor(text=AUDIO_EMOTIONS, return_tensors="pt")
#             text_emb = clap_model.get_text_features(**text_inputs)

#         audio_norm = torch.nn.functional.normalize(audio_emb, p=2, dim=-1)
#         text_norm = torch.nn.functional.normalize(text_emb, p=2, dim=-1)
#         sims = torch.matmul(audio_norm, text_norm.T).squeeze(0)

#         idx = sims.argmax().item()
#         top_emotion = AUDIO_EMOTIONS[idx]
#         scores = {AUDIO_EMOTIONS[i]: float(sims[i]) for i in range(len(AUDIO_EMOTIONS))}

#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         results_history.insert(0, {
#             "filename": file.filename,
#             "emotion": top_emotion,
#             "scores": scores,
#             "timestamp": timestamp,
#         })

#         return {
#             "emotion": top_emotion,
#             "scores": scores,
#             "timestamp": timestamp,
#             "filename": file.filename,
#         }

#     except Exception as exc:
#         return {"error": str(exc)}

#     finally:
#         for path in (file_path, wav_path):
#             if path and os.path.exists(path):
#                 try:
#                     os.remove(path)
#                 except OSError:
#                     pass


# @app.post("/analyze_text/")
# async def analyze_text(file: UploadFile = File(...)):
#     try:
#         content = (await file.read()).decode("utf-8", errors="replace")
#         top_emotion, scores = classify_text_emotions(content)

#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         record = {
#             "filename": file.filename,
#             "emotion": top_emotion,
#             "scores": scores,
#             "timestamp": timestamp,
#         }

#         text_results_history.insert(0, record)
#         return record

#     except Exception as exc:
#         return {"error": str(exc)}


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
