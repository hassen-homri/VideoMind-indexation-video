# 🎬 VideoMind AI: Multimodal Video Search Engine
VideoMind is an advanced AI-powered video indexing and search platform. It allows users to perform complex semantic searches within a video, retrieving moments based on **what is seen**, **what is said**, and **what is written** on the screen.
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green.svg)
![AI Models](https://img.shields.io/badge/Models-CLIP%20%7C%20Whisper%20%7C%20EasyOCR-orange.svg)
## ✨ Key Features
-   **🔍 Visual Semantic Search (CLIP):** Find moments by describing visual actions or objects (e.g., "a red car racing", "someone smiling") using natural language, even if those words are never spoken.
-   **🎙️ Audio Transcription (Whisper):** Search through every word spoken in the video with high-accuracy timestamped results.
-   **📝 On-Screen Text Detection (EasyOCR):** Automatically index and search for text appearing in the video (slides, signs, subtitles, etc.).
-   **💻 Modern Web Interface:** A responsive, sleek UI to browse search results with instant video thumbnails and direct timestamps.
## 🏗️ Architecture
```mermaid
graph TD
    A[Video File] --> B[Indexing Pipeline]
    B --> C[Whisper AI: Audio Transcription]
    B --> D[CLIP: Visual Embeddings]
    B --> E[EasyOCR: Text Recognition]
    C & D & E --> F[Local Vector Index]
    G[User Query] --> H[FastAPI Backend]
    H --> I[Cosine Similarity Search]
    I --> F
    I --> J[JSON Results]
    J --> K[Frontend Interface]
