FROM python:3.11-slim

WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package files and install Node deps
COPY package*.json ./
RUN npm install

# Copy all source files
COPY . .

# Build frontend
RUN npm run build

# Create data directory
RUN mkdir -p data

# Expose port
ENV PORT=8080
EXPOSE 8080

# Start backend with uvicorn
CMD python -m uvicorn backend:app --host 0.0.0.0 --port ${PORT}