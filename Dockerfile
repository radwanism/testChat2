FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create the uploads directory
RUN mkdir -p uploads

# Expose ports
EXPOSE 8000
EXPOSE 7860

# Create a startup script
RUN echo '#!/bin/bash\n\
if [ "$1" = "api" ]; then\n\
  uvicorn app.main:app --host 0.0.0.0 --port 8000\n\
elif [ "$1" = "gradio" ]; then\n\
  python app.py\n\
else\n\
  python -c "import subprocess; \
  api = subprocess.Popen([\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]); \
  gradio = subprocess.Popen([\"python\", \"app.py\"]); \
  api.wait(); \
  gradio.wait()"\n\
fi' > /app/start.sh

RUN chmod +x /app/start.sh

# Set the entrypoint
ENTRYPOINT ["/app/start.sh"]

# Default command (run both API and Gradio)
#CMD ["both"]
CMD ["python", "app.py"]
