# Deployment Guide for Visual Similarity Search

## 1. Backend Deployment (Render.com)

1.  **Sign up/Log in** to [Render.com](https://dashboard.render.com).
2.  **New Web Service**:
    *   Click **New +** -> **Web Service**.
    *   Connect your GitHub repository.
    *   Give it a name (e.g., `visual-search-backend`).
    *   **Runtime**: Python 3.
    *   **Build Command**: `pip install -r backend/requirements.txt`
    *   **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
    *   *Note: If Render detects `render.yaml`, it might auto-configure this.*
3.  **Environment Variables**:
    *   Scroll down to the **Environment** section (or go to the "Environment" tab after creation).
    *   Add the following keys:
        *   `SERPAPI_KEY`: Paste your actual SerpApi key.
        *   `IMGBB_API_KEY`: Paste your actual ImgBB key.
        *   `PYTHON_VERSION`: `3.9.0` (Recommended)

    **👉 Direct Link to Dashboard**: [Render Dashboard](https://dashboard.render.com)
    *(Navigate to your specific service -> Environment to add keys)*

4.  **Deploy**: Click **Create Web Service**. Wait for it to show "Live".
5.  **Copy URL**: Once live, copy the backend URL (e.g., `https://visual-search-backend.onrender.com`).

## 2. Frontend Deployment (Vercel)

1.  **Sign up/Log in** to [Vercel.com](https://vercel.com).
2.  **Import Project**:
    *   Import the same GitHub repository.
    *   **Root Directory**: Click "Edit" and select `frontend`.
    *   **Framework Preset**: Vite (should be auto-detected).
3.  **Environment Variables**:
    *   Find the **Environment Variables** section.
    *   Name: `VITE_API_URL`
    *   Value: Paste your **Render Backend URL** (NOT the dashboard link, the actual app URL, e.g., `https://visual-search-backend.onrender.com`).
4.  **Deploy**: Click **Deploy**.

## 3. Verify
*   Open your new Vercel URL.
*   Upload an image.
*   The frontend (Vercel) will talk to the backend (Render), which will talk to SerpApi/ImgBB.
