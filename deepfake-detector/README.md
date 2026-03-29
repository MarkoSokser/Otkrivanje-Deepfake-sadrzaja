# Deepfake Detector

A full-stack application for detecting deepfake content in images and videos.

## Project Structure

```
deepfake-detector/
│
├── frontend/        # Angular application
├── backend/         # Python FastAPI backend
├── ai_models/       # AI models and inference scripts
├── data/            # Test data (images and videos)
├── docs/            # Documentation
└── docker/          # Docker configuration (optional)
```

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
ng serve
```
