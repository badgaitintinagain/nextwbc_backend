from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from huggingface_hub import hf_hub_download
from PIL import Image
import io
import numpy as np
import base64
import os
from typing import List
import psutil

app = FastAPI()

# CORS configuration to allow requests from your Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development URL
        "https://nextwbc-assembly.vercel.app",  # Production URL on Vercel
        os.getenv("FRONTEND_URL", "https://nextwbc-assembly.vercel.app")  # Environment variable
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

def print_ram_usage(context=""):
    process = psutil.Process(os.getpid())
    print(f"[RAM LOG] {context} RAM used (MB):", process.memory_info().rss / 1024 / 1024)

# Load YOLO model from local file for Lambda
model = YOLO("cv334.pt")
print_ram_usage("After loading YOLO model")

@app.get("/")
async def root():
    return {"message": "NextWBC API is running with Hugging Face model"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict/")
async def predict_image(file: UploadFile = File(...)):
    print_ram_usage("Before reading image")
    # Read and process the image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    print_ram_usage("After loading image")
    
    # Run inference
    results = model(image)
    print_ram_usage("After inference")
    
    # Process results
    result = results[0]
    
    # Get detected objects, bounding boxes, and confidence scores
    boxes = result.boxes.xyxy.tolist()  # x1, y1, x2, y2
    confidences = result.boxes.conf.tolist()
    class_ids = result.boxes.cls.tolist()
    class_names = [result.names[int(class_id)] for class_id in class_ids]
    
    # Get output image with annotations
    output_image = results[0].plot()
    output_image_pil = Image.fromarray(output_image)
    buffered = io.BytesIO()
    output_image_pil.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return {
        "filename": file.filename,
        "detections": [
            {
                "class": class_name,
                "confidence": confidence,
                "box": box
            }
            for class_name, confidence, box in zip(class_names, confidences, boxes)
        ],
        "annotated_image": f"data:image/jpeg;base64,{img_str}"
    }

# For batch processing if needed
@app.post("/predict-batch/")
async def predict_batch(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        prediction = model(image)
        # Process results similarly as above
        # Add to results
    return results

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)