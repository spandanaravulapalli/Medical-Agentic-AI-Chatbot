FROM python:3.10-slim

WORKDIR /app

# Copy only requirements first (layer caching)
COPY requirements.txt .

# Install without cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

EXPOSE 8080
CMD ["python", "app.py"]