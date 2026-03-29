# Deepfake Detector

A full-stack web application for detecting deepfake content in images and videos using AI models.

---

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

---

## Requirements

* Python 3.10+
* Node.js 18+
* npm

---

## Backend Setup

### 1. Navigate to backend

```bash
cd backend
```

### 2. Create virtual environment

#### Linux (Fedora, Ubuntu, etc.)

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Install PyTorch (CPU version - recommended)

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

---

### 5. Run backend server

```bash
uvicorn app.main:app --reload
```

API documentation:
http://127.0.0.1:8000/docs

---

## Frontend Setup

```bash
cd frontend
npm install
npx ng serve
```

Open in browser:
http://localhost:4200

---

## Notes for Team Development

* Always use a virtual environment
* Do NOT commit `venv/` or `node_modules/`
* Use the same Python version (recommended: 3.10 or 3.11)
* Backend runs on port 8000
* Frontend runs on port 4200

---

## Git Workflow

```bash
git add .
git commit -m "your message"
git push
```
