# ══════════════════════════════════════════════════════════════════════════════
#  KenexAI  │  E-Commerce Churn Prediction System
#  Multi-stage Docker build — lightweight production image
# ══════════════════════════════════════════════════════════════════════════════

FROM python:3.11-slim AS base

# Metadata
LABEL maintainer="KenexAI Team"
LABEL description="E-Commerce Churn Prediction & Retention System"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ── System dependencies ──────────────────────────────────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ──────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application code ─────────────────────────────────────────────────────────
COPY . .

# ── Create necessary directories ─────────────────────────────────────────────
RUN mkdir -p \
    data/raw data/processed data/synthetic \
    warehouse/bronze warehouse/silver warehouse/gold \
    models/saved \
    genai/outputs

# ── Expose Streamlit port ─────────────────────────────────────────────────────
EXPOSE 8501

# ── Health check ──────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# ── Default command: Run the Streamlit dashboard ──────────────────────────────
CMD ["streamlit", "run", "dashboard/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--theme.base=dark"]
