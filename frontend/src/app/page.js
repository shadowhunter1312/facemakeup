"use client";
import { useEffect, useRef, useState } from "react";
import * as faceMesh from "@mediapipe/face_mesh";
import { Camera } from "@mediapipe/camera_utils";

export default function Home() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [color, setColor] = useState("#d10061");
  const [style, setStyle] = useState("glossy");
  const [faceMeshInstance, setFaceMeshInstance] = useState(null);
  
  useEffect(() => {
    // Initialize the MediaPipe FaceMesh model
    const faceMeshModel = new faceMesh.FaceMesh({
      locateLandmarks: true,
      maxNumFaces: 1,
    });
    setFaceMeshInstance(faceMeshModel);

    // Set up camera stream and detection
    const startCamera = async () => {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
        audio: false,
      });
      videoRef.current.srcObject = stream;
      videoRef.current.play();

      // Set up the faceMesh model to process frames
      faceMeshModel.onResults(onResults);

      // Create the camera object and start streaming
      const camera = new Camera(videoRef.current, {
        onFrame: async () => {
          await faceMeshModel.send({ image: videoRef.current });
        },
        width: 640,
        height: 480,
      });
      camera.start();
    };

    startCamera();

    // Callback to handle results from FaceMesh
    function onResults(results) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, 640, 480); // Clear previous frame
      ctx.drawImage(videoRef.current, 0, 0, 640, 480); // Draw video frame

      if (!results.multiFaceLandmarks) return;

      const faceLandmarks = results.multiFaceLandmarks[0];
      const lipIndices = [
        78, 95, 88, 87, 84, 13, 312, 317, 316, 14, 78
      ];

      const lipPoints = lipIndices.map(idx => {
        const x = faceLandmarks[idx].x * 640;
        const y = faceLandmarks[idx].y * 480;
        return [x, y];
      });

      // Draw lipstick on lips
      ctx.fillStyle = color; // Apply chosen color
      ctx.beginPath();
      ctx.moveTo(lipPoints[0][0], lipPoints[0][1]);
      lipPoints.forEach(point => {
        ctx.lineTo(point[0], point[1]);
      });
      ctx.closePath();
      ctx.fill();

      // Apply glossy or matte effect (simple example of effect)
      if (style === "glossy") {
        ctx.globalAlpha = 0.6; // Glossy effect by transparency
        ctx.fillStyle = "#ffffff"; // Glossy white color over the lips
        ctx.fill();
      }
      ctx.globalAlpha = 1.0; // Reset alpha for other drawing
    }
  }, [color, style]);

  return (
    <div className="flex flex-col items-center gap-4 p-4">
      <video ref={videoRef} width={640} height={480} className="rounded-xl" />
      <canvas ref={canvasRef} width={640} height={480} hidden></canvas>
      <div className="flex gap-2">
        <input
          type="color"
          value={color}
          onChange={e => setColor(e.target.value)}
        />
        <select onChange={e => setStyle(e.target.value)} value={style}>
          <option value="glossy">Glossy</option>
          <option value="matte">Matte</option>
        </select>
      </div>
    </div>
  );
}
