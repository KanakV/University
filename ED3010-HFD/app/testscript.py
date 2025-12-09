from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL_DIR = 'models/goemotions'

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)

text = "I love this song so much! It makes me feel alive."
inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

with torch.no_grad():
    logits = model(**inputs).logits
    probs = torch.sigmoid(logits).squeeze(0)  # Sigmoid for multi-label probs

TEXT_LABELS = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion",
    "curiosity", "desire", "disappointment", "disapproval", "disgust", "embarrassment",
    "excitement", "fear", "gratitude", "grief", "joy", "love", "nervousness", "optimism",
    "pride", "realization", "relief", "remorse", "sadness", "surprise", "neutral"
]

scores = {label: float(probs[i]) for i, label in enumerate(TEXT_LABELS)}
top_emotion = max(scores, key=scores.get)

print(f"Text: {text}")
print(f"Top Emotion: {top_emotion} ({scores[top_emotion]:.3f})")
print("\nTop 5 scores:")
for label, prob in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {label}: {prob:.3f}")