import React, { useEffect, useRef, useState } from "react";

const API_URL = "http://localhost:4000/api/analyze";

export default function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(true);

  useEffect(() => {
    let stream;
    let timer;

    const init = async () => {
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;

      timer = setInterval(captureAndAnalyze, 2000);
    };

    const captureAndAnalyze = async () => {
      if (!running || !videoRef.current || !canvasRef.current) return;

      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;

      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      const imageBase64 = canvas.toDataURL("image/jpeg", 0.7);

      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ imageBase64 })
      });

      const data = await res.json();
      setResult(data);
    };

    init();

    return () => {
      if (timer) clearInterval(timer);
      if (stream) stream.getTracks().forEach((t) => t.stop());
    };
  }, [running]);

  return (
    <div style={{ fontFamily: "Arial", margin: 20 }}>
      <h2>OpenCV Real-time Image Quality Check</h2>
      <p>Scenario: Ensure incoming camera frames are sharp and well-lit before processing/OCR.</p>

      <video ref={videoRef} autoPlay playsInline width="480" style={{ borderRadius: 8 }} />
      <canvas ref={canvasRef} style={{ display: "none" }} />

      <div style={{ marginTop: 12 }}>
        <button onClick={() => setRunning((v) => !v)}>
          {running ? "Pause Analysis" : "Resume Analysis"}
        </button>
      </div>

      {result && (
        <pre style={{ background: "#f5f5f5", padding: 12, marginTop: 12 }}>
{JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}