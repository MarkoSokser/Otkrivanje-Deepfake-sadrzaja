# Backend API Rute

Popis ruta koje backend mora implementirati da bi frontend bio potpuno funkcionalan.

---

## Rute za frontend

### POST `/analyze`
Prima sliku ili videozapis i vraća rezultat deepfake analize.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` — slika (`.jpg`, `.jpeg`, `.png`) ili video (`.mp4`, `.mov`, `.avi`), max 50 MB

**Response `200 OK`:**
```json
{
  "verdict": "REAL",
  "confidence": 87.3,
  "media_type": "image",
  "model_used": "Xception",
  "explanation": "Model nije pronašao znakove manipulacije.",
  "frame_count": 120,
  "suspicious_frames": 34
}
```
> `verdict`: `"REAL"` ili `"DEEPFAKE"`  
> `confidence`: broj od 0 do 100  
> `media_type`: `"image"` ili `"video"`  
> `frame_count`, `suspicious_frames`: opcionalno, samo za videozapise

---

### GET `/health`
Provjera je li backend dostupan.

**Response `200 OK`:**
```json
{
  "status": "ok"
}
```

---

### GET `/models`
Vraća popis AI modela dostupnih za analizu.

**Response `200 OK`:**
```json
{
  "models": ["Xception", "EfficientNet", "MesoNet"]
}
```

---

## Rute specifične za backend

### GET `/`
Potvrda da API radi.

**Response `200 OK`:**
```json
{
  "message": "Deepfake Detector API radi"
}
```

---

### GET `/models/{name}/info`
Detalji o određenom AI modelu.

**Parametri:** `name` — naziv modela (npr. `Xception`)

**Response `200 OK`:**
```json
{
  "name": "Xception",
  "architecture": "CNN",
  "accuracy": 95.7,
  "dataset": "FaceForensics++",
  "description": "Model treniran na FaceForensics++ datasetu."
}
```
