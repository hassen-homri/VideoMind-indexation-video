import whisper
print("Loading Whisper...")
model = whisper.load_model("base")
print("Whisper loaded.")
from sentence_transformers import SentenceTransformer
print("Loading CLIP...")
model = SentenceTransformer('clip-ViT-B-32')
print("CLIP loaded.")
