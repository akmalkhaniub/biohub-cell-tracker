# 🆓 Free Tier Deployment Guide for Biohub Cell Tracker

Deploy **Biohub Cell Tracker** using **Hugging Face Spaces (16GB RAM Free)**, **Kaggle GPU Kernels**, and **Cloudflare Tunnels**.

---

## 1. Free Cloud GPU Evaluation: Kaggle Kernels
```bash
kaggle kernels push -p deploy/free/
```

---

## 2. Interactive 4D Lineage Visualizer: Hugging Face Spaces
1. Create a Space with Docker SDK at [huggingface.co/spaces](https://huggingface.co/spaces).
2. Push your `Dockerfile`, `src/`, `package.json`, and `README_HF.md`.

---

## 3. Remote Live Visualizer Demo: Cloudflare Tunnel
```powershell
# Windows
.\deploy\free\tunnel.ps1 -Port 3009

# Linux / macOS
./deploy/free/tunnel.sh 3009
```
