# Backend – Python FastAPI

## Requirements

- Python 3.10+

## Installation

```bash
pip install -r requirements.txt
```

## Running the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

## Project layout

```
app/
├── main.py       # FastAPI application entry point
├── routes/       # API route handlers
├── services/     # Business logic
├── models/       # Pydantic / DB models
└── utils/        # Utility helpers
```
