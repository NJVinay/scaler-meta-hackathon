# TASK 05 — Docker Build & Hugging Face Spaces Deployment

**Source:** `task_requirements/The-Task.md`, [Module 3 — Deploying Environments](https://github.com/raun/openenv-course/blob/main/module-3/README.md)

## Objective
Containerize the environment and deploy it to Hugging Face Spaces, ensuring it responds to `POST /reset` with HTTP 200.

## Steps

1. **Create a `Dockerfile` in the project root**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   EXPOSE 7860
   CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
   ```

2. **Test the Docker build locally**
   ```bash
   docker build -t my-openenv .
   docker run -p 7860:7860 my-openenv
   ```

3. **Verify the container responds to reset**
   ```bash
   curl -X POST http://localhost:7860/reset -H "Content-Type: application/json"
   # Expected: HTTP 200 with valid observation JSON
   ```

4. **Deploy to Hugging Face Spaces**
   ```bash
   openenv push   # or push via HF Space Git remote
   ```
   - Tag the Space with `openenv`
   - Ensure the Space URL returns 200 on `POST /reset`

## Scaling Notes (from GitHub README)
- HF Spaces free tier handles up to **128 concurrent WebSocket sessions**
- Each `step()` call uses WebSocket (`/ws`) — ~0.1ms overhead vs HTTP's ~10–50ms

## Validation (Pre-Validation-Script.txt — Step 1 & 2)
```bash
# Ping live HF Space
curl -s -o /dev/null -w "%{http_code}" -X POST https://your-space.hf.space/reset

# Docker build
docker build ./
```
- HTTP 200 → ✅ Pass
- Build success → ✅ Pass
- Connection failure or non-200 → ❌ Disqualified immediately (stopat Step 1)
