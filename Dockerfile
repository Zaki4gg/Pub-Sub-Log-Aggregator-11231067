FROM python:3.11-slim

WORKDIR /app
ENV PATH="/home/appuser/.local/bin:$PATH"

RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

COPY src/ ./src/

EXPOSE 8080
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
