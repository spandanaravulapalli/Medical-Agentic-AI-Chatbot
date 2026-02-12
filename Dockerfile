FROM python:3.10-slim

WORKDIR /app

# Copy only requirements first (layer caching)
COPY . /app

# Install without cache
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]