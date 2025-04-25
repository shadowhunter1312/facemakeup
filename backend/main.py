from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
import numpy as np
from utils.makeup import apply_lipstick  # your makeup logic

app = FastAPI()

# CORS setup (required if frontend is on Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend domain
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process")
async def process_image(file: UploadFile = File(...), color: str = "red", style: str = "glossy"):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    processed = apply_lipstick(image, color, style)
    _, buffer = cv2.imencode('.jpg', processed)
    return Response(content=buffer.tobytes(), media_type="image/jpeg")

# Railway will use this entry if run locally
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
