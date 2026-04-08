# ── Base image ──
FROM python:3.11-slim

# ── Non-root user ──
RUN groupadd -r appgroup && useradd -r -g appgroup --no-create-home appuser

WORKDIR /app

# ── Install dependencies (layer caching) ──
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Copy application code ──
COPY --chown=appuser:appgroup . .

# ── Switch to non-root ──
USER appuser

# ── Expose HF Spaces port ──
EXPOSE 7860

# ── Health check ──
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/health')" || exit 1

# ── Run ──
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1", "--timeout-keep-alive", "30"]
