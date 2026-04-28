# VideoMind AI - Moteur de Recherche Vidéo Sémantique 🎬🧠

VideoMind est un puissant moteur de recherche vidéo basé sur l'intelligence artificielle. Il permet d'analyser une vidéo et d'y effectuer des recherches complexes par le texte, l'audio et même l'image (recherche sémantique).

## Fonctionnalités Principales ✨
- **Recherche Visuelle (CLIP) :** Retrouvez des moments de la vidéo simplement en décrivant ce qui se passe à l'écran (ex: "une voiture rouge", "quelqu'un qui sourit"), sans même que les mots n'aient été prononcés !
- **Transcription Audio (Whisper) :** Retrouvez n'importe quelle phrase prononcée dans la vidéo.
- **Détection de Texte (EasyOCR) :** Le moteur lit les textes affichés sur l'écran (panneaux, sous-titres incrustés, présentations) et permet de les rechercher.
- **Interface Web Interactive :** Une interface utilisateur moderne et réactive pour effectuer vos recherches et voir les résultats s'afficher instantanément avec les extraits d'images correspondants.

## Technologies Utilisées 🛠️
- **Backend :** Python, FastAPI, Uvicorn
- **Modèles d'IA :** 
  - `SentenceTransformers` (CLIP) pour la compréhension visuelle.
  - `OpenAI Whisper` pour la transcription audio.
  - `EasyOCR` pour la reconnaissance de texte sur les images.
  - `OpenCV` pour l'extraction des séquences vidéo.
- **Frontend :** HTML, CSS Vanilla, JavaScript.

## Comment l'installer et le lancer 🚀

### 1. Prérequis
- Python 3.9+ installé
- FFmpeg installé sur le système (requis pour le traitement vidéo)

### 2. Installation des dépendances
Ouvrez un terminal et installez les paquets requis :
```bash
pip install -r backend/requirements.txt
```

### 3. Configuration de la vidéo
Dans le fichier `backend/main.py`, modifiez la variable `TARGET_VIDEO_PATH` pour qu'elle pointe vers votre propre vidéo :
```python
TARGET_VIDEO_PATH = "chemin/vers/votre/video.mp4"
```

### 4. Lancement du Serveur Backend
```bash
python backend/main.py
```
*(Le premier lancement peut prendre du temps car l'application va télécharger les modèles d'IA nécessaires).*

### 5. Lancement de l'Interface Web
Une fois le serveur lancé, ouvrez simplement le fichier `index.html` dans votre navigateur web, cliquez sur **Initialize**, et commencez vos recherches !

---
*Projet développé avec passion.*
