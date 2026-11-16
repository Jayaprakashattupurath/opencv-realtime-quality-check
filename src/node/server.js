import express from "express";
import cors from "cors";
import fs from "fs";
import path from "path";
import os from "os";
import { spawn } from "child_process";

const app = express();
app.use(cors());
app.use(express.json({ limit: "5mb" }));

app.get("/health", (_, res) => res.json({ ok: true }));

app.post("/api/analyze", async (req, res) => {
  try {
    const { imageBase64 } = req.body;
    if (!imageBase64) {
      return res.status(400).json({ ok: false, error: "imageBase64 is required" });
    }

    const clean = imageBase64.replace(/^data:image\/\w+;base64,/, "");
    const buffer = Buffer.from(clean, "base64");

    const tempFile = path.join(os.tmpdir(), `frame-${Date.now()}.jpg`);
    fs.writeFileSync(tempFile, buffer);

    const pyPath = path.resolve("../python/processor.py");
    const py = spawn("python", [pyPath, tempFile]);

    let stdout = "";
    let stderr = "";

    py.stdout.on("data", (d) => (stdout += d.toString()));
    py.stderr.on("data", (d) => (stderr += d.toString()));

    py.on("close", (code) => {
      fs.unlink(tempFile, () => {});
      if (code !== 0) {
        return res.status(500).json({ ok: false, error: stderr || "Python process failed" });
      }

      try {
        const result = JSON.parse(stdout);
        res.json(result);
      } catch {
        res.status(500).json({ ok: false, error: "Invalid processor response" });
      }
    });
  } catch (err) {
    res.status(500).json({ ok: false, error: err.message });
  }
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`API running on http://localhost:${PORT}`);
});