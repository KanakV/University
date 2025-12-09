# import os
# import uvicorn
# import tempfile
# import subprocess
# from datetime import datetime
# from pathlib import Path
# from fastapi import FastAPI, File, UploadFile, Request
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from transformers import pipeline

# # --- Initialize app and folders ---
# app = FastAPI(title="Audio Emotion Recognition Web App")
# app.mount("/static", StaticFiles(directory="static"), name="static")
# BASE_DIR = Path(__file__).resolve().parent
# TEMPLATES_DIR = BASE_DIR / "templates"
# templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# os.makedirs("uploads", exist_ok=True)
# os.makedirs("templates", exist_ok=True)
# os.makedirs("static", exist_ok=True)

# # --- Load the model ---
# print("Loading emotion recognition model...")
# emotion_classifier = pipeline(
#     task="audio-classification",
#     model="BilalHasan/distilhubert-finetuned-ravdess"
# )
# print("Model loaded successfully.")

# # --- In-memory history of predictions ---
# results_history = []

# # --- Helper: convert to 16kHz mono wav ---
# def convert_to_wav_16k(input_path):
#     output_path = tempfile.mktemp(suffix=".wav")
#     result = subprocess.run([
#         "ffmpeg", "-y", "-i", input_path,
#         "-ar", "16000", "-ac", "1", output_path
#     ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    
#     if result.returncode != 0:
#         raise RuntimeError(f"FFmpeg conversion failed with return code {result.returncode}")
    
#     if not os.path.exists(output_path):
#         raise RuntimeError("FFmpeg conversion failed: output file was not created")
    
#     return output_path

# # --- Routes ---

# @app.get("/", response_class=HTMLResponse)
# @app.get("/analyze/", response_class=HTMLResponse)
# async def home(request: Request):
#     return templates.TemplateResponse(
#         name="index.html",
#         context={"request": request, "history": results_history}
#     )




# @app.post("/analyze/")
# async def analyze(file: UploadFile = File(...)):
#     file_path = None
#     wav_path = None
#     try:
#         # Save upload
#         file_path = os.path.join("uploads", file.filename)
#         with open(file_path, "wb") as f:
#             f.write(await file.read())

#         # Convert and classify
#         wav_path = convert_to_wav_16k(file_path)
#         results = emotion_classifier(wav_path)

#         # Record result
#         top_emotion = results[0]["label"]
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         results_history.insert(0, {
#             "filename": file.filename,
#             "emotion": top_emotion,
#             "details": results,
#             "timestamp": timestamp
#         })

#         return JSONResponse(content={"results": results, "emotion": top_emotion, "timestamp": timestamp})

#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)
#     finally:
#         # Cleanup temporary files
#         if wav_path and os.path.exists(wav_path):
#             try:
#                 os.remove(wav_path)
#             except Exception:
#                 pass
#         if file_path and os.path.exists(file_path):
#             try:
#                 os.remove(file_path)
#             except Exception:
#                 pass

# # --- Run app ---
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

import os
import uvicorn
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from transformers import ClapProcessor, ClapModel
import torch
import soundfile as sf
import numpy as np

# --- Initialize app and folders ---
app = FastAPI(title="Music Emotion Classification Web App")
app.mount("/static", StaticFiles(directory="static"), name="static")
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
# Ensure templates update without server restart during development
try:
    templates.env.auto_reload = True
    templates.env.cache = {}
except Exception:
    pass

os.makedirs("uploads", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# --- Load CLAP model ---
print("Loading CLAP music emotion model...")
processor = ClapProcessor.from_pretrained("laion/clap-htsat-unfused")
model = ClapModel.from_pretrained("laion/clap-htsat-unfused")
model.eval()  # Set to evaluation mode
print("Model loaded successfully.")

# --- Define emotions ---
EMOTIONS = ["happy", "sad", "energetic", "calm", "romantic", "angry", "relaxed"]

# --- In-memory history ---
results_history = []

# --- Helper: convert to 48kHz mono wav (CLAP model requirement) ---
def convert_to_wav_48k(input_path):
    output_path = tempfile.mktemp(suffix=".wav")
    result = subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-ar", "48000", "-ac", "1", output_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    if result.returncode != 0 or not os.path.exists(output_path):
        raise RuntimeError("FFmpeg conversion failed.")
    return output_path


# --- Routes ---
@app.get("/", response_class=HTMLResponse)
@app.get("/analyze/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        name="index.html",
        context={"request": request, "history": results_history}
    )


@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    file_path = None
    wav_path = None
    try:
        # Save upload
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Convert audio
        wav_path = convert_to_wav_48k(file_path)
        # Load audio using soundfile (avoids torchcodec requirement)
        audio_data, sr = sf.read(wav_path)
        
        # Ensure mono audio (convert stereo to mono by averaging)
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        # CLAP processor expects audio as a list/array with sampling rate
        # Compute embeddings
        inputs = processor(audio=[audio_data], sampling_rate=sr, return_tensors="pt", padding=True)
        with torch.no_grad():
            audio_emb = model.get_audio_features(**inputs)

        # Compute text embeddings
        text_inputs = processor(text=EMOTIONS, return_tensors="pt", padding=True)
        with torch.no_grad():
            text_emb = model.get_text_features(**text_inputs)

        # Compute cosine similarity between audio and each text embedding
        # audio_emb: [1, embedding_dim], text_emb: [num_emotions, embedding_dim]
        # Normalize embeddings for cosine similarity
        audio_emb_norm = torch.nn.functional.normalize(audio_emb, p=2, dim=-1)
        text_emb_norm = torch.nn.functional.normalize(text_emb, p=2, dim=-1)
        # Compute dot product (cosine similarity after normalization)
        similarities = torch.matmul(audio_emb_norm, text_emb_norm.T).squeeze(0)
        
        top_idx = similarities.argmax().item()
        top_emotion = EMOTIONS[top_idx]
        scores = {EMOTIONS[i]: round(float(similarities[i]), 4) for i in range(len(EMOTIONS))}

        # Record result
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results_history.insert(0, {
            "filename": file.filename,
            "emotion": top_emotion,
            "scores": scores,
            "timestamp": timestamp
        })

        return JSONResponse(content={
            "emotion": top_emotion,
            "scores": scores,
            "timestamp": timestamp
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        # Cleanup
        for path in [wav_path, file_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass


# --- Run app ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
