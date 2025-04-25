"use client"
import { useEffect, useRef, useState } from "react";
import axios from "axios";

export default function Home() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [color, setColor] = useState("#d10061");
  const [style, setStyle] = useState("glossy");

  useEffect(() => {
    const startCamera = async () => {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
        audio: false,
      });
      videoRef.current.srcObject = stream;
      videoRef.current.play();
    };

    startCamera();
  }, []);

  const captureAndSend = async () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(videoRef.current, 0, 0, 640, 480);
    canvas.toBlob(async (blob) => {
      const formData = new FormData();
      formData.append("image", blob, "capture.jpg");
      formData.append("color", color);
      formData.append("style", style);

      const res = await axios.post("https://your-api-url/process", formData, {
        responseType: "blob",
      });
      const output = URL.createObjectURL(res.data);
      const img = new Image();
      img.src = output;
      img.onload = () => {
        ctx.clearRect(0, 0, 640, 480);
        ctx.drawImage(img, 0, 0);
      };
    }, "image/jpeg");
  };

  return (
    <div className="flex flex-col items-center gap-4 p-4">
      <video ref={videoRef} width={640} height={480} className="rounded-xl" />
      <canvas ref={canvasRef} width={640} height={480} hidden></canvas>
      <div className="flex gap-2">
        <input type="color" value={color} onChange={e => setColor(e.target.value)} />
        <select onChange={e => setStyle(e.target.value)} value={style}>
          <option value="glossy">Glossy</option>
          <option value="matte">Matte</option>
        </select>
        <button onClick={captureAndSend} className="bg-pink-500 text-white px-4 py-2 rounded">
          Apply Lipstick
        </button>
      </div>
    </div>
  );
}
