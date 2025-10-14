# ==============================
# STEP 1: Use a compatible Python image
# ==============================
FROM python:3.11-slim

# ==============================
# STEP 2: Set working directory
# ==============================
WORKDIR /app

# ==============================
# STEP 3: Copy requirements and install them
# ==============================
COPY requirements.txt .
RUN apt-get update && apt-get install -y poppler-utils libgl1 && \
    pip install --no-cache-dir -r requirements.txt

# ==============================
# STEP 4: Copy all your project files
# ==============================
COPY . .

# ==============================
# STEP 5: Expose the port Google Cloud Run expects
# ==============================
EXPOSE 8080

# ==============================
# STEP 6: Start your Flask app with Gunicorn
# ==============================
CMD ["gunicorn", "-b", ":8080", "app:app"]
