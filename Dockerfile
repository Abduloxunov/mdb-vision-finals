# CarDoctor on Hugging Face Spaces (Docker SDK). CPU inference.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    CARDOCTOR_KB_RUNTIME=/app/kb/.runtime CARDOCTOR_CHECKPOINT=/app/weights/checkpoint_best_ema.pth \
    HF_HOME=/app/kb/.runtime/cache/huggingface
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements-app-local.txt ./
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch==2.14.0 torchvision==0.29.0 \
 && grep -v '^torch' requirements-app-local.txt > /tmp/req.txt && pip install -r /tmp/req.txt
COPY . .
# Build the pinned E5 model + Qdrant index at image build time; keyword retrieval is the fallback if this fails.
RUN (cd kb && python -B setup_vector.py && python -B vector_store.py ingest) || echo "Vector index not built; keyword retrieval will be used."
RUN mkdir -p /app/weights && useradd -m -u 1000 user && chown -R user /app
USER user
EXPOSE 7860
CMD ["python", "-B", "deploy/start_space.py"]
