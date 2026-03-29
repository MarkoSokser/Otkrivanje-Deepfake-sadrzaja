from fastapi import FastAPI, UploadFile, File
import shutil

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Deepfake Detector API"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    file_location = f"temp/{file.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # TODO: model inference
    result = {
        "prediction": "fake",
        "confidence": 0.87
    }

    return result