import cv2
import os
import torch
from moviepy import VideoFileClip
import whisper
from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np
import easyocr

class VideoIndexer:
    def __init__(self):
        # Load models lazily to save memory on init
        self.clip_model = None
        self.whisper_model = None
        self.ocr_reader = None

    def load_models(self):
        if not self.clip_model:
            print("Loading CLIP model...")
            self.clip_model = SentenceTransformer('clip-ViT-B-32')
        if not self.whisper_model:
            print("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
        if not self.ocr_reader:
            print("Loading EasyOCR reader...")
            self.ocr_reader = easyocr.Reader(['en', 'fr'])

    def process_video(self, video_path: str):
        """
        Runs the full indexing pipeline on a video.
        """
        self.load_models()
        
        # 1. Extract Audio & Transcribe
        audio_path = f"{video_path}.mp3"
        video = VideoFileClip(video_path)
        
        transcription_segments = []
        if video.audio is not None:
            try:
                video.audio.write_audiofile(audio_path, logger=None)
                print("Transcribing audio...")
                transcription = self.whisper_model.transcribe(audio_path, verbose=False)
                transcription_segments = transcription.get('segments', [])
            finally:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
        else:
            print("Aucune piste audio trouvée dans la vidéo.")
        
        # 2. Sample Frames for Visual and OCR
        # We sample one frame every 2 seconds for efficiency
        print("Analyzing frames...")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Erreur: Impossible d'ouvrir la vidéo {video_path}")
            return {"transcription": transcription_segments, "visual_indices": []}

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30.0 # Valeur par défaut
        frame_interval = max(1, int(fps * 2))
        
        frame_results = []
        count = 0
        
        # Create a directory for thumbnails
        thumbnails_dir = "thumbnails"
        os.makedirs(thumbnails_dir, exist_ok=True)
        import uuid
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if count % frame_interval == 0:
                timestamp = count / fps
                
                # Save Frame Image
                frame_filename = f"{thumbnails_dir}/frame_{uuid.uuid4().hex[:8]}.jpg"
                cv2.imwrite(frame_filename, frame)
                
                # Visual Embedding (CLIP)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_frame)
                embedding = self.clip_model.encode(pil_img)
                
                # OCR (Text Detection)
                ocr_results = self.ocr_reader.readtext(frame)
                ocr_text = " ".join([res[1] for res in ocr_results])
                
                # Store results
                frame_results.append({
                    "timestamp": timestamp,
                    "visual_embedding": embedding.tolist(),
                    "ocr_text": ocr_text,
                    "thumbnail_path": frame_filename
                })
                
            count += 1
        cap.release()
        
        return {
            "transcription": transcription_segments,
            "visual_indices": frame_results
        }

# Example usage (commented out for API integration)
# indexer = VideoIndexer()
# data = indexer.process_video("path/to/video.mp4")
