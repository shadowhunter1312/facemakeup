from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import mediapipe as mp
from io import BytesIO

app = FastAPI()

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True)

def apply_lipstick(image, color_hex, style):
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    if not results.multi_face_landmarks:
        return image

    r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
    overlay = image.copy()

    for face_landmarks in results.multi_face_landmarks:
        lips_indices = list(mp_face_mesh.FACEMESH_LIPS)
        points = [face_landmarks.landmark[i[0]] for i in lips_indices] + [face_landmarks.landmark[i[1]] for i in lips_indices]
        h, w, _ = image.shape
        pts = np.array([[int(p.x * w), int(p.y * h)] for p in points], np.int32)

        if style == "matte":
            cv2.fillPoly(overlay, [pts], (b, g, r))
        else:
            cv2.fillPoly(overlay, [pts], (b, g, r))
            overlay = cv2.addWeighted(image, 0.7, overlay, 0.3, 0)

    return overlay

@app.post("/process")
async def process_image(image: UploadFile = File(...), color: str = Form(...), style: str = Form(...)):
    img_bytes = await image.read()
    np_img = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    processed_img = apply_lipstick(img, color, style)
    _, buffer = cv2.imencode(".jpg", processed_img)
    return StreamingResponse(BytesIO(buffer.tobytes()), media_type="image/jpeg")
