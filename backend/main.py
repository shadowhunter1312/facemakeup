from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import mediapipe as mp

app = FastAPI()

# Allow frontend access (e.g. Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def apply_lipstick(image: np.ndarray, color: str = "red", style: str = "glossy") -> np.ndarray:
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True)

    results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if not results.multi_face_landmarks:
        return image

    face_landmarks = results.multi_face_landmarks[0]
    lip_indices = list(set(mp_face_mesh.FACEMESH_LIPS))

    h, w, _ = image.shape
    lip_points = []

    for connection in lip_indices:
        for idx in connection:
            x = int(face_landmarks.landmark[idx].x * w)
            y = int(face_landmarks.landmark[idx].y * h)
            lip_points.append([x, y])

    if not lip_points:
        return image

    lip_points = np.array(lip_points)
    mask = np.zeros_like(image)
    
    # Convert color string to BGR
    color_map = {
        "red": (0, 0, 255),
        "pink": (203, 192, 255),
        "nude": (180, 160, 130),
        "purple": (150, 50, 180),
    }
    lip_color = color_map.get(color.lower(), (0, 0, 255))

    cv2.fillPoly(mask, [lip_points], lip_color)

    if style == "matte":
        output = cv2.addWeighted(image, 1.0, mask, 0.4, 0)
    else:  # glossy
        blur = cv2.GaussianBlur(mask, (7, 7), 10)
        output = cv2.addWeighted(image, 1.0, blur, 0.6, 0)

    return output

@app.post("/process")
async def process(file: UploadFile = File(...), color: str = "red", style: str = "glossy"):
    contents = await file.read()
    img_np = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

    if image is None:
        return {"error": "Invalid image"}

    result = apply_lipstick(image, color, style)
    _, encoded_img = cv2.imencode('.jpg', result)
    return Response(content=encoded_img.tobytes(), media_type="image/jpeg")

@app.get("/")
def health():
    return {"status": "ok", "message": "Face Makeup API running"}

# For local run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
