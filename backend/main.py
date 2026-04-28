from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import os
import uuid
import json
from indexer import VideoIndexer
import numpy as np
from sentence_transformers import util
import torch
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("VideoMind is ready (Models will load on first use).")
    yield

app = FastAPI(title="VideoMind API", lifespan=lifespan)
indexer = VideoIndexer()

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the thumbnails directory for the frontend
os.makedirs("thumbnails", exist_ok=True)
app.mount("/thumbnails", StaticFiles(directory="thumbnails"), name="thumbnails")

# Configuration: Specify the video to be indexed
TARGET_VIDEO_PATH = "./videoplayback.mp4" # <--- MANUALLY ENTER YOUR VIDEO PATH OR URL HERE

# Storage for indices (Persistent JSON file)
INDEX_FILE = "index.json"

def load_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r") as f:
            return json.load(f)
    return []

def save_index(index_data):
    with open(INDEX_FILE, "w") as f:
        json.dump(index_data, f)

VIDEO_INDEX = load_index()

@app.get("/")
async def root():
    return {"message": "VideoMind API is running"}

@app.get("/status")
async def get_status():
    is_indexed = any(item["filename"] == TARGET_VIDEO_PATH for item in VIDEO_INDEX)
    return {
        "is_indexed": is_indexed,
        "video_name": TARGET_VIDEO_PATH,
        "status": "ready" if is_indexed else "needs_indexing"
    }

@app.post("/initialize")
async def initialize():
    global VIDEO_INDEX
    if not any(item["filename"] == TARGET_VIDEO_PATH for item in VIDEO_INDEX):
        if os.path.exists(TARGET_VIDEO_PATH):
            print(f"Indexing target video: {TARGET_VIDEO_PATH}...")
            data = indexer.process_video(TARGET_VIDEO_PATH)
            data["filename"] = TARGET_VIDEO_PATH
            VIDEO_INDEX.append(data)
            save_index(VIDEO_INDEX)
            return {"status": "success", "message": "Indexing complete"}
        else:
            return {"status": "error", "message": f"File {TARGET_VIDEO_PATH} not found"}
    return {"status": "already_indexed"}

@app.get("/search")
async def search(query: str):
    if not VIDEO_INDEX:
        return []

    results = []
    # Load CLIP for query embedding
    indexer.load_models()
    query_embedding = indexer.clip_model.encode(query)

    for video in VIDEO_INDEX:
        # Try to find a default thumbnail
        default_thumb = video["visual_indices"][0]["thumbnail_path"] if video["visual_indices"] else ""
        
        # 1. Search in Transcription (Audio)
        for segment in video["transcription"]:
            if query.lower() in segment["text"].lower():
                # Find the closest visual frame for thumbnail
                closest_frame = min(video["visual_indices"], key=lambda f: abs(f["timestamp"] - segment["start"]), default=None)
                thumb = closest_frame["thumbnail_path"] if closest_frame else default_thumb
                
                results.append({
                    "title": video["filename"],
                    "thumbnail": f"http://localhost:8081/{thumb}",
                    "timestamp": f"{int(segment['start'] // 60)}:{int(segment['start'] % 60):02d}",
                    "matchType": "audio",
                    "matchText": segment["text"],
                    "score": 1.0 # Exact text match has highest priority
                })

        # 2. Search in OCR (Text on screen)
        for frame in video["visual_indices"]:
            if query.lower() in frame["ocr_text"].lower():
                thumb = frame.get("thumbnail_path", default_thumb)
                results.append({
                    "title": video["filename"],
                    "thumbnail": f"http://localhost:8081/{thumb}",
                    "timestamp": f"{int(frame['timestamp'] // 60)}:{int(frame['timestamp'] % 60):02d}",
                    "matchType": "ocr",
                    "matchText": f"Detected on screen: '{frame['ocr_text']}'",
                    "score": 1.0 # Exact text match has highest priority
                })

        # 3. Search in Visual (CLIP)
        for frame in video["visual_indices"]:
            # Ensure float32 dtype to match the model's query_embedding dtype
            sim = util.cos_sim(query_embedding, np.array(frame["visual_embedding"], dtype=np.float32)).item()
            if sim > 0.22: # Lowered threshold to retrieve more potential matches
                thumb = frame.get("thumbnail_path", default_thumb)
                results.append({
                    "title": video["filename"],
                    "thumbnail": f"http://localhost:8081/{thumb}",
                    "timestamp": f"{int(frame['timestamp'] // 60)}:{int(frame['timestamp'] % 60):02d}",
                    "matchType": "visual",
                    "matchText": f"Visual match detected with {sim:.2f} confidence.",
                    "score": float(sim)
                })

    # Sort results by score (descending) to show best matches first
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:10] # Return top 10

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
