# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 7860

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create data directories for persistence (Note: these will be ephemeral in standard Spaces)
RUN mkdir -p data/chroma_db data/memory

# Pre-populate the Knowledge Base (Optional: only if you want it ready on boot)
# RUN python -m rag.embed_kb

# Expose the port FastAPI will run on
EXPOSE 7860

# Command to run the application
# We use 0.0.0.0 to allow external access and 7860 as it's the default HF Space port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
